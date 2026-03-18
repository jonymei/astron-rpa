"""Bank card OCR client."""

import base64
from typing import Any

from fastapi import UploadFile

from app.logger import get_logger
from app.utils.ocr.base import OCRError, XFYunOCRClient
from app.utils.ocr.config import BANK_CARD_CONFIG

logger = get_logger(__name__)


class BankCardOCRClient(XFYunOCRClient):
    """Client for bank card recognition using XunFei OCR API."""

    def __init__(self):
        super().__init__(BANK_CARD_CONFIG)

    async def recognize(self, file: UploadFile) -> dict[str, Any]:
        """识别银行卡.

        Args:
            file: 上传的图片文件
        """
        # 读取图片并编码
        image_data = await file.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        # 发起请求（使用表单数据）
        data = {"image": image_base64}
        response = await self._make_request("POST", self.config.base_url, data=data)
        result = response.json()

        # 检查响应
        code = result.get("code")
        if code != "0":
            error_msg = result.get("desc", "Unknown error")
            raise OCRError(f"OCR failed: {error_msg}")

        return result.get("data", {})
