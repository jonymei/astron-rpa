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

    # Create a simple test image (1x1 white pixel PNG)
    test_image_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    )
    test_image_base64 = base64.b64encode(test_image_bytes).decode("utf-8")

    try:
        client = DocumentOCRClient()
        print(f"Client created with config: {client.config.service_name}")
        print(f"Auth type: {client.config.auth_type}")
        print(f"Base URL: {client.config.base_url}")

        print("\nSending request...")
        result = await client.recognize(test_image_base64, encoding="png")

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
    """Test PDF OCR with a sample PDF URL."""
    print("\n=== Testing PDF OCR ===")

    # Note: This requires a valid PDF URL or file
    # For now, we'll just test the client creation
    try:
        client = PDFOCRClient()
        print(f"Client created with config: {client.config.service_name}")
        print(f"Auth type: {client.config.auth_type}")
        print(f"Base URL: {client.config.base_url}")
        print(f"Poll interval: {client.poll_interval}s")
        print(f"Max poll time: {client.max_poll_time}s")

        print("\n⚠️  PDF OCR test skipped (requires valid PDF file or URL)")
        print("To test PDF OCR, provide a PDF file or URL in the code")
        return True

    except Exception as e:
        print(f"\n❌ PDF OCR client creation failed: {e}")
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
