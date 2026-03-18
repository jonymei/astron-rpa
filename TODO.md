# TODO

## astronverse-openapi 安全改造

### 背景

当前 `astronverse-openapi` 组件中的能力接入方式不一致：

- 一部分能力通过本地网关访问 `127.0.0.1:{GATEWAY_PORT}/api/rpa-ai-service/...`
- 一部分能力仍在组件内直接访问讯飞外部接口，并在组件侧处理签名与鉴权

已确认的直连讯飞能力包括：

- `id_card`
- `business_license`
- `vat_invoice`
- `train_ticket`
- `taxi_ticket`

对应代码位置：

- [openapi.py](/C:/Users/ahume/GitHub/astron-rpa/engine/components/astronverse-openapi/src/astronverse/openapi/openapi.py)
- [core_iflytek.py](/C:/Users/ahume/GitHub/astron-rpa/engine/components/astronverse-openapi/src/astronverse/openapi/core_iflytek.py)

### 风险说明

- 组件侧直接感知外部服务真实地址、签名逻辑和接入细节，职责边界不清晰。
- 若本地配置分发、调试包传播或日志处理不当，存在 `APP_ID`、`API_KEY`、`API_SECRET` 等敏感信息泄露风险。
- 组件直接出网会绕过统一网关，后续难以在网关层统一做鉴权、审计、限流、观测和策略控制。
- 组件与云端 `ai-service` 的接入模式不一致，增加维护成本和后续迁移成本。

### 改造目标

将 `astronverse-openapi` 中所有直连讯飞的能力统一改造为：

- 组件只访问本地网关 `127.0.0.1:{GATEWAY_PORT}`
- 本地网关负责转发到云端 `ai-service`
- 云端 `ai-service` 负责外部厂商接口访问、签名、鉴权、异常处理和能力编排

### 待办事项

- 在 `ai-service` 中补齐证件/票据类 OCR 能力的服务端接口，覆盖以下场景：
  - 身份证 OCR
  - 营业执照 OCR
  - 增值税发票 OCR
  - 火车票 OCR
  - 出租车票 OCR
- 将上述能力的讯飞签名、鉴权和外部接口访问逻辑全部迁移到 `ai-service`。
- 为本地网关增加上述 OCR 能力的代理路由，统一纳入 `/api/rpa-ai-service/...` 访问路径。
- 修改 `astronverse-openapi` 组件，移除组件内对讯飞模板 OCR 的直连调用。
- 修改 `astronverse-openapi` 组件，移除组件内对 `APP_ID`、`API_KEY`、`API_SECRET` 的直接依赖。
- 收敛组件内外部服务地址拼装逻辑，统一通过本地网关访问，不再暴露外部厂商地址到组件侧。
- 改造完成后，复查组件代码、配置文件和文档，确保不再要求组件侧持有外部服务密钥。

### 验收标准

- `astronverse-openapi` 组件内不再出现讯飞外部 OCR 地址直连。
- `astronverse-openapi` 组件内不再保留讯飞签名与鉴权逻辑。
- 组件侧所有 OCR 与语音能力统一通过本地网关访问。
- 外部厂商密钥仅保留在云端服务或受控服务端环境中。
