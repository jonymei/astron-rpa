"""Manual test script for new OCR clients."""

import asyncio
import base64
import os
import ssl
import sys
from pathlib import Path

# 设置SSL环境变量以兼容旧的SSL证书
os.environ["PYTHONHTTPSVERIFY"] = "0"
ssl._create_default_https_context = ssl._create_unverified_context

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.utils.ocr.bank_card_ocr import BankCardOCRClient
from app.utils.ocr.business_card_ocr import BusinessCardOCRClient
from app.utils.ocr.business_license_ocr import BusinessLicenseOCRClient
from app.utils.ocr.id_card_ocr import IDCardOCRClient
from app.utils.ocr.ticket_ocr import TicketOCRClient
from app.utils.ocr.vat_invoice_ocr import VATInvoiceOCRClient


class MockUploadFile:
    """Mock UploadFile for testing."""

    def __init__(self, filename: str, content: bytes, content_type: str):
        self.filename = filename
        self.content = content
        self.content_type = content_type

    async def read(self) -> bytes:
        return self.content


async def test_ticket_ocr():
    """测试票据卡证识别."""
    print("\n" + "=" * 50)
    print("Testing Ticket OCR...")
    print("=" * 50)

    try:
        # 读取测试图片
        test_image_path = Path(__file__).parent.parent / "assets" / "test.jpg"
        with open(test_image_path, "rb") as f:
            image_data = f.read()

        # 创建 mock file
        mock_file = MockUploadFile("test.jpg", image_data, "image/jpeg")

        # 测试识别
        client = TicketOCRClient()
        result = await client.recognize(file=mock_file, ocr_type="air_itinerary")

        print(f"✅ Ticket OCR test passed!")
        print(f"- Image size: {len(image_data) / 1024:.0f}KB")
        print(f"- Result keys: {list(result.keys())}")
        print(f"- Result preview: {str(result)[:200]}...")

        return True

    except Exception as e:
        print(f"❌ Ticket OCR test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_business_card_ocr():
    """测试名片识别."""
    print("\n" + "=" * 50)
    print("Testing Business Card OCR...")
    print("=" * 50)

    try:
        # 读取测试图片
        test_image_path = Path(__file__).parent.parent / "assets" / "test.jpg"
        with open(test_image_path, "rb") as f:
            image_data = f.read()

        # 创建 mock file
        mock_file = MockUploadFile("test.jpg", image_data, "image/jpeg")

        # 测试识别
        client = BusinessCardOCRClient()
        result = await client.recognize(mock_file)

        print(f"✅ Business Card OCR test passed!")
        print(f"- Image size: {len(image_data) / 1024:.0f}KB")
        print(f"- Result: {result}")

        return True

    except Exception as e:
        print(f"❌ Business Card OCR test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_id_card_ocr():
    """测试身份证识别."""
    print("\n" + "=" * 50)
    print("Testing ID Card OCR...")
    print("=" * 50)

    try:
        # 读取测试图片
        test_image_path = Path(__file__).parent.parent / "assets" / "test.jpg"
        with open(test_image_path, "rb") as f:
            image_data = f.read()

        # 创建 mock file
        mock_file = MockUploadFile("test.jpg", image_data, "image/jpeg")

        # 测试识别
        client = IDCardOCRClient()
        result = await client.recognize(mock_file)

        print(f"✅ ID Card OCR test passed!")
        print(f"- Image size: {len(image_data) / 1024:.0f}KB")
        print(f"- Result: {result}")

        return True

    except Exception as e:
        print(f"❌ ID Card OCR test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_bank_card_ocr():
    """测试银行卡识别."""
    print("\n" + "=" * 50)
    print("Testing Bank Card OCR...")
    print("=" * 50)

    try:
        # 读取测试图片
        test_image_path = Path(__file__).parent.parent / "assets" / "test.jpg"
        with open(test_image_path, "rb") as f:
            image_data = f.read()

        # 创建 mock file
        mock_file = MockUploadFile("test.jpg", image_data, "image/jpeg")

        # 测试识别
        client = BankCardOCRClient()
        result = await client.recognize(mock_file)

        print(f"✅ Bank Card OCR test passed!")
        print(f"- Image size: {len(image_data) / 1024:.0f}KB")
        print(f"- Result: {result}")

        return True

    except Exception as e:
        print(f"❌ Bank Card OCR test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_business_license_ocr():
    """测试营业执照识别."""
    print("\n" + "=" * 50)
    print("Testing Business License OCR...")
    print("=" * 50)

    try:
        # 读取测试图片
        test_image_path = Path(__file__).parent.parent / "assets" / "test.jpg"
        with open(test_image_path, "rb") as f:
            image_data = f.read()

        # 创建 mock file
        mock_file = MockUploadFile("test.jpg", image_data, "image/jpeg")

        # 测试识别
        client = BusinessLicenseOCRClient()
        result = await client.recognize(mock_file)

        print(f"✅ Business License OCR test passed!")
        print(f"- Image size: {len(image_data) / 1024:.0f}KB")
        print(f"- Result: {result}")

        return True

    except Exception as e:
        print(f"❌ Business License OCR test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_vat_invoice_ocr():
    """测试增值税发票识别."""
    print("\n" + "=" * 50)
    print("Testing VAT Invoice OCR...")
    print("=" * 50)

    try:
        # 读取测试图片
        test_image_path = Path(__file__).parent.parent / "assets" / "test.jpg"
        with open(test_image_path, "rb") as f:
            image_data = f.read()

        # 创建 mock file
        mock_file = MockUploadFile("test.jpg", image_data, "image/jpeg")

        # 测试识别
        client = VATInvoiceOCRClient()
        result = await client.recognize(mock_file)

        print(f"✅ VAT Invoice OCR test passed!")
        print(f"- Image size: {len(image_data) / 1024:.0f}KB")
        print(f"- Result: {result}")

        return True

    except Exception as e:
        print(f"❌ VAT Invoice OCR test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """运行所有测试."""
    print("\n" + "=" * 50)
    print("Starting New OCR Clients Tests")
    print("=" * 50)

    results = []

    # 运行所有测试
    results.append(("Ticket OCR", await test_ticket_ocr()))
    results.append(("Business Card OCR", await test_business_card_ocr()))
    results.append(("ID Card OCR", await test_id_card_ocr()))
    results.append(("Bank Card OCR", await test_bank_card_ocr()))
    results.append(("Business License OCR", await test_business_license_ocr()))
    results.append(("VAT Invoice OCR", await test_vat_invoice_ocr()))

    # 打印总结
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")

    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")

    if passed == total:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {total - passed} test(s) failed!")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
