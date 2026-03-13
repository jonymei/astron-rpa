import asyncio
import base64
import hashlib
import hmac
import json
import random
import string
import time
from datetime import datetime
from io import BytesIO
from time import mktime
from urllib.parse import quote, urlencode
from wsgiref.handlers import format_date_time

import httpx
import websockets
from mutagen import File as MutagenFile

from app.config import get_settings


class SpeechError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def decode_audio_base64(audio_base64: str) -> bytes:
    try:
        return base64.b64decode(audio_base64)
    except Exception as exc:
        raise SpeechError("Invalid audio_base64 payload.") from exc


def get_audio_duration_seconds(audio_bytes: bytes, filename: str) -> float:
    audio = MutagenFile(BytesIO(audio_bytes), filename=filename)
    duration = getattr(getattr(audio, "info", None), "length", None)
    if duration is None or duration <= 0:
        raise SpeechError("Unable to determine audio duration.")
    return float(duration)


def _raasr_signa(app_id: str, api_secret: str) -> tuple[str, str]:
    ts = str(int(time.time()))
    md5 = hashlib.md5(f"{app_id}{ts}".encode("utf-8")).hexdigest().encode("utf-8")
    signa = base64.b64encode(hmac.new(api_secret.encode("utf-8"), md5, hashlib.sha1).digest()).decode("utf-8")
    return ts, signa


async def submit_raasr_job(audio_bytes: bytes, filename: str, duration_seconds: float, language: str) -> tuple[str, int]:
    settings = get_settings()
    ts, signa = _raasr_signa(settings.XFYUN_APP_ID, settings.XFYUN_API_SECRET)
    params = {
        "appId": settings.XFYUN_APP_ID,
        "ts": ts,
        "signa": signa,
        "fileName": filename,
        "fileSize": str(len(audio_bytes)),
        "duration": str(max(1, int(duration_seconds))),
        "language": language,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://raasr.xfyun.cn/v2/api/upload",
            params=params,
            content=audio_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )
        response.raise_for_status()
        payload = response.json()
    if payload.get("code") != "000000":
        raise SpeechError(payload.get("descInfo", "XFYun ASR upload failed."))
    content = payload.get("content") or {}
    return content["orderId"], int(content.get("taskEstimateTime", 0))


async def poll_raasr_result(order_id: str, result_type: str = "transfer") -> dict:
    settings = get_settings()
    deadline = time.monotonic() + settings.XFYUN_SPEECH_POLL_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        ts, signa = _raasr_signa(settings.XFYUN_APP_ID, settings.XFYUN_API_SECRET)
        params = {
            "appId": settings.XFYUN_APP_ID,
            "ts": ts,
            "signa": signa,
            "orderId": order_id,
            "resultType": result_type,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post("https://raasr.xfyun.cn/v2/api/getResult", params=params)
            response.raise_for_status()
            payload = response.json()
        if payload.get("code") != "000000":
            raise SpeechError(payload.get("descInfo", "XFYun ASR query failed."))

        content = payload.get("content") or {}
        order_info = content.get("orderInfo") or {}
        status = order_info.get("status")
        if status == 4:
            return content
        if order_info.get("failType", 0):
            raise SpeechError(f"XFYun transcription failed with failType={order_info['failType']}.")
        await asyncio.sleep(settings.XFYUN_SPEECH_POLL_INTERVAL_SECONDS)
    raise SpeechError("XFYun transcription polling timed out.")


def _ifasr_llm_signature(params: dict[str, str], api_secret: str) -> str:
    items = []
    for key in sorted(params.keys()):
        value = params[key]
        if value is not None and value != "":
            items.append(f"{key}={quote(str(value), safe='')}")
    base_string = "&".join(items)
    return base64.b64encode(
        hmac.new(api_secret.encode("utf-8"), base_string.encode("utf-8"), hashlib.sha1).digest()
    ).decode("utf-8")


async def submit_ifasr_llm_job(audio_bytes: bytes, filename: str, duration_ms: int, language: str) -> tuple[str, int]:
    settings = get_settings()
    signature_random = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    params = {
        "appId": settings.XFYUN_APP_ID,
        "accessKeyId": settings.XFYUN_API_KEY,
        "dateTime": datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "signatureRandom": signature_random,
        "fileSize": str(len(audio_bytes)),
        "fileName": filename,
        "duration": str(duration_ms),
        "language": language,
    }
    signature = _ifasr_llm_signature(params, settings.XFYUN_API_SECRET)
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "https://office-api-ist-dx.iflyaisol.com/v2/upload",
            params=params,
            headers={"Content-Type": "application/octet-stream", "signature": signature},
            content=audio_bytes,
        )
        response.raise_for_status()
        payload = response.json()
    if payload.get("code") != "000000":
        raise SpeechError(payload.get("descInfo", "XFYun IFASR LLM upload failed."))
    content = payload.get("content") or {}
    return content["orderId"], int(content.get("taskEstimateTime", 0))


async def poll_ifasr_llm_result(order_id: str, result_type: str = "transfer") -> dict:
    settings = get_settings()
    deadline = time.monotonic() + settings.XFYUN_SPEECH_POLL_TIMEOUT_SECONDS
    signature_random = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    async with httpx.AsyncClient(timeout=120) as client:
        while time.monotonic() < deadline:
            params = {
                "accessKeyId": settings.XFYUN_API_KEY,
                "dateTime": datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
                "signatureRandom": signature_random,
                "orderId": order_id,
                "resultType": result_type,
            }
            signature = _ifasr_llm_signature(params, settings.XFYUN_API_SECRET)
            response = await client.post(
                "https://office-api-ist-dx.iflyaisol.com/v2/getResult",
                params=params,
                headers={"Content-Type": "application/json", "signature": signature},
                json={},
            )
            response.raise_for_status()
            payload = response.json()
            if payload.get("code") != "000000":
                raise SpeechError(payload.get("descInfo", "XFYun IFASR LLM query failed."))

            content = payload.get("content") or {}
            order_info = content.get("orderInfo") or {}
            status = order_info.get("status")
            if status == 4:
                return content
            if order_info.get("failType", 0):
                raise SpeechError(f"XFYun transcription failed with failType={order_info['failType']}.")
            await asyncio.sleep(settings.XFYUN_SPEECH_POLL_INTERVAL_SECONDS)
    raise SpeechError("XFYun transcription polling timed out.")


def extract_text_from_order_result(order_result: str | dict) -> tuple[str, list[dict]]:
    if isinstance(order_result, str):
        parsed = json.loads(order_result)
    else:
        parsed = order_result

    segments: list[dict] = []
    texts: list[str] = []
    for item in parsed.get("lattice2") or parsed.get("lattice") or []:
        json_best = item.get("json_1best")
        if isinstance(json_best, str):
            json_best = json.loads(json_best)
        st = (json_best or {}).get("st", {})
        words = []
        for rt in st.get("rt", []):
            for ws in rt.get("ws", []):
                for candidate in ws.get("cw", []):
                    word = candidate.get("w", "")
                    if word:
                        words.append(word)
                        break
        segment_text = "".join(words).strip()
        if segment_text:
            texts.append(segment_text)
            segments.append(
                {
                    "text": segment_text,
                    "begin": int(item.get("begin") or st.get("bg") or 0),
                    "end": int(item.get("end") or st.get("ed") or 0),
                    "speaker": item.get("spk"),
                }
            )
    return "".join(texts), segments


def assemble_ws_auth_url(url: str, api_key: str, api_secret: str) -> str:
    index = url.index("://")
    host = url[index + 3 :]
    schema = url[: index + 3]
    path_index = host.index("/")
    path = host[path_index:]
    host = host[:path_index]

    date = format_date_time(mktime(datetime.now().timetuple()))
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    signature_sha = hmac.new(
        api_secret.encode("utf-8"),
        signature_origin.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    signature = base64.b64encode(signature_sha).decode("utf-8")
    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")
    return f"{schema}{host}{path}?{urlencode({'authorization': authorization, 'date': date, 'host': host})}"


async def synthesize_tts_audio(text: str, voice: str, speed: int, volume: int, pitch: int, audio_format: str, sample_rate: int) -> tuple[bytes, dict]:
    settings = get_settings()
    url = assemble_ws_auth_url("wss://tts-api.xfyun.cn/v2/tts", settings.XFYUN_API_KEY, settings.XFYUN_API_SECRET)
    request_body = {
        "common": {"app_id": settings.XFYUN_APP_ID},
        "business": {
            "aue": "lame" if audio_format == "mp3" else "raw",
            "auf": f"audio/L16;rate={sample_rate}",
            "vcn": voice,
            "speed": speed,
            "volume": volume,
            "pitch": pitch,
            "tte": "utf8",
        },
        "data": {
            "status": 2,
            "text": base64.b64encode(text.encode("utf-8")).decode("utf-8"),
        },
    }
    audio_chunks: list[bytes] = []
    result_meta = {"format": audio_format, "sample_rate": sample_rate, "voice": voice}
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(request_body))
        async for message in websocket:
            payload = json.loads(message)
            if payload.get("code", 0) != 0:
                raise SpeechError(payload.get("message", "XFYun TTS failed."))
            data = payload.get("data") or {}
            audio = data.get("audio")
            if audio:
                audio_chunks.append(base64.b64decode(audio))
            if data.get("status") == 2:
                break
    return b"".join(audio_chunks), result_meta
