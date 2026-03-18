import unittest
from unittest.mock import patch, MagicMock
from astronverse.openapi.client import GatewayClient


class TestGatewayClientMultipart(unittest.TestCase):
    @patch('astronverse.openapi.client.requests.post')
    @patch('astronverse.openapi.client.atomicMg.cfg')
    def test_post_multipart_success(self, mock_cfg, mock_post):
        mock_cfg.return_value.get.return_value = "13159"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        result = GatewayClient.post_multipart("/ocr/general", b"fake_image", "test.jpg", {"lang": "zh"})

        self.assertEqual(result, {"status": "success"})
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args.args[0], "http://127.0.0.1:13159/api/rpa-ai-service/ocr/general")
        self.assertEqual(call_args.kwargs['files'], {"file": ("test.jpg", b"fake_image")})
        self.assertEqual(call_args.kwargs['data'], {"lang": "zh"})
