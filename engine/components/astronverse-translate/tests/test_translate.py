import unittest
from unittest.mock import MagicMock, patch

import requests

from astronverse.translate.error import BaseException
from astronverse.translate.translator import TranslatorAI


class TestTranslatorAI(unittest.TestCase):
    @patch("astronverse.translate.core.requests.post")
    def test_translate_text_posts_to_normalized_chat_completions_url(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello world"}}],
        }
        mock_post.return_value = mock_response

        result = TranslatorAI.translate_text(
            base_url="https://example.com/v1/",
            api_key="test-key",
            model="gpt-4o-mini",
            target_language="english",
            source_text="你好，世界",
        )

        self.assertEqual(result, "Hello world")
        mock_post.assert_called_once()
        self.assertEqual(mock_post.call_args.args[0], "https://example.com/v1/chat/completions")
        self.assertEqual(mock_post.call_args.kwargs["headers"]["Authorization"], "Bearer test-key")
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["model"], "gpt-4o-mini")
        self.assertFalse(payload["stream"])
        self.assertIn("english", payload["messages"][0]["content"].lower())
        self.assertIn("你好，世界", payload["messages"][1]["content"])

    @patch("astronverse.translate.core.requests.post")
    def test_translate_text_supports_nested_data_choices_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": {
                "choices": [{"message": {"content": "Hola mundo"}}],
            }
        }
        mock_post.return_value = mock_response

        result = TranslatorAI.translate_text(
            base_url="https://example.com/openai",
            api_key="test-key",
            model="translator-1",
            target_language="spanish",
            source_text="Hello world",
        )

        self.assertEqual(result, "Hola mundo")
        self.assertEqual(mock_post.call_args.args[0], "https://example.com/openai/chat/completions")

    @patch("astronverse.translate.core.requests.post")
    def test_translate_text_raises_domain_error_for_invalid_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"unexpected": "shape"}
        mock_post.return_value = mock_response

        with self.assertRaises(BaseException) as exc_info:
            TranslatorAI.translate_text(
                base_url="https://example.com/v1",
                api_key="test-key",
                model="translator-1",
                target_language="french",
                source_text="Hello world",
            )

        self.assertIn("翻译接口返回结果格式不受支持", str(exc_info.exception))
        self.assertIn("unsupported response shape", exc_info.exception.message)

    @patch("astronverse.translate.core.requests.post")
    def test_translate_text_raises_domain_error_for_request_failure(self, mock_post):
        mock_post.side_effect = requests.RequestException("connection timeout")

        with self.assertRaises(BaseException) as exc_info:
            TranslatorAI.translate_text(
                base_url="https://example.com/v1",
                api_key="test-key",
                model="translator-1",
                target_language="french",
                source_text="Hello world",
            )

        self.assertIn("翻译接口请求失败", str(exc_info.exception))
        self.assertIn("connection timeout", exc_info.exception.message)


if __name__ == "__main__":
    unittest.main()
