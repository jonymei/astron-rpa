"""OCR utilities package for XunFei OCR services."""

from app.utils.ocr.document_ocr import DocumentOCRClient
from app.utils.ocr.pdf_ocr import PDFOCRClient

__all__ = ["DocumentOCRClient", "PDFOCRClient"]
