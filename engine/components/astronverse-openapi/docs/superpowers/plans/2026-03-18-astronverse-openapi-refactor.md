# astronverse-openapi 重构实施计划

**日期**: 2026-03-18
**状态**: 待实施
**预计时间**: 约 2-3 小时

## 概述

本计划将 astronverse-openapi 从混乱的单文件结构重构为按能力分类的模块化架构，统一通过本地网关访问 ai-service，完整暴露 9 种 OCR 能力，并保持向后兼容。

## 原则

- **TDD**: 先写测试，再实现功能
- **DRY**: 提取公共逻辑，避免重复代码
- **YAGNI**: 只实现规范要求的功能，不过度设计

## 任务列表

### 任务 1: 扩展 GatewayClient 支持 multipart/form-data

**预计时间**: 5 分钟

**目标**: 为 GatewayClient 新增 `post_multipart` 方法，支持文件上传。

**步骤**:

1. 打开 `src/astronverse/openapi/client.py`
2. 在 `post` 方法后追加 `post_multipart` 方法

**代码**:

```python
@staticmethod
def post_multipart(
    path: str,
    file_bytes: bytes,
    filename: str,
    extra_fields: dict | None = None,
) -> dict:
    url = f"{GatewayClient._gateway_base_url()}{path}"
    files = {"file": (filename, file_bytes)}
    data = extra_fields or {}
    response = requests.post(url, files=files, data=data)
    if response.status_code != 200:
        raise BaseException(AI_SERVER_ERROR, f"ai服务器无响应或错误: {response.text}")
    return response.json()
```

**验证**: 运行 `pytest tests/test_gateway_client.py -v`

---

### 任务 2: 创建目录结构

**预计时间**: 3 分钟

**目标**: 创建 `speech/` 和 `ocr/` 子目录及各模块文件骨架。

**步骤**:

1. 在 `src/astronverse/openapi/` 下创建以下文件（内容为空的 `__init__.py`）：
   - `speech/__init__.py`
   - `speech/asr.py`
   - `speech/transcription.py`
   - `speech/tts.py`
   - `ocr/__init__.py`
   - `ocr/general.py`
   - `ocr/document.py`
   - `ocr/pdf.py`
   - `ocr/ticket.py`
   - `ocr/id_card.py`
   - `ocr/bank_card.py`
   - `ocr/business_card.py`
   - `ocr/business_license.py`
   - `ocr/vat_invoice.py`
   - `ocr/_common.py`

2. 在 `tests/` 下创建 `tests/ocr/` 目录及 `__init__.py`

**验证**: `ls src/astronverse/openapi/speech/ src/astronverse/openapi/ocr/` 确认目录存在

---

### 任务 3: 迁移语音能力到 speech/ 子模块

**预计时间**: 10 分钟

**目标**: 将 `openapi.py` 中的语音函数移动到 `speech/` 子模块，逻辑不变。

**步骤**:

1. 从 `openapi.py` 中提取 `speech_asr_zh`、`speech_asr_multilingual` 到 `speech/asr.py`
2. 提取 `speech_transcribe_audio` 到 `speech/transcription.py`
3. 提取 `speech_tts_ultra_human` 到 `speech/tts.py`
4. 在 `speech/__init__.py` 中导出所有语音函数

**speech/__init__.py 内容**:

```python
from astronverse.openapi.speech.asr import speech_asr_zh, speech_asr_multilingual
from astronverse.openapi.speech.transcription import speech_transcribe_audio
from astronverse.openapi.speech.tts import speech_tts_ultra_human

__all__ = [
    "speech_asr_zh",
    "speech_asr_multilingual",
    "speech_transcribe_audio",
    "speech_tts_ultra_human",
]
```

**验证**: 运行 `pytest tests/test_speech_openapi.py -v` 确认现有测试通过

---

### 任务 4: 实现 OCR 通用模式能力（general, id_card, bank_card, business_card, business_license, vat_invoice）

**预计时间**: 30 分钟

**目标**: 实现 6 种通用模式 OCR 能力，统一走 multipart 路径。

**步骤**:

1. 先写测试 `tests/ocr/test_ocr_general.py`（mock GatewayClient）
2. 实现 `ocr/general.py`
3. 对其余 5 种能力重复上述步骤

**公共辅助函数**（放在 `ocr/_common.py`）:

```python
import os
from astronverse.actionlib.types import PATH
from astronverse.openapi import utils
from astronverse.openapi.client import GatewayClient
from astronverse.openapi.error import BaseException, IMAGE_EMPTY


def _read_image_bytes(src_file: str) -> tuple[str, bytes]:
    """读取单个图像文件，返回 (filename, bytes)"""
    files = utils.generate_src_files(src_file)  # file_type="image" 默认
    if not files:
        raise BaseException(IMAGE_EMPTY, "图像路径不存在或格式错误")
    path = files[0]
    with open(path, "rb") as f:
        return os.path.basename(path), f.read()


def _collect_dir_files(src_dir: str) -> list[str]:
    """收集文件夹中的所有图像文件"""
    files = utils.generate_src_files(src_dir)  # 传入目录时自动过滤图像
    if not files:
        raise BaseException(IMAGE_EMPTY, "图像文件夹不存在或为空")
    return files


def _run_multipart_ocr(
    api_path: str,
    is_multi: bool,
    src_file: PATH,
    src_dir: PATH,
    is_save: bool,
    dst_file: PATH,
    dst_file_name: str,
    extra_fields: dict | None = None,
) -> list:
    file_paths = _collect_dir_files(src_dir) if is_multi else None
    if not is_multi:
        fname, fbytes = _read_image_bytes(src_file)
        file_paths = [(fname, fbytes)]
    else:
        file_paths = [(os.path.basename(fp), open(fp, "rb").read()) for fp in file_paths]

    results = []
    for fname, fbytes in file_paths:
        resp = GatewayClient.post_multipart(api_path, fbytes, fname, extra_fields)
        results.append(resp)

    if is_save and results:
        utils.write_to_excel(dst_file, dst_file_name, {}, results)

    return results
```

**ocr/general.py 示例**:

```python
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import PATH
from astronverse.openapi.ocr._common import _run_multipart_ocr


def ocr_general(
    is_multi: bool = False,
    src_file: PATH = "",
    src_dir: PATH = "",
    is_save: bool = True,
    dst_file: PATH = "",
    dst_file_name: str = "general_ocr",
) -> list:
    return _run_multipart_ocr(
        "/ocr/general",
        is_multi, src_file, src_dir,
        is_save, dst_file, dst_file_name,
    )
```

**测试示例** (`tests/ocr/test_ocr_general.py`):

```python
from unittest.mock import patch, MagicMock
import pytest
from astronverse.openapi.ocr.general import ocr_general


@patch("astronverse.openapi.ocr._common.GatewayClient.post_multipart")
def test_ocr_general_single(mock_post):
    mock_post.return_value = {"payload": {"words": "测试文字"}}
    result = ocr_general(src_file="/fake/image.jpg", is_save=False)
    assert len(result) == 1
    mock_post.assert_called_once()


@patch("astronverse.openapi.ocr._common.GatewayClient.post_multipart")
def test_ocr_general_raises_on_empty_file(mock_post):
    with pytest.raises(Exception):
        ocr_general(src_file="", is_save=False)
```

**验证**: `pytest tests/ocr/test_ocr_general.py tests/ocr/test_ocr_id_card.py -v`

---

### 任务 5: 实现 OCR 票据识别（ticket）

**预计时间**: 10 分钟

**目标**: 实现 `ocr_ticket`，支持 `ticket_type` 参数区分票据类型。

**步骤**:

1. 先写测试 `tests/ocr/test_ocr_ticket.py`
2. 实现 `ocr/ticket.py`

**ocr/ticket.py**:

```python
from astronverse.actionlib.types import PATH
from astronverse.openapi.ocr._common import _run_multipart_ocr


def ocr_ticket(
    ticket_type: str = "train_ticket",
    is_multi: bool = False,
    src_file: PATH = "",
    src_dir: PATH = "",
    is_save: bool = True,
    dst_file: PATH = "",
    dst_file_name: str = "ticket_ocr",
) -> list:
    return _run_multipart_ocr(
        "/ocr/ticket",
        is_multi, src_file, src_dir,
        is_save, dst_file, dst_file_name,
        extra_fields={"ticket_type": ticket_type},
    )
```

**测试示例** (`tests/ocr/test_ocr_ticket.py`):

```python
from unittest.mock import patch
from astronverse.openapi.ocr.ticket import ocr_ticket


@patch("astronverse.openapi.ocr._common.GatewayClient.post_multipart")
def test_ocr_ticket_train(mock_post):
    mock_post.return_value = {"payload": {"ticket_no": "G1234"}}
    result = ocr_ticket(ticket_type="train_ticket", src_file="/fake/ticket.jpg", is_save=False)
    assert len(result) == 1
    _, kwargs = mock_post.call_args
    # extra_fields 是第 4 个位置参数
    call_args = mock_post.call_args
    assert call_args.args[3]["ticket_type"] == "train_ticket"
```

**验证**: `pytest tests/ocr/test_ocr_ticket.py -v`

---

### 任务 6: 实现 OCR 文档识别（document）

**预计时间**: 10 分钟

**目标**: 实现 `ocr_document`，走 JSON 路径，解析 base64 编码的响应。

**步骤**:

1. 先写测试 `tests/ocr/test_ocr_document.py`
2. 实现 `ocr/document.py`

**ocr/document.py**:

```python
import base64
import json
import os

from astronverse.actionlib.types import PATH
from astronverse.openapi import utils
from astronverse.openapi.client import GatewayClient
from astronverse.openapi.error import BaseException, IMAGE_EMPTY


def ocr_document(
    src_file: PATH = "",
    output_format: str = "markdown",
    output_level: int = 1,
    is_save: bool = True,
    dst_file: PATH = "",
    dst_file_name: str = "document_ocr",
) -> dict:
    files = utils.generate_src_files(src_file)  # file_type="image" 默认，过滤图像格式
    if not files:
        raise BaseException(IMAGE_EMPTY, "文件路径不存在或格式错误")

    with open(files[0], "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    resp = GatewayClient.post(
        "/ocr/document",
        {"image": image_b64, "output_format": output_format, "output_level": output_level},
    )

    raw_b64 = resp["payload"]["result"]["text"]
    raw_str = base64.b64decode(raw_b64).decode("utf-8")
    raw = json.loads(raw_str)
    text = raw.get("text", raw_str)

    saved_file = ""
    if is_save:
        saved_file = utils.write_text_file(dst_file, dst_file_name, text, suffix=".txt")

    return {"text": text, "raw": raw, "saved_file": saved_file}
```

**测试示例** (`tests/ocr/test_ocr_document.py`):

```python
import base64
import json
from unittest.mock import patch
from astronverse.openapi.ocr.document import ocr_document


@patch("astronverse.openapi.ocr.document.GatewayClient.post")
def test_ocr_document_parses_base64(mock_post):
    raw = {"text": "识别内容", "pages": 1}
    encoded = base64.b64encode(json.dumps(raw).encode()).decode()
    mock_post.return_value = {"payload": {"result": {"text": encoded}}}

    result = ocr_document(src_file="/fake/doc.jpg", is_save=False)

    assert result["text"] == "识别内容"
    assert result["raw"]["pages"] == 1
    assert result["saved_file"] == ""
```

**验证**: `pytest tests/ocr/test_ocr_document.py -v`

---

### 任务 7: 实现 OCR PDF 识别（pdf）

**预计时间**: 10 分钟

**目标**: 实现 `ocr_pdf`，支持本地文件和公网 URL，走 multipart 路径，返回异步任务信息。

**步骤**:

1. 先写测试 `tests/ocr/test_ocr_pdf.py`
2. 实现 `ocr/pdf.py`

**ocr/pdf.py**:

```python
import os
from astronverse.actionlib.types import PATH
from astronverse.openapi.client import GatewayClient
from astronverse.openapi.error import BaseException, IMAGE_EMPTY


def ocr_pdf(
    src_file: PATH = "",
    pdf_url: str = "",
    export_format: str = "json",
    dst_file: PATH = "",
    dst_file_name: str = "pdf_ocr",
) -> dict:
    if pdf_url:
        resp = GatewayClient.post(
            "/ocr/pdf",
            {"pdf_url": pdf_url, "export_format": export_format},
        )
    elif src_file:
        with open(src_file, "rb") as f:
            file_bytes = f.read()
        resp = GatewayClient.post_multipart(
            "/ocr/pdf",
            file_bytes,
            os.path.basename(src_file),
            extra_fields={"export_format": export_format},
        )
    else:
        raise BaseException(IMAGE_EMPTY, "src_file 和 pdf_url 不能同时为空")

    payload = resp.get("payload", {})
    return {
        "task_no": payload.get("task_no", ""),
        "status": payload.get("status", ""),
        "page_count": payload.get("page_count", 0),
        "result_url": payload.get("result_url", ""),
    }
```

**测试示例** (`tests/ocr/test_ocr_pdf.py`):

```python
from unittest.mock import patch
import pytest
from astronverse.openapi.ocr.pdf import ocr_pdf


@patch("astronverse.openapi.ocr.pdf.GatewayClient.post")
def test_ocr_pdf_with_url(mock_post):
    mock_post.return_value = {
        "payload": {"task_no": "T001", "status": "done", "page_count": 5, "result_url": "http://x.com/r"}
    }
    result = ocr_pdf(pdf_url="http://example.com/test.pdf")
    assert result["task_no"] == "T001"
    assert result["page_count"] == 5


def test_ocr_pdf_raises_when_no_input():
    with pytest.raises(Exception):
        ocr_pdf()
```

**验证**: `pytest tests/ocr/test_ocr_pdf.py -v`

---

### 任务 8: 删除 core_iflytek.py

**预计时间**: 3 分钟

**目标**: 删除直连讯飞的代码，并清理 `openapi.py` 中的引用。

**步骤**:

1. 确认 `openapi.py` 中 `from astronverse.openapi.core_iflytek import OpenapiIflytek` 的所有使用点已被替换
2. 删除 `src/astronverse/openapi/core_iflytek.py`
3. 删除 `openapi.py` 中的 import 行

**验证**: `python -c "from astronverse.openapi import OpenApi"` 无报错

---

### 任务 9: 更新 config.yaml

**预计时间**: 10 分钟

**目标**: 按规范补充 OCR 能力的 config.yaml 配置，新增 options 节点。

**步骤**:

1. 打开 `config.yaml`，在 `atomic:` 节点下，语音配置之后追加 OCR 配置
2. 在 `options:` 节点下追加 `ticket_type`、`output_format`、`export_format` 选项

**新增 options 内容**:

```yaml
options:
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
```

**验证**: `python -c "from astronverse.actionlib.atomic import atomicMg; print(atomicMg.cfg())"` 无报错

---

### 任务 10: 添加 deprecated 别名

**预计时间**: 5 分钟

**目标**: 在 `ocr/__init__.py` 中为旧函数名提供 deprecated 别名，保持向后兼容。

**步骤**:

1. 在 `ocr/__init__.py` 末尾追加 deprecated 别名代码

**ocr/__init__.py 完整内容**:

```python
from astronverse.openapi.ocr.general import ocr_general
from astronverse.openapi.ocr.document import ocr_document
from astronverse.openapi.ocr.pdf import ocr_pdf
from astronverse.openapi.ocr.ticket import ocr_ticket
from astronverse.openapi.ocr.id_card import ocr_id_card
from astronverse.openapi.ocr.bank_card import ocr_bank_card
from astronverse.openapi.ocr.business_card import ocr_business_card
from astronverse.openapi.ocr.business_license import ocr_business_license
from astronverse.openapi.ocr.vat_invoice import ocr_vat_invoice

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


id_card = _deprecated("id_card", ocr_id_card)
business_license = _deprecated("business_license", ocr_business_license)
vat_invoice = _deprecated("vat_invoice", ocr_vat_invoice)
common_ocr = _deprecated("common_ocr", ocr_general)


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


__all__ = [
    "ocr_general", "ocr_document", "ocr_pdf", "ocr_ticket",
    "ocr_id_card", "ocr_bank_card", "ocr_business_card",
    "ocr_business_license", "ocr_vat_invoice",
    # deprecated
    "id_card", "business_license", "vat_invoice", "common_ocr",
    "train_ticket", "taxi_ticket",
]
```

**验证**: 运行以下代码确认 deprecated 警告正常触发：

```python
import warnings
warnings.simplefilter("always")
from astronverse.openapi import OpenApi
OpenApi.common_ocr(src_file="/fake/img.jpg")  # 应触发 DeprecationWarning
```

---

### 任务 11: 更新顶层 __init__.py 导出

**预计时间**: 5 分钟

**目标**: 更新 `src/astronverse/openapi/__init__.py`，将 speech/ 和 ocr/ 的所有函数挂载到 `OpenApi` 命名空间。

**步骤**:

1. 读取当前 `__init__.py` 内容
2. 在 `OpenApi` 类中导入 speech 和 ocr 子模块的所有函数

**__init__.py 关键修改**:

```python
from astronverse.openapi.speech import (
    speech_asr_zh,
    speech_asr_multilingual,
    speech_transcribe_audio,
    speech_tts_ultra_human,
)
from astronverse.openapi.ocr import (
    ocr_general, ocr_document, ocr_pdf, ocr_ticket,
    ocr_id_card, ocr_bank_card, ocr_business_card,
    ocr_business_license, ocr_vat_invoice,
    # deprecated aliases
    id_card, business_license, vat_invoice, common_ocr,
    train_ticket, taxi_ticket,
)


class OpenApi:
    speech_asr_zh = staticmethod(speech_asr_zh)
    speech_asr_multilingual = staticmethod(speech_asr_multilingual)
    speech_transcribe_audio = staticmethod(speech_transcribe_audio)
    speech_tts_ultra_human = staticmethod(speech_tts_ultra_human)

    ocr_general = staticmethod(ocr_general)
    ocr_document = staticmethod(ocr_document)
    ocr_pdf = staticmethod(ocr_pdf)
    ocr_ticket = staticmethod(ocr_ticket)
    ocr_id_card = staticmethod(ocr_id_card)
    ocr_bank_card = staticmethod(ocr_bank_card)
    ocr_business_card = staticmethod(ocr_business_card)
    ocr_business_license = staticmethod(ocr_business_license)
    ocr_vat_invoice = staticmethod(ocr_vat_invoice)

    # deprecated
    id_card = staticmethod(id_card)
    business_license = staticmethod(business_license)
    vat_invoice = staticmethod(vat_invoice)
    common_ocr = staticmethod(common_ocr)
    train_ticket = staticmethod(train_ticket)
    taxi_ticket = staticmethod(taxi_ticket)
```

**验证**: `python -c "from astronverse.openapi import OpenApi; print(dir(OpenApi))"` 确认所有方法可见

---

### 任务 12: 更新测试

**预计时间**: 15 分钟

**目标**: 补充 `tests/ocr/` 目录下所有 OCR 能力的测试，确保覆盖正常路径和错误路径。

**步骤**:

1. 创建 `tests/ocr/__init__.py`（空文件）
2. 为每种 OCR 能力创建测试文件（参考任务 4-7 中的测试示例）
3. 确认现有语音测试仍然通过

**测试文件清单**:

| 文件 | 覆盖能力 |
|---|---|
| `tests/ocr/test_ocr_general.py` | ocr_general |
| `tests/ocr/test_ocr_id_card.py` | ocr_id_card |
| `tests/ocr/test_ocr_bank_card.py` | ocr_bank_card |
| `tests/ocr/test_ocr_business_card.py` | ocr_business_card |
| `tests/ocr/test_ocr_business_license.py` | ocr_business_license |
| `tests/ocr/test_ocr_vat_invoice.py` | ocr_vat_invoice |
| `tests/ocr/test_ocr_ticket.py` | ocr_ticket（含 deprecated train_ticket/taxi_ticket） |
| `tests/ocr/test_ocr_document.py` | ocr_document |
| `tests/ocr/test_ocr_pdf.py` | ocr_pdf |

**全量验证命令**:

```bash
pytest tests/ -v --tb=short
```

---

## 提交步骤

完成所有任务后，按以下顺序提交：

```bash
# 1. 确认所有测试通过
pytest tests/ -v

# 2. 暂存所有变更
git add src/astronverse/openapi/client.py
git add src/astronverse/openapi/speech/
git add src/astronverse/openapi/ocr/
git add src/astronverse/openapi/__init__.py
git add tests/ocr/
git add config.yaml

# 3. 删除旧文件
git rm src/astronverse/openapi/core_iflytek.py

# 4. 提交
git commit -m "refactor(openapi): 按能力分类重构，统一走网关，完整暴露9种OCR能力"
```

---

## 风险与注意事项

1. **openapi.py 清理**: 迁移完成后，`openapi.py` 中的旧 OCR 函数需要全部删除，避免重复定义
2. **utils.save_to_excel / utils.save_text**: 实现前先确认 `utils.py` 中已有对应方法，若无则需新增
3. **atomicMg.atomic 装饰器**: 迁移语音函数时，装饰器参数需完整复制，不能遗漏
4. **集成测试**: 任务 4-7 的测试均为 mock 测试，集成测试需要本地网关运行，参考 `tests/test_speech_via_gateway.py` 模式
