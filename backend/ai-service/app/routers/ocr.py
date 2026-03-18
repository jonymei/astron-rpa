import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.config import get_settings
from app.dependencies.points import PointChecker, PointsContext
from app.logger import get_logger
from app.schemas.ocr import (
    DocumentOCRRequest,
    DocumentOCRResponse,
    OCRGeneralRequestBody,
    OCRGeneralResponseBody,
    PDFOCRResponse,
)
from app.services.point import PointTransactionType
from app.utils.ocr import OCRError, recognize_text_from_image
from app.utils.ocr.document_ocr import DocumentOCRClient
from app.utils.ocr.pdf_ocr import PDFOCRClient

logger = get_logger(__name__)

router = APIRouter(
    prefix="/ocr",
    tags=["开放平台OCR"],
)


@router.post("/general", response_model=OCRGeneralResponseBody)
async def general_ocr(
    params: OCRGeneralRequestBody,
    points_context: PointsContext = Depends(
        PointChecker(get_settings().OCR_GENERAL_POINTS_COST, PointTransactionType.XFYUN_COST),
    ),
):
    """
    Perform OCR on an image using Xunfei's general text recognition API.

    Returns:
        OCR result in the following format:
        {
          "header": {
            "code": 0,
            "message": "success",
            "sid": "ase000d1688@hu17b34308ea40210882"
          },
          "payload": {
            "result": {
              "compress": "raw",
              "encoding": "utf8",
              "format": "json",
              "text": "ewogImNhdGVnb3J5IjogImNoX2VuX3B1YmxpY19jbG91ZC..."
            }
          }
        }

    Raises:
        HTTPException: 400 for invalid requests, 500 for server errors, 503 for network issues
    """
    try:
        # 调用上游 OCR 服务
        result = await recognize_text_from_image(params.image, params.encoding, params.status)

        # 检查结果并处理积分扣除
        if result.header.code == 0:
            # 成功时才扣除积分
            await points_context.deduct_points()
            logger.info("OCR processing successful, points deducted for user")

        return result

    except OCRError as e:
        # 业务逻辑错误 - 400 Bad Request
        logger.error(f"OCR business logic error: {e.message}")
        raise HTTPException(status_code=400, detail=f"OCR processing failed: {e.message}")

    except httpx.HTTPError as e:
        # 网络错误 - 503 Service Unavailable
        logger.error(f"OCR service network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="OCR service is temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        # 其他未预期的错误 - 500 Internal Server Error
        logger.error(f"Unexpected error in OCR processing: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during OCR processing")


@router.post("/document", response_model=DocumentOCRResponse)
async def document_ocr(
    params: DocumentOCRRequest,
    points_context: PointsContext = Depends(
        PointChecker(50, PointTransactionType.XFYUN_COST),
    ),
):
    """
    通用文档识别（OCR大模型）.

    基于星火大模型的文档识别能力，支持公式、图表、栏目等复杂场景。

    Args:
        params: 请求参数，包含 base64 编码的图像和输出配置

    Returns:
        DocumentOCRResponse: 识别结果

    Raises:
        HTTPException: 400/500/503 错误
    """
    try:
        client = DocumentOCRClient()
        result = await client.recognize(
            params.image, params.encoding, params.output_level, params.output_format
        )

        # 成功时扣除积分
        if result.header.code == 0:
            await points_context.deduct_points()
            logger.info("Document OCR processing successful, points deducted")

        return result

    except OCRError as e:
        logger.error(f"Document OCR business logic error: {e.message}")
        raise HTTPException(status_code=400, detail=f"Document OCR failed: {e.message}")

    except httpx.HTTPError as e:
        logger.error(f"Document OCR service network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Document OCR service is temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        logger.error(f"Unexpected error in Document OCR: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during Document OCR")


@router.post("/pdf", response_model=PDFOCRResponse)
async def pdf_ocr(
    file: UploadFile = File(None),
    pdf_url: str = Form(None),
    export_format: str = Form("json"),
    points_context: PointsContext = Depends(
        PointChecker(0, PointTransactionType.XFYUN_COST),  # 初始不扣费，按页数计费
    ),
):
    """
    PDF 文档识别（OCR大模型）.

    支持多页 PDF 文档识别，按页数计费（10 积分/页）。

    Args:
        file: 上传的 PDF 文件（与 pdf_url 二选一）
        pdf_url: PDF 文件的公网 URL（与 file 二选一）
        export_format: 导出格式 (word, markdown, json)

    Returns:
        PDFOCRResponse: 任务信息和识别结果

    Raises:
        HTTPException: 400/500/503 错误
    """
    try:
        if not file and not pdf_url:
            raise HTTPException(status_code=400, detail="Either file or pdf_url must be provided")

        client = PDFOCRClient()
        result = await client.recognize(file, pdf_url, export_format)

        # 按页数扣费：10 积分/页
        if result.status == "completed":
            points_to_deduct = result.page_count * 10
            await points_context.deduct_custom_points(points_to_deduct)
            logger.info(f"PDF OCR completed, {result.page_count} pages, deducted {points_to_deduct} points")

        return result

    except OCRError as e:
        logger.error(f"PDF OCR business logic error: {e.message}")
        raise HTTPException(status_code=400, detail=f"PDF OCR failed: {e.message}")

    except httpx.HTTPError as e:
        logger.error(f"PDF OCR service network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="PDF OCR service is temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        logger.error(f"Unexpected error in PDF OCR: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during PDF OCR")
