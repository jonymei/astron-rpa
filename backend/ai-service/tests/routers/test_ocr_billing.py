from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.models.point import PointAllocation, PointTransaction, PointTransactionType
from app.routers import ocr as ocr_router
from app.schemas.ocr import (
    DocumentOCRResponse,
    DocumentOCRResponseHeader,
    DocumentOCRResponsePayload,
    DocumentOCRResponseResult,
)
from app.utils.ocr.base import OCRError


async def _seed_monthly_grant(session, user_id: str, amount: int = 1000):
    allocation = PointAllocation(
        user_id=user_id,
        initial_amount=amount,
        remaining_amount=amount,
        allocation_type=PointTransactionType.MONTHLY_GRANT.value,
        priority=50,
        expires_at=datetime.now(UTC) + timedelta(days=30),
        description="test monthly grant",
    )
    session.add(allocation)
    await session.flush()


async def _xfyun_cost_count(session, user_id: str) -> int:
    result = await session.execute(
        select(PointTransaction).where(
            PointTransaction.user_id == user_id,
            PointTransaction.transaction_type == PointTransactionType.XFYUN_COST.value,
        )
    )
    return len(result.scalars().all())


@pytest.mark.asyncio
async def test_bank_card_billable_failure_deducts_points(client, test_get_db):
    user_id = "ocr-billable-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_recognize(self, file):
        raise OCRError("fail to recognize", should_deduct_points=True, status_code=400, code="101")

    original = ocr_router.BankCardOCRClient.recognize
    ocr_router.BankCardOCRClient.recognize = fake_recognize
    try:
        response = await client.post(
            "/ocr/bank-card",
            headers={"X-User-Id": user_id},
            files={"file": ("test.jpg", b"fake-image", "image/jpeg")},
        )
    finally:
        ocr_router.BankCardOCRClient.recognize = original

    after = await _xfyun_cost_count(test_get_db, user_id)

    assert response.status_code == 400
    assert after == before + 1


@pytest.mark.asyncio
async def test_vat_invoice_non_billable_failure_does_not_deduct_points(client, test_get_db):
    user_id = "ocr-non-billable-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_recognize(self, file):
        raise OCRError("illegal image format", should_deduct_points=False, status_code=400, code="40204")

    original = ocr_router.VATInvoiceOCRClient.recognize
    ocr_router.VATInvoiceOCRClient.recognize = fake_recognize
    try:
        response = await client.post(
            "/ocr/vat-invoice",
            headers={"X-User-Id": user_id},
            files={"file": ("test.jpg", b"fake-image", "image/jpeg")},
        )
    finally:
        ocr_router.VATInvoiceOCRClient.recognize = original

    after = await _xfyun_cost_count(test_get_db, user_id)

    assert response.status_code == 400
    assert after == before


@pytest.mark.asyncio
async def test_document_success_deducts_points(client, test_get_db):
    user_id = "ocr-success-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_recognize(self, image_base64, encoding="jpg", output_level=1, output_format="markdown"):
        return DocumentOCRResponse(
            header=DocumentOCRResponseHeader(code=0, message="success", sid="test-sid"),
            payload=DocumentOCRResponsePayload(
                result=DocumentOCRResponseResult(
                    compress="raw",
                    encoding="utf8",
                    format="plain",
                    text="dGVzdA==",
                )
            ),
        )

    original = ocr_router.DocumentOCRClient.recognize
    ocr_router.DocumentOCRClient.recognize = fake_recognize
    try:
        response = await client.post(
            "/ocr/document",
            headers={"X-User-Id": user_id},
            json={"image": "dGVzdA==", "encoding": "jpg", "output_level": 1, "output_format": "json"},
        )
    finally:
        ocr_router.DocumentOCRClient.recognize = original

    after = await _xfyun_cost_count(test_get_db, user_id)

    assert response.status_code == 200
    assert after == before + 1
