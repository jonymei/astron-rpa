# astronverse-openapi 重构设计文档

**日期**: 2026-03-18
**状态**: 待实施

## 背景

当前 `astronverse-openapi` 存在以下问题：

1. OCR 能力混乱：部分直连讯飞 API（`core_iflytek.py`），部分走本地网关，两套路径并存
2. 能力不完整：后端 ai-service 已有 9 种 OCR 能力，前端只暴露了 6 种，且对应关系不一致
3. 代码组织差：所有能力堆在单个 `openapi.py` 文件（760 行），语音和 OCR 混在一起
4. 无法扩展：后续新增 NLP 等分类没有清晰的组织位置

## 目标

- 所有能力统一通过本地网关（`127.0.0.1:13159`）代理访问 ai-service
- OCR 能力与后端对齐，完整暴露 9 种能力
- 按能力分类组织代码，便于维护和扩展
- 保持向后兼容，旧函数名提供 deprecated 别名

---

## 目录结构

```
engine/components/astronverse-openapi/
├── config.yaml
├── meta.py
├── pyproject.toml
└── src/astronverse/openapi/
    ├── __init__.py          # 统一导出 OpenApi 命名空间
    ├── client.py            # GatewayClient（不变）
    ├── error.py             # 错误码（不变）
    ├── utils.py             # 文件工具（不变）
    ├── speech/
    │   ├── __init__.py      # 导出语音能力到 OpenApi 命名空间
    │   ├── asr.py           # speech_asr_zh, speech_asr_multilingual
    │   ├── transcription.py # speech_transcribe_audio
    │   └── tts.py           # speech_tts_ultra_human
    └── ocr/
        ├── __init__.py      # 导出所有 OCR 能力到 OpenApi 命名空间
        ├── general.py       # ocr_general（通用文字识别）
        ├── document.py      # ocr_document（文档识别，OCR大模型）
        ├── pdf.py           # ocr_pdf（PDF识别，按页计费）
        ├── ticket.py        # ocr_ticket（票据识别，统一入口）
        ├── id_card.py       # ocr_id_card（身份证）
        ├── bank_card.py     # ocr_bank_card（银行卡）
        ├── business_card.py # ocr_business_card（名片）
        ├── business_license.py # ocr_business_license（营业执照）
        └── vat_invoice.py   # ocr_vat_invoice（增值税发票）
```

**删除**：`core_iflytek.py`（直连讯飞的代码全部移除）

---

## 数据流

后端接口分两种传输格式，`GatewayClient` 需要支持两条路径：

**JSON 路径**（`general`、`document`）：
```
用户调用 → 读取文件 → base64 编码
    ↓
GatewayClient.post(path, {"image": base64, ...})  # JSON body
    ↓
http://127.0.0.1:{GATEWAY_PORT}/api/rpa-ai-service/{path}
    ↓
返回 JSON → 解析 → 用户
```

**Multipart 路径**（`ticket`、`id-card`、`bank-card`、`business-card`、`business-license`、`vat-invoice`、`pdf`）：
```
用户调用 → 读取文件字节
    ↓
GatewayClient.post_multipart(path, file_bytes, filename, extra_fields)
    ↓
http://127.0.0.1:{GATEWAY_PORT}/api/rpa-ai-service/{path}  # multipart/form-data
    ↓
返回 JSON → 解析 → 用户
```

`GatewayClient` 需要新增 `post_multipart(path, file_bytes, filename, extra_fields=None)` 方法，使用 `requests` 的 `files` 参数发送。

---

## 能力清单与接口对应

| astronverse-openapi 函数 | ai-service 路由 | 说明 |
|---|---|---|
| `OpenApi.speech_asr_zh` | `POST /speech/asr/chinese` | 不变 |
| `OpenApi.speech_asr_multilingual` | `POST /speech/asr/multilingual` | 不变 |
| `OpenApi.speech_transcribe_audio` | `POST /speech/transcription` | 不变 |
| `OpenApi.speech_tts_ultra_human` | `POST /speech/tts` | 不变 |
| `OpenApi.ocr_general` | `POST /ocr/general` | 原 `common_ocr`，改名 |
| `OpenApi.ocr_document` | `POST /ocr/document` | 新增 |
| `OpenApi.ocr_pdf` | `POST /ocr/pdf` | 新增 |
| `OpenApi.ocr_ticket` | `POST /ocr/ticket` | 原 `train_ticket`+`taxi_ticket` 合并 |
| `OpenApi.ocr_id_card` | `POST /ocr/id-card` | 原 `id_card`，改名+改路由 |
| `OpenApi.ocr_bank_card` | `POST /ocr/bank-card` | 新增 |
| `OpenApi.ocr_business_card` | `POST /ocr/business-card` | 新增 |
| `OpenApi.ocr_business_license` | `POST /ocr/business-license` | 原 `business_license`，改名+改路由 |
| `OpenApi.ocr_vat_invoice` | `POST /ocr/vat-invoice` | 原 `vat_invoice`，改名+改路由 |

---

## 各能力参数设计

### OCR 通用模式（general / id_card / bank_card / business_card / business_license / vat_invoice）

```python
def ocr_xxx(
    is_multi: bool = False,
    src_file: PATH = "",       # is_multi=False 时使用
    src_dir: PATH = "",        # is_multi=True 时使用
    is_save: bool = True,
    dst_file: PATH = "",
    dst_file_name: str = "xxx_ocr",
) -> list
```

输出：识别结果列表，每项为 dict（字段名为中文）

### ocr_ticket（票据识别）

```python
def ocr_ticket(
    ticket_type: str = "train_ticket",  # train_ticket / taxi_receipt / air_itinerary
    is_multi: bool = False,
    src_file: PATH = "",
    src_dir: PATH = "",
    is_save: bool = True,
    dst_file: PATH = "",
    dst_file_name: str = "ticket_ocr",
) -> list
```

`ticket_type` 通过 config.yaml options 提供下拉选项。

### ocr_document（文档识别）

```python
def ocr_document(
    src_file: PATH = "",
    output_format: str = "markdown",   # markdown / json
    output_level: int = 1,             # 1-3
    is_save: bool = True,
    dst_file: PATH = "",
    dst_file_name: str = "document_ocr",
) -> dict
```

**说明**：文档识别为单文件模式，不支持批量处理（无 `is_multi` 参数）。

**响应解析**：
- 后端返回 `{"header": {...}, "payload": {"result": {"text": base64_str}}}`
- `text` 字段：从 `payload.result.text` base64 解码后得到 JSON 字符串，再解析为 dict
- `raw` 字段：解码后的完整 JSON 内容
- `saved_file` 字段：如果 `is_save=True`，保存到本地的文件路径

输出：`{"text": str, "raw": dict, "saved_file": str}`

### ocr_pdf（PDF识别）

```python
def ocr_pdf(
    src_file: PATH = "",       # 与 pdf_url 二选一
    pdf_url: str = "",         # 公网 URL
    export_format: str = "json",  # word / markdown / json
    dst_file: PATH = "",
    dst_file_name: str = "pdf_ocr",
) -> dict
```

**说明**：PDF 识别为异步任务，结果通过 `result_url` 下载，不支持 `is_save` 直接保存（结果是远程 URL，不是本地文件）。

输出：`{"task_no": str, "status": str, "page_count": int, "result_url": str}`
计费：按页数，10 积分/页（由 ai-service 处理）

---

## config.yaml 结构

顶层按 `speech` / `ocr` 分组，`atomic` 节点保持现有格式：

```yaml
atomic:
  # --- 语音 ---
  OpenApi.speech_asr_zh:
    title: 中文语音识别大模型
    # ... 现有配置不变

  OpenApi.speech_asr_multilingual:
    # ... 现有配置不变

  OpenApi.speech_transcribe_audio:
    # ... 现有配置不变

  OpenApi.speech_tts_ultra_human:
    # ... 现有配置不变

  # --- OCR ---
  OpenApi.ocr_general:
    title: 通用文字识别
    comment: 识别图片中的文字内容
    icon: general-text-recognition
    inputList:
      - key: is_multi
      - key: src_file
      - key: src_dir
      - key: is_save
      - key: dst_file
      - key: dst_file_name
    outputList:
      - key: ocr_general
        title: 通用文字识别结果

  OpenApi.ocr_document:
    title: 文档识别（OCR大模型）
    comment: 支持公式、图表、复杂排版的文档识别
    inputList:
      - key: src_file
      - key: output_format
      - key: output_level
      - key: is_save
      - key: dst_file
      - key: dst_file_name
    outputList:
      - key: text
      - key: raw

  OpenApi.ocr_pdf:
    title: PDF文档识别
    comment: 多页PDF识别，按页计费（10积分/页）
    inputList:
      - key: src_file
      - key: pdf_url
      - key: export_format
      - key: dst_file
      - key: dst_file_name
    outputList:
      - key: task_no
      - key: status
      - key: page_count
      - key: result_url

  OpenApi.ocr_ticket:
    title: 票据识别
    comment: 支持火车票、出租车票、行程单等多种票据
    inputList:
      - key: ticket_type
      - key: is_multi
      - key: src_file
      - key: src_dir
      - key: is_save
      - key: dst_file
      - key: dst_file_name
    outputList:
      - key: ocr_ticket

  OpenApi.ocr_id_card:
    title: 身份证识别
    comment: 识别身份证正反面信息
    icon: id-card-recognition
    helpManual: ''
    inputList:
      - key: is_multi
        title: 批量处理
        tip: 选择"否"处理单张，选择"是"按文件夹批量处理
      - key: src_file
        title: 图像文件
        tip: ''
      - key: src_dir
        title: 图像文件夹
        tip: ''
      - key: is_save
        title: 输出文档
        tip: 是否保存识别结果为 Excel 文档
      - key: dst_file
        title: 文档输出路径
        tip: ''
      - key: dst_file_name
        title: 文档输出文件名
        tip: ''
    outputList:
      - key: ocr_id_card
        title: 身份证识别结果
        tip: 输出身份证识别结果列表

  OpenApi.ocr_bank_card:
    title: 银行卡识别
    comment: 识别银行卡号、有效期等信息
    icon: bank-card-recognition
    helpManual: ''
    inputList:
      - key: is_multi
        title: 批量处理
        tip: 选择"否"处理单张，选择"是"按文件夹批量处理
      - key: src_file
        title: 图像文件
        tip: ''
      - key: src_dir
        title: 图像文件夹
        tip: ''
      - key: is_save
        title: 输出文档
        tip: 是否保存识别结果为 Excel 文档
      - key: dst_file
        title: 文档输出路径
        tip: ''
      - key: dst_file_name
        title: 文档输出文件名
        tip: ''
    outputList:
      - key: ocr_bank_card
        title: 银行卡识别结果
        tip: 输出银行卡识别结果列表

  OpenApi.ocr_business_card:
    title: 名片识别
    comment: 识别名片上的姓名、电话、邮箱等信息
    icon: business-card-recognition
    helpManual: ''
    inputList:
      - key: is_multi
        title: 批量处理
        tip: 选择"否"处理单张，选择"是"按文件夹批量处理
      - key: src_file
        title: 图像文件
        tip: ''
      - key: src_dir
        title: 图像文件夹
        tip: ''
      - key: is_save
        title: 输出文档
        tip: 是否保存识别结果为 Excel 文档
      - key: dst_file
        title: 文档输出路径
        tip: ''
      - key: dst_file_name
        title: 文档输出文件名
        tip: ''
    outputList:
      - key: ocr_business_card
        title: 名片识别结果
        tip: 输出名片识别结果列表

  OpenApi.ocr_business_license:
    title: 营业执照识别
    comment: 识别营业执照上的企业名称、注册号等信息
    icon: business-license-recognition
    helpManual: ''
    inputList:
      - key: is_multi
        title: 批量处理
        tip: 选择"否"处理单张，选择"是"按文件夹批量处理
      - key: src_file
        title: 图像文件
        tip: ''
      - key: src_dir
        title: 图像文件夹
        tip: ''
      - key: is_save
        title: 输出文档
        tip: 是否保存识别结果为 Excel 文档
      - key: dst_file
        title: 文档输出路径
        tip: ''
      - key: dst_file_name
        title: 文档输出文件名
        tip: ''
    outputList:
      - key: ocr_business_license
        title: 营业执照识别结果
        tip: 输出营业执照识别结果列表

  OpenApi.ocr_vat_invoice:
    title: 增值税发票识别
    comment: 识别增值税发票上的发票代码、金额等信息
    icon: vat-invoice-recognition
    helpManual: ''
    inputList:
      - key: is_multi
        title: 批量处理
        tip: 选择"否"处理单张，选择"是"按文件夹批量处理
      - key: src_file
        title: 图像文件
        tip: ''
      - key: src_dir
        title: 图像文件夹
        tip: ''
      - key: is_save
        title: 输出文档
        tip: 是否保存识别结果为 Excel 文档
      - key: dst_file
        title: 文档输出路径
        tip: ''
      - key: dst_file_name
        title: 文档输出文件名
        tip: ''
    outputList:
      - key: ocr_vat_invoice
        title: 增值税发票识别结果
        tip: 输出增值税发票识别结果列表

options:
  Bool:
    - value: true
      label: 是
    - value: false
      label: 否
  ticket_type:
    - value: train_ticket
      label: 火车票
    - value: taxi_receipt
      label: 出租车票
    - value: air_itinerary
      label: 行程单
  output_format:
    - value: markdown
      label: Markdown
    - value: json
      label: JSON
  export_format:
    - value: json
      label: JSON
    - value: markdown
      label: Markdown
    - value: word
      label: Word
  voice:
    # ... 现有配置不变
  audio_format:
    # ... 现有配置不变
  save_format:
    # ... 现有配置不变
```

---

## 向后兼容

在 `ocr/__init__.py` 中为旧函数名提供 deprecated 别名：

```python
import warnings

def _deprecated(old_name: str, new_fn):
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"OpenApi.{old_name} is deprecated, use OpenApi.{new_fn.__name__}",
            DeprecationWarning,
            stacklevel=2,
        )
        return new_fn(*args, **kwargs)
    return wrapper

# 旧名称 → 新名称（直接映射）
id_card = _deprecated("id_card", ocr_id_card)
business_license = _deprecated("business_license", ocr_business_license)
vat_invoice = _deprecated("vat_invoice", ocr_vat_invoice)
common_ocr = _deprecated("common_ocr", ocr_general)

# train_ticket / taxi_ticket → ocr_ticket（需要硬编码 ticket_type）
def train_ticket(*args, **kwargs):
    warnings.warn(
        "OpenApi.train_ticket is deprecated, use OpenApi.ocr_ticket with ticket_type='train_ticket'",
        DeprecationWarning,
        stacklevel=2,
    )
    kwargs.setdefault("ticket_type", "train_ticket")
    return ocr_ticket(*args, **kwargs)

def taxi_ticket(*args, **kwargs):
    warnings.warn(
        "OpenApi.taxi_ticket is deprecated, use OpenApi.ocr_ticket with ticket_type='taxi_receipt'",
        DeprecationWarning,
        stacklevel=2,
    )
    kwargs.setdefault("ticket_type", "taxi_receipt")
    return ocr_ticket(*args, **kwargs)
```

---

## 错误处理

所有能力统一处理以下错误：

- `AI_SERVER_ERROR`：网关返回非 200，抛出 `BaseException`
- 文件不存在/格式错误：抛出 `BaseException(IMAGE_EMPTY, ...)`
- 网络超时：由 `requests` 抛出，不捕获，让上层处理

---

## 测试策略

- 现有测试（`tests/test_speech_openapi.py` 等）继续有效
- 新增 `tests/ocr/` 目录，每种 OCR 能力对应一个测试文件
- 集成测试通过 `tests/test_speech_via_gateway.py` 模式，需要本地网关运行

---

## 迁移步骤

1. **扩展 GatewayClient**：新增 `post_multipart(path, file_bytes, filename, extra_fields=None)` 方法
2. **创建目录结构**：创建 `speech/` 和 `ocr/` 子目录
3. **迁移语音能力**：将现有语音函数从 `openapi.py` 迁移到 `speech/` 子模块（纯文件移动，逻辑不变）
4. **实现新增 OCR 能力**：`document`、`pdf`、`bank_card`、`business_card`
5. **改造旧 OCR 能力**：将 `id_card`、`business_license`、`vat_invoice`、`train_ticket`、`taxi_ticket`、`common_ocr` 改为走网关
6. **删除直连代码**：删除 `core_iflytek.py`
7. **更新 config.yaml**：按新结构补充配置
8. **添加 deprecated 别名**：在 `__init__.py` 中添加向后兼容代码
9. **更新测试**：新增 `tests/ocr/` 目录，补充测试用例
