# OCR 接口升级实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 PDF 文档识别和通用文档识别两个 OCR 大模型接口，建立配置驱动的统一基类架构

**Architecture:** 采用配置驱动的基类设计，通过 OCRConfig 定义 API 特性，AuthStrategy 实现认证策略，XFYunOCRClient 基类封装通用逻辑，具体客户端类继承基类实现业务逻辑

**Tech Stack:** Python 3.13, FastAPI, httpx, Pydantic, pytest

---

## 文件结构规划

### 新建文件
- `app/utils/ocr/__init__.py` - 导出公共接口
- `app/utils/ocr/config.py` - OCRConfig 配置类和预定义配置
- `app/utils/ocr/auth.py` - 认证策略实现
- `app/utils/ocr/base.py` - XFYunOCRClient 基类
- `app/utils/ocr/document_ocr.py` - 通用文档识别客户端
- `app/utils/ocr/pdf_ocr.py` - PDF 文档识别客户端
- `tests/utils/ocr/test_auth.py` - 认证策略测试
- `tests/utils/ocr/test_document_ocr.py` - 通用文档识别测试
- `tests/utils/ocr/test_pdf_ocr.py` - PDF 文档识别测试
- `tests/manual/test_ocr_clients.py` - 手动测试脚本

### 修改文件
- `app/schemas/ocr.py` - 添加新的 Schema 定义
- `app/routers/ocr.py` - 添加新的路由
- `app/dependencies/points.py` - 添加自定义扣费方法（如需要）

---

## Task 1: 创建目录结构和配置系统

**Files:**
- Create: `app/utils/ocr/__init__.py`
- Create: `app/utils/ocr/config.py`
- Create: `tests/utils/ocr/__init__.py`

- [ ] **Step 1: 创建 OCR 工具包目录**

```bash
mkdir -p app/utils/ocr
mkdir -p tests/utils/ocr
touch app/utils/ocr/__init__.py
touch tests/utils/ocr/__init__.py
```

- [ ] **Step 2: 实现配置类**

创建 `app/utils/ocr/config.py`:

```python
from dataclass