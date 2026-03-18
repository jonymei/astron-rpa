# OCR 接口升级规划

## 📋 升级概述

本次升级将在现有通用文字识别接口的基础上,扩展更多讯飞开放平台的 OCR 接口代理能力。所有接口将保持与讯飞开放平台原始接口的高度一致性,仅修改认证鉴权部分并集成积分计费系统。

## 🎯 设计原则

1. **接口代理模式**: 参数与讯飞开放平台原始接口保持一致,方便客户端调试
2. **统一认证**: 修改讯飞的认证鉴权方式,使用平台统一的用户认证
3. **积分计费**: 所有接口调用都集成积分管理系统
4. **直接请求**: 避免使用讯飞 SDK,直接发起网络请求以保证代码质量

## 📚 待实现接口列表

### 1. PDF文档识别(OCR大模型)
- **API文档**: https://www.xfyun.cn/doc/words/pdfOcr/API.html
- **功能描述**: 基于 OCR 大模型的 PDF 文档识别能力
- **接口路径**: 待定
- **积分消耗**: 待定

### 2. 通用文档识别(OCR大模型)
- **API文档**: https://www.xfyun.cn/doc/words/OCRforLLM/API.html
- **功能描述**: 基于 OCR 大模型的通用文档识别能力
- **接口路径**: 待定
- **积分消耗**: 待定

### 3. 通用文字识别
- **API文档**: https://www.xfyun.cn/doc/words/universal_character_recognition/API.html
- **功能描述**: 通用文字识别(当前已实现)
- **接口路径**: `/ocr/general`
- **积分消耗**: 50
- **状态**: ✅ 已实现

### 4. 票据卡证识别
- **API文档**: https://www.xfyun.cn/doc/words/TicketIdentification/API.html
- **功能描述**: 识别各类票据和卡证信息
- **接口路径**: 待定
- **积分消耗**: 待定

### 5. 名片识别
- **API文档**: https://www.xfyun.cn/doc/words/businessCardRecg/API.html
- **功能描述**: 识别名片上的联系人信息
- **接口路径**: 待定
- **积分消耗**: 待定

### 6. 身份证识别
- **API文档**: https://www.xfyun.cn/doc/words/idCardRecg/API.html
- **功能描述**: 识别身份证正反面信息
- **接口路径**: 待定
- **积分消耗**: 待定

### 7. 银行卡识别
- **API文档**: https://www.xfyun.cn/doc/words/bankCardRecg/API.html
- **功能描述**: 识别银行卡号等信息
- **接口路径**: 待定
- **积分消耗**: 待定

### 8. 营业执照识别
- **API文档**: https://www.xfyun.cn/doc/words/businessLicenseRecg/API.html
- **功能描述**: 识别营业执照上的企业信息
- **接口路径**: 待定
- **积分消耗**: 待定

### 9. 增值税发票识别
- **API文档**: https://www.xfyun.cn/doc/words/VAT-invoice-recg/API.html
- **功能描述**: 识别增值税发票信息
- **接口路径**: 待定
- **积分消耗**: 待定

## 🔧 技术实现要点

### 认证鉴权
- 参考现有 `app/utils/ocr.py` 中的实现
- 使用 HMAC-SHA256 签名算法
- 构建认证 URL: `assemble_ws_auth_url()`
- 认证参数: host, date, authorization

### 请求构建
- 统一的请求头格式
- 标准的 JSON 请求体结构
- 异步 HTTP 请求 (httpx.AsyncClient)

### 响应处理
- 定义对应的 Pydantic Schema
- 统一的错误处理机制
- 完整的日志记录

### 积分管理
- 使用 `PointChecker` 依赖注入
- 请求前检查积分余额
- 请求成功后扣除积分
- 失败时不扣除积分(部分接口)

## ⚠️ 重要注意事项

### API 文档使用
1. **优先参考官方 API 文档**: 讯飞开放平台的 API 文档虽然不够规范,但整体是正确的
2. **避免使用网络上的其他信息**: 可能存在过时或错误的信息
3. **参考官方 Demo**: 如果按文档调试不通,可以下载官方 demo 参考
4. **避免 SDK Demo**: 不要下载带 SDK 的 demo,SDK 实现质量较差
5. **直接发起网络请求**: 不使用讯飞 SDK,直接使用 httpx 等库发起请求

### 现有实现参考
- 文件位置: `app/utils/ocr.py`
- 路由位置: `app/routers/ocr.py`
- Schema 位置: `app/schemas/ocr.py`
- 当前实现的是通用文字识别接口

## 📝 实施步骤

### 阶段一: 调研与设计
1. [ ] 详细阅读所有 API 文档
2. [ ] 分析各接口的请求/响应格式差异
3. [ ] 设计统一的接口架构
4. [ ] 确定各接口的积分消耗策略
5. [ ] 设计 Schema 和数据模型

### 阶段二: 核心功能实现
1. [ ] 实现 PDF 文档识别接口
2. [ ] 实现通用文档识别(OCR大模型)接口
3. [ ] 实现票据卡证识别接口
4. [ ] 实现名片识别接口

### 阶段三: 证件识别实现
1. [ ] 实现身份证识别接口
2. [ ] 实现银行卡识别接口
3. [ ] 实现营业执照识别接口
4. [ ] 实现增值税发票识别接口

### 阶段四: 测试与优化
1. [ ] 编写单元测试
2. [ ] 编写集成测试
3. [ ] 性能测试与优化
4. [ ] 文档更新

## 📖 相关文档

- [讯飞开放平台](https://www.xfyun.cn/)
- [现有 OCR 实现](app/utils/ocr.py)
- [项目 README](README.zh.md)

## 🔄 更新记录

- 2026-03-18: 创建文档,记录 OCR 接口升级规划
