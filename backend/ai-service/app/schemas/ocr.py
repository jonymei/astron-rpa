from typing import Optional

from pydantic import BaseModel, Field


class OCRGeneralRequestBody(BaseModel):
    encoding: str = Field(
        "jpg",
        description="图像编码，jpg格式(默认值)/jpeg格式/png格式/bmp格式",
        examples=["jpg"],
    )
    status: int = Field(3, description="上传数据状态，可选值：3（一次传完）", examples=[3])
    image: str = Field(
        ...,
        description="图像数据，需保证图像文件大小base64编码后不超过4MB",
        examples=["iVBORw0KGgoAAAANSUhEUgAA..."],
    )


class OCRGeneralResponseInnerHeader(BaseModel):
    code: int = Field(..., description="返回码，0表示成功，非0表示失败", examples=[0])
    message: str = Field(..., description="返回信息", examples=["success"])
    sid: str = Field(..., description="会话唯一标识", examples=["ase000fa8ab@hu196fbeb910905c4882"])


class OCRGeneralResponseInnerResult(BaseModel):
    compress: str = Field(..., description="文本压缩格式", examples=["raw"])
    encoding: str = Field(..., description="文本编码格式", examples=["utf8"])
    format: str = Field(..., description="文本格式", examples=["json"])
    text: str = Field(
        ...,
        description="返回的文本数据， 需要对其进行base64解码",
        examples=["fQogXQp9Cg=="],
    )


class OCRGeneralResponseInnerPayload(BaseModel):
    result: OCRGeneralResponseInnerResult


class OCRGeneralResponseBody(BaseModel):
    header: OCRGeneralResponseInnerHeader
    payload: Optional[OCRGeneralResponseInnerPayload]


# ============ Document OCR (OCR LLM) Schemas ============


class DocumentOCRRequest(BaseModel):
    image: str = Field(..., description="Base64 编码的图像数据", examples=["iVBORw0KGgoAAAANSUhEUgAA..."])
    encoding: str = Field("jpg", description="图像格式 (jpg, png, bmp)", examples=["jpg"])
    output_level: int = Field(1, description="输出级别 (1-3)", examples=[1])
    output_format: str = Field("markdown", description="输出格式 (markdown, json)", examples=["markdown"])


class DocumentOCRResponseHeader(BaseModel):
    code: int = Field(..., description="返回码，0表示成功", examples=[0])
    message: str = Field(..., description="返回信息", examples=["success"])
    sid: str = Field(..., description="会话唯一标识", examples=["ase000fa8ab@hu196fbeb910905c4882"])


class DocumentOCRResponseResult(BaseModel):
    compress: str = Field(..., description="文本压缩格式", examples=["raw"])
    encoding: str = Field(..., description="文本编码格式", examples=["utf8"])
    format: str = Field(..., description="文本格式", examples=["json"])
    text: str = Field(..., description="返回的文本数据，需要 base64 解码", examples=["fQogXQp9Cg=="])


class DocumentOCRResponsePayload(BaseModel):
    result: DocumentOCRResponseResult


class DocumentOCRResponse(BaseModel):
    header: DocumentOCRResponseHeader
    payload: Optional[DocumentOCRResponsePayload] = None


# ============ PDF OCR Schemas ============


class PDFOCRResponse(BaseModel):
    task_no: str = Field(..., description="任务编号", examples=["task_123456"])
    status: str = Field(..., description="任务状态 (completed, failed, processing)", examples=["completed"])
    page_count: int = Field(..., description="PDF 页数", examples=[10])
    result_url: Optional[str] = Field(None, description="结果下载链接", examples=["https://example.com/result.json"])


# ============ Ticket OCR Schemas ============


class TicketOCRRequest(BaseModel):
    ocr_type: str = Field(
        "air_itinerary",
        description="票据类型 (air_itinerary: 行程单, train_ticket: 火车票, taxi_receipt: 出租车票等)",
        examples=["air_itinerary"],
    )


class TicketOCRResponse(BaseModel):
    data: dict = Field(..., description="识别结果数据", examples=[{}])


# ============ Business Card OCR Schemas ============


class BusinessCardOCRResponse(BaseModel):
    code: str = Field(..., description="返回码，0表示成功", examples=["0"])
    desc: str = Field(..., description="返回描述", examples=["success"])
    data: dict = Field(..., description="名片识别结果", examples=[{}])
    sid: Optional[str] = Field(None, description="会话ID", examples=["abc123"])


# ============ ID Card OCR Schemas ============


class IDCardOCRResponse(BaseModel):
    code: str = Field(..., description="返回码，0表示成功", examples=["0"])
    desc: str = Field(..., description="返回描述", examples=["success"])
    data: dict = Field(..., description="身份证识别结果", examples=[{}])
    sid: Optional[str] = Field(None, description="会话ID", examples=["abc123"])


# ============ Bank Card OCR Schemas ============


class BankCardOCRResponse(BaseModel):
    code: str = Field(..., description="返回码，0表示成功", examples=["0"])
    desc: str = Field(..., description="返回描述", examples=["success"])
    data: dict = Field(..., description="银行卡识别结果", examples=[{}])
    sid: Optional[str] = Field(None, description="会话ID", examples=["abc123"])


# ============ Business License OCR Schemas ============


class BusinessLicenseOCRResponse(BaseModel):
    code: str = Field(..., description="返回码，0表示成功", examples=["0"])
    desc: str = Field(..., description="返回描述", examples=["success"])
    data: dict = Field(..., description="营业执照识别结果", examples=[{}])
    sid: Optional[str] = Field(None, description="会话ID", examples=["abc123"])


# ============ VAT Invoice OCR Schemas ============


class VATInvoiceOCRResponse(BaseModel):
    code: str = Field(..., description="返回码，0表示成功", examples=["0"])
    desc: str = Field(..., description="返回描述", examples=["success"])
    data: dict = Field(..., description="增值税发票识别结果", examples=[{}])
    sid: Optional[str] = Field(None, description="会话ID", examples=["abc123"])

