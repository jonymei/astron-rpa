import json
import os
import re
import time
from pathlib import Path

import pytest
import requests

from astronverse.actionlib.atomic import atomicMg
from astronverse.openapi.client import GatewayClient
from astronverse.openapi import speech_asr_zh, speech_asr_multilingual, speech_tts_ultra_human


RUN_LOCAL_TESTS = os.getenv("RUN_LOCAL_OPENAPI_TESTS") == "1"
AI_SERVICE_BASE_URL = os.getenv("OPENAPI_LOCAL_AI_SERVICE_BASE_URL", "http://127.0.0.1:8010").rstrip("/")
AI_SERVICE_USER_ID = os.getenv("OPENAPI_LOCAL_USER_ID", "123")
TTS_VOICE = os.getenv("OPENAPI_LOCAL_TTS_VOICE", "x5_lingyuyan_flow")
ZH_TEXT = os.getenv("OPENAPI_LOCAL_ZH_TEXT", "你好，这是 engine 到 ai-service 的本地联调测试。")
EN_TEXT = os.getenv(
    "OPENAPI_LOCAL_EN_TEXT",
    "Hello, this is a local integration test from engine to ai-service.",
)


pytestmark = pytest.mark.skipif(
    not RUN_LOCAL_TESTS,
    reason="local openapi tests are skipped by default; set RUN_LOCAL_OPENAPI_TESTS=1 to run them",
)


def _post_ai_service_direct(path: str, payload: dict) -> dict:
    last_response = None
    for _ in range(3):
        response = requests.post(
            f"{AI_SERVICE_BASE_URL}{path}",
            data=json.dumps(payload),
            headers={"content-type": "application/json", "X-User-Id": AI_SERVICE_USER_ID},
            timeout=180,
        )
        if response.status_code == 200:
            return response.json()
        last_response = response
        time.sleep(2)
    assert last_response is not None
    assert last_response.status_code == 200, last_response.text
    return {}


@pytest.fixture(autouse=True)
def configure_local_direct_ai_service(monkeypatch):
    monkeypatch.setattr(
        atomicMg.__class__,
        "_cfg",
        {
            "GATEWAY_PORT": "",
            "WS": None,
        },
    )
    monkeypatch.setattr(GatewayClient, "post", staticmethod(_post_ai_service_direct))


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


def test_local_openapi_speech_asr_zh_roundtrip(tmp_path):
    tts_result = speech_tts_ultra_human(
        text=ZH_TEXT,
        voice=TTS_VOICE,
        speed=35,
        dst_file=str(tmp_path),
        dst_file_name="engine_zh_roundtrip",
    )

    audio_path = Path(tts_result["audio_file"])
    assert audio_path.exists()
    assert audio_path.stat().st_size > 0

    asr_result = speech_asr_zh(
        src_file=str(audio_path),
        is_save=True,
        dst_file=str(tmp_path),
        dst_file_name="engine_zh_asr",
        save_format="txt",
    )

    assert asr_result["text"]
    _assert_text_has_overlap(asr_result["text"], ZH_TEXT, minimum_common_chars=2)
    assert Path(asr_result["saved_file"]).read_text(encoding="utf-8").strip() == asr_result["text"].strip()


def test_local_openapi_speech_asr_multilingual_roundtrip(tmp_path):
    tts_result = speech_tts_ultra_human(
        text=EN_TEXT,
        voice=TTS_VOICE,
        speed=30,
        dst_file=str(tmp_path),
        dst_file_name="engine_en_roundtrip",
    )

    audio_path = Path(tts_result["audio_file"])
    assert audio_path.exists()
    assert audio_path.stat().st_size > 0

    asr_result = speech_asr_multilingual(
        src_file=str(audio_path),
        language="en",
        is_save=True,
        dst_file=str(tmp_path),
        dst_file_name="engine_en_asr",
        save_format="txt",
    )

    assert asr_result["text"]
    _assert_text_has_overlap(asr_result["text"], EN_TEXT, minimum_common_chars=3)
    assert Path(asr_result["saved_file"]).read_text(encoding="utf-8").strip() == asr_result["text"].strip()
