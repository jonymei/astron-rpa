import base64

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.config import get_settings
from app.dependencies import get_user_id_from_header, get_user_point_service
from app.logger import get_logger
from app.schemas.speech import (
    SpeechASRRequestBody,
    SpeechASRResponseBody,
    SpeechTranscriptionRequestBody,
    SpeechTTSRequestBody,
    SpeechTTSResponseBody,
)
from app.services.point import PointTransactionType, UserPointService
from app.services.speech_pricing import calculate_audio_points, calculate_text_points
from app.utils.speech import (
    SpeechError,
    decode_audio_base64,
    extract_text_from_order_result,
    get_audio_duration_seconds,
    poll_ifasr_llm_result,
    poll_raasr_result,
    submit_ifasr_llm_job,
    submit_raasr_job,
    synthesize_tts_audio,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/speech", tags=["开放平台语音"])


async def _ensure_points(user_id: str, service: UserPointService, required_points: int):
    await service.grant_monthly_points(user_id)
    points = await service.get_cached_points(user_id)
    if points < required_points:
        raise HTTPException(status_code=403, detail="Insufficient points.")


async def _deduct_points(user_id: str, service: UserPointService, points_cost: int, description: str):
    await service.deduct_points(
        user_id=user_id,
        amount=points_cost,
        transaction_type=PointTransactionType.XFYUN_COST,
        description=description,
    )


@router.post("/asr/chinese", response_model=SpeechASRResponseBody)
async def speech_asr_chinese(
    params: SpeechASRRequestBody,
    user_id: str = Depends(get_user_id_from_header),
    point_service: UserPointService = Depends(get_user_point_service),
):
    return await _handle_asr_request(params, user_id, point_service, default_language="cn")


@router.post("/asr/multilingual", response_model=SpeechASRResponseBody)
async def speech_asr_multilingual(
    params: SpeechASRRequestBody,
    user_id: str = Depends(get_user_id_from_header),
    point_service: UserPointService = Depends(get_user_point_service),
):
    return await _handle_asr_request(params, user_id, point_service, default_language=params.language)


@router.post("/transcription", response_model=SpeechASRResponseBody)
async def speech_transcription(
    params: SpeechTranscriptionRequestBody,
    user_id: str = Depends(get_user_id_from_header),
    point_service: UserPointService = Depends(get_user_point_service),
):
    settings = get_settings()
    try:
        audio_bytes = decode_audio_base64(params.audio_base64)
        duration_seconds = get_audio_duration_seconds(audio_bytes, params.filename)
        points_cost = calculate_audio_points(
            duration_seconds,
            settings.XFYUN_SPEECH_ASR_SECONDS_PER_UNIT,
            settings.XFYUN_SPEECH_ASR_POINTS_PER_UNIT,
        )
        await _ensure_points(user_id, point_service, points_cost)
        order_id, _ = await submit_ifasr_llm_job(
            audio_bytes,
            params.filename,
            int(duration_seconds * 1000),
            params.language,
        )
        result_content = await poll_ifasr_llm_result(order_id, result_type=params.result_type)
        text, segments = extract_text_from_order_result(result_content.get("orderResult", "{}"))
        await _deduct_points(user_id, point_service, points_cost, description=f"speech_transcription:{order_id}")
        return SpeechASRResponseBody(
            text=text,
            result={"order_id": order_id, "segments": segments, "raw": result_content},
            duration_seconds=duration_seconds,
            points_cost=points_cost,
        )
    except SpeechError as exc:
        logger.error(f"Speech transcription error: {exc.message}")
        raise HTTPException(status_code=400, detail=exc.message)
    except httpx.HTTPError as exc:
        logger.error(f"Speech transcription network error: {exc}")
        raise HTTPException(status_code=503, detail="Speech service is temporarily unavailable.")


async def _handle_asr_request(params, user_id: str, point_service: UserPointService, default_language: str, result_type: str = "transfer"):
    settings = get_settings()
    try:
        audio_bytes = decode_audio_base64(params.audio_base64)
        duration_seconds = get_audio_duration_seconds(audio_bytes, params.filename)
        points_cost = calculate_audio_points(
            duration_seconds,
            settings.XFYUN_SPEECH_ASR_SECONDS_PER_UNIT,
            settings.XFYUN_SPEECH_ASR_POINTS_PER_UNIT,
        )
        await _ensure_points(user_id, point_service, points_cost)
        order_id, _ = await submit_raasr_job(audio_bytes, params.filename, duration_seconds, default_language)
        result_content = await poll_raasr_result(order_id, result_type=result_type)
        text, segments = extract_text_from_order_result(result_content.get("orderResult", "{}"))
        await _deduct_points(user_id, point_service, points_cost, description=f"speech_asr:{order_id}")
        return SpeechASRResponseBody(
            text=text,
            result={"order_id": order_id, "segments": segments, "raw": result_content},
            duration_seconds=duration_seconds,
            points_cost=points_cost,
        )
    except SpeechError as exc:
        logger.error(f"Speech ASR error: {exc.message}")
        raise HTTPException(status_code=400, detail=exc.message)
    except httpx.HTTPError as exc:
        logger.error(f"Speech ASR network error: {exc}")
        raise HTTPException(status_code=503, detail="Speech service is temporarily unavailable.")


@router.post("/tts", response_model=SpeechTTSResponseBody)
async def speech_tts(
    params: SpeechTTSRequestBody,
    user_id: str = Depends(get_user_id_from_header),
    point_service: UserPointService = Depends(get_user_point_service),
):
    settings = get_settings()
    try:
        points_cost = calculate_text_points(
            params.text,
            settings.XFYUN_SPEECH_TTS_CHARS_PER_UNIT,
            settings.XFYUN_SPEECH_TTS_POINTS_PER_UNIT,
        )
        await _ensure_points(user_id, point_service, points_cost)
        audio_bytes, result_meta = await synthesize_tts_audio(
            text=params.text,
            voice=params.voice,
            speed=params.speed,
            volume=params.volume,
            pitch=params.pitch,
            audio_format=params.audio_format,
            sample_rate=params.sample_rate,
        )
        await _deduct_points(user_id, point_service, points_cost, description="speech_tts")
        return SpeechTTSResponseBody(
            audio_base64=base64.b64encode(audio_bytes).decode("utf-8"),
            result=result_meta,
            points_cost=points_cost,
        )
    except SpeechError as exc:
        logger.error(f"Speech TTS error: {exc.message}")
        raise HTTPException(status_code=400, detail=exc.message)
    except httpx.HTTPError as exc:
        logger.error(f"Speech TTS network error: {exc}")
        raise HTTPException(status_code=503, detail="Speech service is temporarily unavailable.")
