import requests
from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta
from astronverse.actionlib.atomic import atomicMg

from astronverse.translate import TargetLanguageTypes
from astronverse.translate.error import TranslateAPIError


class TranslatorAI:
    """Translate free text with a user-configured OpenAI-compatible API."""

    @staticmethod
    def _build_chat_completions_url(base_url: str) -> str:
        normalized = base_url.rstrip("/")
        if normalized.endswith("/chat/completions"):
            return normalized
        return f"{normalized}/chat/completions"

    @staticmethod
    def _build_payload(model: str, target_language: str, source_text: str) -> dict:
        return {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a translation engine. Translate the user text into "
                        f"{target_language}. Return only the translated text without explanation."
                    ),
                },
                {"role": "user", "content": source_text},
            ],
            "stream": False,
        }

    @staticmethod
    def _extract_content(response_json: dict) -> str:
        choices = response_json.get("choices")
        if not choices and isinstance(response_json.get("data"), dict):
            choices = response_json["data"].get("choices")

        if not choices:
            raise TranslateAPIError("Translation API returned an unsupported response shape.")

        try:
            content = choices[0]["message"]["content"]
        except (IndexError, KeyError, TypeError) as exc:
            raise TranslateAPIError("Translation API response is missing message content.") from exc

        if not isinstance(content, str) or not content.strip():
            raise TranslateAPIError("Translation API returned empty translated text.")

        return content.strip()

    @staticmethod
    @atomicMg.atomic(
        "TranslatorAI",
        inputList=[
            atomicMg.param(
                "source_text",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_PYTHON_TEXTAREAMODAL_VARIABLE.value),
            )
        ],
        outputList=[atomicMg.param("translated_text", types="Str")],
    )
    def translate_text(
        base_url: str,
        api_key: str,
        model: str,
        target_language: TargetLanguageTypes = TargetLanguageTypes.ENGLISH,
        source_text: str = "",
    ) -> str:
        url = TranslatorAI._build_chat_completions_url(base_url=base_url)
        payload = TranslatorAI._build_payload(
            model=model,
            target_language=target_language.value if isinstance(target_language, TargetLanguageTypes) else str(target_language),
            source_text=source_text,
        )
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise TranslateAPIError(f"Translation API request failed: {exc}") from exc

        return TranslatorAI._extract_content(response.json())
