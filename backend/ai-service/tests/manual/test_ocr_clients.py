"""Manual test script for OCR clients.

This script tests the OCR clients directly without going through the API routes.
Requires valid XunFei credentials in .env file.
"""

import asyncio
import base64
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.utils.ocr.document_ocr import DocumentOCRClient
from app.utils.ocr.pdf_ocr import PDFOCRClient


async def test_document_ocr():
    """Test document OCR with a sample image."""
    print("\n=== Testing Document OCR ===")

    # Load test image from assets
    test_image_path = os.path.join(os.path.dirname(__file__), "../assets/test.jpg")
    print(f"Loading test image from: {test_image_path}")

    with open(test_image_path, "rb") as f:
        test_image_bytes = f.read()
    test_image_base64 = base64.b64encode(test_image_bytes).decode("utf-8")
    print(f"Image size: {len(test_image_bytes)} bytes, base64 size: {len(test_image_base64)} chars")

    try:
        client = DocumentOCRClient()
        print(f"Client created with config: {client.config.service_name}")
        print(f"Auth type: {client.config.auth_type}")
        print(f"Base URL: {client.config.base_url}")

        print("\nSending request...")
        result = await client.recognize(test_image_base64, encoding="jpg")

        print(f"\nResponse received:")
        print(f"  Code: {result.header.code}")
        print(f"  Message: {result.header.message}")
        print(f"  SID: {result.header.sid}")

        if result.payload:
            print(f"  Result format: {result.payload.result.format}")
            print(f"  Result encoding: {result.payload.result.encoding}")
            # Decode the text
            decoded_text = base64.b64decode(result.payload.result.text).decode("utf-8")
            print(f"  Decoded text: {decoded_text[:200]}...")

        print("\n✅ Document OCR test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Document OCR test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_pdf_ocr():
    """Test PDF OCR with a sample PDF file."""
    print("\n=== Testing PDF OCR ===")

    # Load test PDF from assets
    test_pdf_path = os.path.join(os.path.dirname(__file__), "../assets/test.pdf")
    print(f"Loading test PDF from: {test_pdf_path}")

    try:
        client = PDFOCRClient()
        print(f"Client created with config: {client.config.service_name}")
        print(f"Auth type: {client.config.auth_type}")
        print(f"Base URL: {client.config.base_url}")
        print(f"Poll interval: {client.poll_interval}s")
        print(f"Max poll time: {client.max_poll_time}s")

        print("\nUploading PDF and creating task...")
        # Create a fake UploadFile object
        from io import BytesIO

        with open(test_pdf_path, "rb") as f:
            pdf_content = f.read()

        print(f"PDF size: {len(pdf_content)} bytes")

        # Create a simple file-like object
        class FakeUploadFile:
            def __init__(self, filename, content, content_type):
                self.filename = filename
                self.content = content
                self.content_type = content_type
                self._file = BytesIO(content)

            async def read(self):
                return self.content

        fake_file = FakeUploadFile("test.pdf", pdf_content, "application/pdf")

        result = await client.recognize(file=fake_file, export_format="json")

        print(f"\nResponse received:")
        print(f"  Task No: {result.task_no}")
        print(f"  Status: {result.status}")
        print(f"  Page Count: {result.page_count}")
        print(f"  Result URL: {result.result_url}")

        print("\n✅ PDF OCR test passed!")
        return True

    except Exception as e:
        print(f"\n❌ PDF OCR test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("OCR Clients Manual Test")
    print("=" * 60)

    results = []

    # Test Document OCR
    results.append(await test_document_ocr())

    # Test PDF OCR
    results.append(await test_pdf_ocr())

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")

    if all(results):
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
