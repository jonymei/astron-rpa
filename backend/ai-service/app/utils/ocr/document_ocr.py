"""Document OCR client for general document recognition using OCR LLM."""

import json
from typing import Any

from app.logger import get_logger
from app.schemas.ocr import DocumentOCRResponse
from app.utils.ocr.base import OCRError, XFYunOCRClient
from app.utils.ocr.config import DOCUMENT_OCR_CONFIG

logger = get_logger(__name__)


class DocumentOCRClient(XFYunOCRClient):
    """Client for general document OCR using XunFei OCR LLM."""

    def __init__(self):
        super().__init__(DOCUMENT_OCR_CONFIG)

    def _build_request_payload(
        self, image_base64: str, encoding: str = "jpg", output_level: int = 1, output_format: str = "markdown"
    ) -> dict[str, Any]:
        """构建请求 payload."""
        return {
            "header": {"app_id": self.auth_strategy.app_id, "status": 3},
            "parameter": {
                "ocr": {
                    "output_level": output_level,
                    "output_format": output_format,
                    "result": {"encoding": "utf8", "compress": "raw", "format": "json"},
                }
            },
            "payload": {
                "image": {
                    "encoding": encoding,
                    "image": image_base64,
                    "status": 3,
                }
            },
        }

    async def recognize(
        self, image_base64: str, encoding: str = "jpg", output_level: int = 1, output_format: str = "markdown"
    ) -> DocumentOCRResponse:
        """
        识别文档图像.

        Args:
            image_base64: Base64 编码的图像
            encoding: 图像格式 (jpg, png, etc.)
            output_level: 输出级别 (1-3)
            output_format: 输出格式 (markdown, json, etc.)

        Returns:
            DocumentOCRResponse: 识别结果

        Raises:
            OCRError: 识别失败时抛出
        """
        try:
            payload = self._build_request_payload(image_base64, encoding, output_level, output_format)

            response = await self._make_request("POST", self.config.base_url, json=payload)

            result = response.json()
            model = DocumentOCRResponse.model_validate(result)

            if model.header.code != 0:
                error_message = model.header.message or "Unknown API error"
                raise OCRError(f"API returned error: {error_message}")

            logger.info("Document OCR processing completed successfully")
            return model

        except Exception as e:
            logger.error(f"Document OCR processing failed: {e}")
            raise
