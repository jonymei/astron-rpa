import base64
import os
import re
import time
from pathlib import Path

import httpx
import pytest


RUN_LOCAL_TESTS = os.getenv("RUN_LOCAL_SPEECH_E2E") == "1"
BASE_URL = os.getenv("LOCAL_SPEECH_E2E_BASE_URL", "http://127.0.0.1:8010").rstrip("/")
USER_ID = os.getenv("LOCAL_SPEECH_E2E_USER_ID", "123")
TTS_VOICE = os.getenv("LOCAL_SPEECH_E2E_TTS_VOICE", "x5_lingyuyan_flow")
ZH_AUDIO_FILE = os.getenv("LOCAL_SPEECH_E2E_ZH_AUDIO_FILE", "").strip()
MULTILINGUAL_AUDIO_FILE = os.getenv("LOCAL_SPEECH_E2E_MULTILINGUAL_AUDIO_FILE", "").strip()
TRANSCRIPTION_AUDIO_FILE = os.getenv("LOCAL_SPEECH_E2E_TRANSCRIPTION_AUDIO_FILE", "").strip()
ARTIFACT_DIR = os.getenv("LOCAL_SPEECH_E2E_ARTIFACT_DIR", "").strip()
ZH_TEXT = os.getenv(
    "LOCAL_SPEECH_E2E_ZH_TEXT",
    "\u4f60\u597d\uff0c\u8fd9\u662f\u4e2d\u6587\u8bed\u97f3\u8bc6\u522b\u7aef\u5230\u7aef\u6d4b\u8bd5\u3002",
)
MULTILINGUAL_TEXT = os.getenv(
    "LOCAL_SPEECH_E2E_MULTILINGUAL_TEXT",
    "Hello, this is an English speech recognition end to end test.",
)


pytestmark = pytest.mark.skipif(
    not RUN_LOCAL_TESTS,
    reason="local speech e2e tests are skipped by default; set RUN_LOCAL_SPEECH_E2E=1 to run them",
)


def _headers() -> dict[str, str]:
    return {
        "content-type": "application/json",
        "X-User-Id": USER_ID,
    }


def _post(path: str, payload: dict, timeout: int = 180) -> dict:
    response = httpx.post(
        f"{BASE_URL}{path}",
        json=payload,
        headers=_headers(),
        timeout=timeout,
    )
    assert response.status_code == 200, (
        f"POST {path} failed with status={response.status_code}, body={response.text}"
    )
    return response.json()


def _normalize_text(text: str) -> str:
    return re.sub(r"[\W_]+", "", text).lower()


def _assert_text_has_overlap(actual: str, expected: str, minimum_common_chars: int = 4):
    actual_normalized = _normalize_text(actual)
    expected_normalized = _normalize_text(expected)

    assert actual_normalized, f"recognized text is empty: {actual!r}"
    assert expected_normalized, f"expected text is empty: {expected!r}"

    common_chars = set(actual_normalized) & set(expected_normalized)
    assert len(common_chars) >= minimum_common_chars, (
        f"text overlap too small; expected={expected!r}, actual={actual!r}, common={sorted(common_chars)!r}"
    )


def _assert_asr_response_has_text(response: dict, expected_text: str, minimum_common_chars: int = 2):
    actual_text = (response.get("text") or "").strip()
    if actual_text:
        _assert_text_has_overlap(actual_text, expected_text, minimum_common_chars=minimum_common_chars)
        return

    pytest.fail(
        f"recognition returned empty text; expected={expected_text!r}, response={response!r}"
    )


def _decode_audio(audio_base64: str) -> bytes:
    audio_bytes = base64.b64decode(audio_base64)
    assert audio_bytes, "tts returned empty audio"
    return audio_bytes


def _load_audio_file(audio_file: str) -> tuple[bytes, str, str]:
    path = Path(audio_file)
    assert path.exists(), f"audio file not found: {audio_file}"
    audio_bytes = path.read_bytes()
    assert audio_bytes, f"audio file is empty: {audio_file}"
    return audio_bytes, path.name, str(path)


def _build_artifact_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    if ARTIFACT_DIR:
        path = Path(ARTIFACT_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path
    return tmp_path_factory.mktemp("speech_e2e_audio")


def _synthesize_audio_to_file(
    *,
    text: str,
    voice: str,
    output_file: Path,
    speed: int,
) -> tuple[bytes, str, str]:
    last_error = None
    for _ in range(3):
        try:
            response = _post(
                "/speech/tts",
                {
                    "text": text,
                    "voice": voice,
                    "speed": speed,
                    "volume": 50,
                    "pitch": 50,
                    "audio_format": "mp3",
                    "sample_rate": 16000,
                },
            )
            audio_base64 = response.get("audio_base64")
            assert audio_base64, f"tts returned no audio_base64: {response!r}"
            assert response["result"]["format"] == "mp3"
            assert response["result"]["voice"] == voice
            assert response["points_cost"] > 0

            audio_bytes = _decode_audio(audio_base64)
            output_file.write_bytes(audio_bytes)
            assert output_file.stat().st_size > 0, f"generated audio file is empty: {output_file}"
            return audio_bytes, output_file.name, str(output_file)
        except AssertionError as exc:
            last_error = exc
            time.sleep(2)

    raise AssertionError(f"tts failed after retries for text={text!r}: {last_error}")


@pytest.fixture(scope="module")
def synthesized_zh_audio(tmp_path_factory: pytest.TempPathFactory) -> tuple[bytes, str, str]:
    if ZH_AUDIO_FILE:
        return _load_audio_file(ZH_AUDIO_FILE)

    artifact_dir = _build_artifact_dir(tmp_path_factory)
    return _synthesize_audio_to_file(
        text=ZH_TEXT,
        voice=TTS_VOICE,
        output_file=artifact_dir / "tts_zh.mp3",
        speed=35,
    )


@pytest.fixture(scope="module")
def synthesized_en_audio(tmp_path_factory: pytest.TempPathFactory) -> tuple[bytes, str, str]:
    if MULTILINGUAL_AUDIO_FILE:
        return _load_audio_file(MULTILINGUAL_AUDIO_FILE)

    artifact_dir = _build_artifact_dir(tmp_path_factory)
    return _synthesize_audio_to_file(
        text=MULTILINGUAL_TEXT,
        voice=TTS_VOICE,
        output_file=artifact_dir / "tts_en.mp3",
        speed=30,
    )


def test_local_speech_tts_synthesizes_chinese_audio_file(synthesized_zh_audio):
    audio_bytes, filename, file_path = synthesized_zh_audio
    assert filename.endswith(".mp3")
    assert audio_bytes
    assert Path(file_path).stat().st_size > 0


def test_local_speech_tts_synthesizes_english_audio_file(synthesized_en_audio):
    audio_bytes, filename, file_path = synthesized_en_audio
    assert filename.endswith(".mp3")
    assert audio_bytes
    assert Path(file_path).stat().st_size > 0


def test_local_speech_asr_chinese_roundtrip(synthesized_zh_audio):
    audio_bytes, filename, _ = synthesized_zh_audio

    response = _post(
        "/speech/asr/chinese",
        {
            "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
            "filename": filename,
            "language": "cn",
        },
    )

    assert response["duration_seconds"] > 0
    assert response["points_cost"] > 0
    assert "result" in response
    _assert_asr_response_has_text(response, ZH_TEXT, minimum_common_chars=2)


def test_local_speech_asr_multilingual_roundtrip(synthesized_en_audio):
    audio_bytes, filename, _ = synthesized_en_audio

    response = _post(
        "/speech/asr/multilingual",
        {
            "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
            "filename": filename,
            "language": "en",
        },
    )

    assert response["duration_seconds"] > 0
    assert response["points_cost"] > 0
    assert "result" in response
    _assert_asr_response_has_text(response, MULTILINGUAL_TEXT, minimum_common_chars=3)


def test_local_speech_transcription_roundtrip(synthesized_zh_audio):
    if TRANSCRIPTION_AUDIO_FILE:
        audio_bytes, filename, _ = _load_audio_file(TRANSCRIPTION_AUDIO_FILE)
    else:
        audio_bytes, filename, _ = synthesized_zh_audio

    response = _post(
        "/speech/transcription",
        {
            "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
            "filename": filename,
            "language": "cn",
            "result_type": "transfer",
        },
        timeout=300,
    )

    assert response["duration_seconds"] > 0
    assert response["points_cost"] > 0
    assert response["result"]["order_id"]
    _assert_asr_response_has_text(response, ZH_TEXT, minimum_common_chars=2)
