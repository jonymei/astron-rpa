# OCR 接口升级设计文档

## 概述

本文档描述 ai-service OCR 接口升级的技术设计方案。本次升级将在现有通用文字识别接口的基础上，扩展更多讯飞开放平台的 OCR 接口代理能力。

## 背景

当前系统已实现通用文字识别接口 (`/ocr/general`)，采用接口代理模式，保持与讯飞开放平台原始接口的高度一致性，仅修改认证鉴权部分并集成积分计费系统。

本次升级需要扩展 8 个新的 OCR 接口，首批实现 2 个 OCR 大模型接口：
1. PDF 文档识别（OCR大模型）
2. 通用文档识别（OCR大模型）

## 设计目标

1. **统一架构**：通过配置驱动的基类设计，降低新增接口的开发成本
2. **灵活认证**：支持多种认证方式（HMAC-SHA256、MD5+HmacSHA1）
3. **多种模式**：支持同步和异步两种 API 调用模式
4. **渐进迁移**：先实现新接口验证架构，再迁移现有代码
5. **易于扩展**：为后续 6 个接口的实现提供清晰的模板

## API 分析

### 通用文档识别（OCR大模型）
- **端点**：`https://cbm01.cn-huabei-1.xf-yun.com/v1/private/se75ocrbm`
- **认证**：HMAC-SHA256（与现有通用文字识别相同）
- **模式**：同步
- **请求**：JSON 格式，base64 编码图像
- **特性**：基于星火大模型，支持公式、图表、栏目等复杂场景
- **积分**：50 积分/次

### PDF 文档识别（OCR大模型）
- **端点**：
  - 创建任务：`https://iocr.xfyun.cn/ocrzdq/v1/pdfOcr/start`
  - 查询状态：`https://iocr.xfyun.cn/ocrzdq/v1/pdfOcr/status`
- **认证**：MD5 + HmacSHA1（不同于其他接口）
- **模式**：异步（创建任务 → 轮询状态 → 获取结果）
- **请求**：multipart/form-data 上传文件
- **特性**：支持多页 PDF，可导出 word/markdown/json
- **积分**：10 积分/页

## 架构设计

### 目录结构

```
app/utils/ocr/
├── __init__.py           # 导出公共接口
├── base.py               # XFYunOCRClient 基类
├── config.py             # OCRConfig 配置类和预定义配置
├── auth.py               # 认证策略实现
├── pdf_ocr.py            # PDF 文档识别
└── document_ocr.py       # 通用文档识别(OCR大模型)
```

### 核心组件

#### 1. 配置系统 (config.py)

**OCRConfig 类**：定义单个 API 的所有配置
```python
@dataclass
class OCRConfig:
    service_name: str           # 服务名称
    base_url: str               # API 端点
    auth_type: str              # 认证类型：'hmac_sha256' 或 'md5_hmac_sha1'
    request_mode: str           # 请求模式：'sync' 或 'async'
    service_id: Optional[str]   # 服务 ID（用于同步接口）
    timeout: float              # 请求超时时间
```

**预定义配置**：
- `DOCUMENT_OCR_CONFIG`：通用文档识别配置
- `PDF_OCR_CONFIG`：PDF 文档识别配置

#### 2. 认证策略 (auth.py)

**AuthStrategy 抽象基类**：
```python
class AuthStrategy(ABC):
    @abstractmethod
    def build_auth_url(self, url: str) -> str:
        """构建带认证参数的 URL"""

    @abstractmethod
    def build_auth_headers(self) -> dict:
        """构建认证请求头"""
```

**HmacSHA256Auth**：
- 实现 HMAC-SHA256 签名
- 用于通用文档识别等接口
- 认证参数附加在 URL 中

**MD5HmacSHA1Auth**：
- 实现 MD5 + HmacSHA1 签名
- 用于 PDF 文档识别接口
- 认证参数放在 HTTP 头中

#### 3. 统一基类 (base.py)

**XFYunOCRClient**：
- 接收 `OCRConfig` 配置对象
- 根据配置选择认证策略
- 提供 `_make_request()` 方法封装 HTTP 请求
- 统一的错误处理和日志记录

#### 4. 具体实现类

**DocumentOCRClient (document_ocr.py)**：
- 继承 `XFYunOCRClient`
- 使用 `DOCUMENT_OCR_CONFIG`
- 实现 `recognize()` 方法：接收 base64 图像，返回识别结果
- 同步模式，直接返回结果

**PDFOCRClient (pdf_ocr.py)**：
- 继承 `XFYunOCRClient`
- 使用 `PDF_OCR_CONFIG`
- 实现 `recognize()` 方法：
  1. 上传 PDF 文件，创建任务
  2. 轮询任务状态（间隔 5 秒）
  3. 任务完成后返回结果（包含页数信息）
- 异步模式，需要轮询

## 数据模型

### Schema 设计

**通用文档识别**：
```python
# 请求
class DocumentOCRRequest(BaseModel):
    image: str              # base64 编码的图像
    encoding: str = "jpg"   # 图像格式
    output_level: int = 1   # 输出级别
    output_format: str = "markdown"  # 输出格式

# 响应
class DocumentOCRResponse(BaseModel):
    header: OCRResponseHeader
    payload: Optional[OCRResponsePayload]
```

**PDF 文档识别**：
```python
# 请求
class PDFOCRRequest(BaseModel):
    file: UploadFile = None         # 文件上传
    pdf_url: str = None             # 或 PDF URL
    export_format: str = "json"     # 导出格式

# 响应
class PDFOCRResponse(BaseModel):
    task_no: str            # 任务号
    status: str             # 状态
    page_count: int         # 页数
    result_url: str = None  # 结果下载链接
```

## 路由设计

### 通用文档识别路由

```python
@router.post("/ocr/document", response_model=DocumentOCRResponse)
async def document_ocr(
    params: DocumentOCRRequest,
    points_context: PointsContext = Depends(
        PointChecker(50, PointTransactionType.XFYUN_COST)
    ),
):
    """通用文档识别（OCR大模型）"""
    client = DocumentOCRClient()
    result = await client.recognize(params.image, params.encoding)

    if result.header.code == 0:
        await points_context.deduct_points()

    return result
```

### PDF 文档识别路由

```python
@router.post("/ocr/pdf", response_model=PDFOCRResponse)
async def pdf_ocr(
    file: UploadFile = File(None),
    pdf_url: str = Form(None),
    export_format: str = Form("json"),
    points_context: PointsContext = Depends(
        PointChecker(0, PointTransactionType.XFYUN_COST)  # 初始不扣费
    ),
):
    """PDF 文档识别（OCR大模型）"""
    client = PDFOCRClient()
    result = await client.recognize(file, pdf_url, export_format)

    if result.status == "completed":
        # 按页数扣费：10 积分/页
        points_to_deduct = result.page_count * 10
        await points_context.deduct_points_custom(points_to_deduct)

    return result
```

## 积分计费策略

1. **通用文档识别**：固定 50 积分/次，成功时扣费
2. **PDF 文档识别**：按页数计费，10 积分/页，任务完成时扣费
3. **扣费时机**：API 调用成功（返回码为 0 或任务完成）后扣费
4. **失败处理**：调用失败不扣费

## 错误处理

### 错误类型

1. **业务逻辑错误**：API 返回非 0 错误码 → 400 Bad Request
2. **网络错误**：HTTP 请求失败 → 503 Service Unavailable
3. **超时错误**：请求超时 → 504 Gateway Timeout
4. **未知错误**：其他异常 → 500 Internal Server Error

### 错误响应格式

```python
{
    "detail": "错误描述信息"
}
```

## 测试策略

### 单元测试

1. **认证策略测试**：
   - 测试 HMAC-SHA256 签名生成
   - 测试 MD5+HmacSHA1 签名生成

2. **基类测试**：
   - 测试配置加载
   - 测试认证策略选择
   - 测试错误处理

3. **客户端测试**：
   - Mock HTTP 请求，测试请求构建
   - 测试响应解析
   - 测试异步轮询逻辑

### 集成测试

1. **通用文档识别**：
   - 准备测试图像（base64 编码）
   - 调用 API，验证返回结果
   - 验证积分扣除

2. **PDF 文档识别**：
   - 准备测试 PDF 文件
   - 调用 API，创建任务
   - 轮询任务状态
   - 验证按页数扣费

### 手动测试脚本

创建 `tests/manual/test_ocr_clients.py`：
- 直接调用客户端类
- 使用真实的讯飞 API
- 验证端到端流程

## 实施计划

### 阶段 1：基础设施（第 1 天）
1. 创建目录结构
2. 实现配置系统 (config.py)
3. 实现认证策略 (auth.py)
4. 实现统一基类 (base.py)

### 阶段 2：客户端实现（第 2 天）
1. 实现通用文档识别客户端 (document_ocr.py)
2. 实现 PDF 文档识别客户端 (pdf_ocr.py)
3. 编写单元测试

### 阶段 3：路由集成（第 3 天）
1. 定义 Schema (app/schemas/ocr.py)
2. 实现路由 (app/routers/ocr.py)
3. 配置积分扣费
4. 编写集成测试

### 阶段 4：测试验证（第 4 天）
1. 运行单元测试
2. 运行集成测试
3. 手动测试验证
4. 修复问题

### 阶段 5：文档和部署（第 5 天）
1. 更新 README
2. 更新 API 文档
3. 部署到测试环境
4. 验收测试

## 后续扩展

完成前两个接口后，后续 6 个接口的实现流程：

1. 在 `config.py` 中添加新的配置常量
2. 创建新的客户端类（如果需要特殊逻辑）
3. 在 `app/schemas/ocr.py` 中添加 Schema
4. 在 `app/routers/ocr.py` 中添加路由
5. 编写测试

预计每个接口的开发时间：0.5-1 天

## 风险和注意事项

1. **API 文档不规范**：讯飞 API 文档可能不准确，需要参考官方 demo
2. **认证差异**：不同接口的认证方式可能有细微差异，需要逐个验证
3. **异步轮询**：PDF 识别的轮询逻辑需要合理设置间隔和超时
4. **积分计费**：PDF 按页数计费需要准确获取页数信息
5. **现有代码迁移**：迁移现有通用文字识别时需要确保不影响现有功能

## 总结

本设计采用配置驱动的统一基类架构，通过灵活的认证策略和请求模式支持，为 OCR 接口的扩展提供了清晰的框架。首批实现的两个 OCR 大模型接口将验证架构的合理性，为后续 6 个接口的快速实现奠定基础。
