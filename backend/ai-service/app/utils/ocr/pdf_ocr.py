"""PDF OCR client for PDF document recognition."""

import asyncio
from typing import Any, Optional

from fastapi import UploadFile

from app.logger import get_logger
from app.schemas.ocr import PDFOCRResponse
from app.utils.ocr.base import OCRError, XFYunOCRClient
from app.utils.ocr.config import PDF_OCR_CONFIG

logger = get_logger(__name__)


class PDFOCRClient(XFYunOCRClient):
    """Client for PDF document OCR using XunFei OCR LLM."""

    def __init__(self):
        super().__init__(PDF_OCR_CONFIG)
        self.poll_interval = 5  # 轮询间隔（秒）
        self.max_poll_time = 300  # 最大轮询时间（秒）

    async def _create_task(
        self, file: Optional[UploadFile] = None, pdf_url: Optional[str] = None, export_format: str = "json"
    ) -> dict[str, Any]:
        """创建 PDF OCR 任务."""
        if not file and not pdf_url:
            raise OCRError("Either file or pdf_url must be provided")

        url = f"{self.config.base_url}/start"

        if file:
            # 上传文件
            file_content = await file.read()
            files = {"file": (file.filename, file_content, file.content_type)}
            data = {"exportFormat": export_format}

            response = await self._make_request("POST", url, data=data, files=files)
        else:
            # 使用 URL
            data = {"pdfUrl": pdf_url, "exportFormat": export_format}
            response = await self._make_request("POST", url, data=data)

        result = response.json()

        if result.get("flag") != "success":
            error_msg = result.get("desc", "Unknown error")
            raise OCRError(f"Failed to create PDF OCR task: {error_msg}")

        return result.get("data", {})

    async def _query_task_status(self, task_no: str) -> dict[str, Any]:
        """查询任务状态."""
        url = f"{self.config.base_url}/status"
        params = {"taskNo": task_no}

        response = await self._make_request("GET", url, params=params)
        result = response.json()

        if result.get("flag") != "success":
            error_msg = result.get("desc", "Unknown error")
            raise OCRError(f"Failed to query task status: {error_msg}")

        return result.get("data", {})

    async def _poll_task_completion(self, task_no: str) -> dict[str, Any]:
        """轮询任务直到完成."""
        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self.max_poll_time:
                raise OCRError(f"Task polling timeout after {self.max_poll_time} seconds")

            task_data = await self._query_task_status(task_no)
            status = task_data.get("status")

            logger.info(f"Task {task_no} status: {status}")

            if status == "completed":
                return task_data
            elif status == "failed":
                raise OCRError(f"Task {task_no} failed")

            # 等待后继续轮询
            await asyncio.sleep(self.poll_interval)

    async def recognize(
        self, file: Optional[UploadFile] = None, pdf_url: Optional[str] = None, export_format: str = "json"
    ) -> PDFOCRResponse:
        """
        识别 PDF 文档.

        Args:
            file: 上传的 PDF 文件
            pdf_url: PDF 文件的公网 URL
            export_format: 导出格式 (word, markdown, json)

        Returns:
            PDFOCRResponse: 识别结果

        Raises:
            OCRError: 识别失败时抛出
        """
        try:
            # 创建任务
            task_data = await self._create_task(file, pdf_url, export_format)
            task_no = task_data.get("taskNo")

            if not task_no:
                raise OCRError("Failed to get task number from response")

            logger.info(f"Created PDF OCR task: {task_no}")

            # 轮询任务完成
            completed_data = await self._poll_task_completion(task_no)

            # 构建响应
            response = PDFOCRResponse(
                task_no=task_no,
                status=completed_data.get("status", "unknown"),
                page_count=completed_data.get("pageCount", 0),
                result_url=completed_data.get("downloadUrl"),
            )

            logger.info(f"PDF OCR task {task_no} completed with {response.page_count} pages")
            return response

        except Exception as e:
            logger.error(f"PDF OCR processing failed: {e}")
            raise
