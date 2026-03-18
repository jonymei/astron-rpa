"""Configuration for OCR clients."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OCRConfig:
    """Configuration for a specific OCR API."""

    service_name: str  # 服务名称
    base_url: str  # API 端点
    auth_type: str  # 认证类型：'hmac_sha256' 或 'md5_hmac_sha1'
    request_mode: str  # 请求模式：'sync' 或 'async'
    service_id: Optional[str] = None  # 服务 ID（用于同步接口）
    timeout: float = 30.0  # 请求超时时间


# 通用文档识别（OCR大模型）配置
DOCUMENT_OCR_CONFIG = OCRConfig(
    service_name="document_ocr",
    base_url="https://cbm01.cn-huabei-1.xf-yun.com/v1/private/se75ocrbm",
    auth_type="hmac_sha256",
    request_mode="sync",
    service_id="se75ocrbm",
    timeout=30.0,
)

# PDF 文档识别（OCR大模型）配置
PDF_OCR_CONFIG = OCRConfig(
    service_name="pdf_ocr",
    base_url="https://iocr.xfyun.cn/ocrzdq/v1/pdfOcr",
    auth_type="md5_hmac_sha1",
    request_mode="async",
    service_id=None,
    timeout=30.0,
)
