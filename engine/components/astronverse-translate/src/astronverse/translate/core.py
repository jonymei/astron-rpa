"""翻译组件运行时实现。"""

import requests


class TranslateRequestError(Exception):
    """Raised when the remote translation API request fails."""


class TranslateResponseShapeError(Exception):
    """Raised when the translation API returns an unsupported payload shape."""


class TranslateResponseEmptyError(Exception):
    """Raised when the translation API returns empty translated text."""


class TranslatorCore:
    """HTTP client and response parser for OpenAI-compatible translation APIs."""

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
            raise TranslateResponseShapeError("unsupported response shape")

        try:
            content = choices[0]["message"]["content"]
        except (IndexError, KeyError, TypeError) as exc:
            raise TranslateResponseShapeError("response is missing message content") from exc

        if not isinstance(content, str) or not content.strip():
            raise TranslateResponseEmptyError("translated text is empty")

        return content.strip()

    @classmethod
    def translate_text(
        cls,
        base_url: str,
        api_key: str,
        model: str,
        target_language: str,
        source_text: str,
    ) -> str:
        url = cls._build_chat_completions_url(base_url=base_url)
        payload = cls._build_payload(
            model=model,
            target_language=target_language,
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
            raise TranslateRequestError(str(exc)) from exc

        return cls._extract_content(response.json())
