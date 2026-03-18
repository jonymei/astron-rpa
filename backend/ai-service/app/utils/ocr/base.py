"""Base client for XunFei OCR APIs."""

from typing import Any

import httpx

from app.logger import get_logger
from app.utils.ocr.auth import AuthStrategy, HmacSHA256Auth, MD5HmacSHA1Auth
from app.utils.ocr.config import OCRConfig

logger = get_logger(__name__)


class OCRError(Exception):
    """Custom exception for OCR-related errors."""

    def __init__(self, msg: str):
        self.message = msg
        super().__init__(msg)


class XFYunOCRClient:
    """Base client for XunFei OCR APIs with configurable authentication and request modes."""

    def __init__(self, config: OCRConfig):
        self.config = config
        self.auth_strategy = self._create_auth_strategy()

    def _create_auth_strategy(self) -> AuthStrategy:
        """根据配置创建认证策略."""
        if self.config.auth_type == "hmac_sha256":
            return HmacSHA256Auth()
        elif self.config.auth_type == "md5_hmac_sha1":
            return MD5HmacSHA1Auth()
        else:
            raise ValueError(f"Unknown auth type: {self.config.auth_type}")

    async def _make_request(
        self, method: str, url: str, headers: dict[str, Any] | None = None, **kwargs
    ) -> httpx.Response:
        """发起 HTTP 请求."""
        # 构建认证 URL 和请求头
        auth_url = self.auth_strategy.build_auth_url(url)
        auth_headers = self.auth_strategy.build_auth_headers()

        # 合并请求头
        final_headers = {**auth_headers, **(headers or {})}

        logger.debug(f"Making {method} request to {auth_url}")

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.request(method, auth_url, headers=final_headers, **kwargs)
            response.raise_for_status()
            return response
