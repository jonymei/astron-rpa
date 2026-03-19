---
name: action
description: >-
  为 Astronverse RPA 引擎编写与修改原子能力组件：@atomicMg.atomic、inputList/outputList、meta.py、
  config.yaml 与 meta.json。在 engine/components/astronverse-* 新增或改能力、配展示文案、排查 Meta
  与前端绑定时使用。默认用 meta 骨架脚本生成 config，对照 astronverse-hello / astronverse-report。
license: Proprietary
metadata:
  astronverse-domain: engine
  version: "3.0.0"
  maintainer: TBD
compatibility: >-
  Python >=3.13；engine 工作区 uv；依赖 astronverse-actionlib（及常见 astronverse-baseline）。
  能力包位于 engine/components/。
---

# Astronverse 原子能力组件

面向 **`engine/components/astronverse-*`**：用 `astronverse.actionlib` 暴露编排可调用的原子方法，并由 **`meta.json`** 驱动前端表单。本 Skill 只补充 **仓库内约定与易错点**；通用 Python 语法不赘述。

## 何时使用

- 新增/修改 **原子能力类**、**`@atomicMg.atomic`** 方法、**`inputList` / `outputList`**。
- 维护 **`config.yaml`**、**`meta.py`**，或解释 **Meta 与参数不一致**。
- 需要 **枚举 / 布尔 / Pick** 等在前端的默认控件行为时，去 actionlib 源码核对（见下文「深入查阅」）。

**不必使用**：与原子能力无关的 `servers/`、`shared/` 纯库改动（除非要新暴露为原子能力）。

## 默认工作流（请按序执行）

编排配置易与代码漂移，**默认路径**如下；勿跳过第 2～3 步从零写整份 `config.yaml`。

1. **实现**：`@staticmethod` + `@atomicMg.atomic(...)`；签名与 `inputList`/`outputList` 一致；需要给用户看的返回值在装饰器上声明 **`outputList=[atomicMg.param("字段名", types="Str")]`**（类型名如 `Str`/`Int` 与框架约定一致）。不需要暴露给前端的返回可用 **`outputList=[]`**（见 `astronverse-report`）。
2. **生成 meta**：在组件目录执行 **`meta.py`**，得到 **`meta.json`**。若首次缺 `config.yaml`，可复制同仓库邻近组件的 `config.yaml` 再改。
3. **生成 config 骨架**（默认工具）：在 **`engine/`** 目录下执行（需 PyYAML，使用已 `uv sync` 的环境）：

```bash
uv run python ../.agents/skills/action/scripts/meta_json_to_config_yaml.py components/<组件名>/meta.json -o components/<组件名>/config.yaml
```

脚本路径相对**仓库根**：`.agents/skills/action/scripts/meta_json_to_config_yaml.py`。无 `-o` 则打印到 stdout。

4. **丰富化**：在骨架上改 **`title` / `comment` / `tip`**，补 **`options`**；**`inputList`/`outputList` 的 `key`** 必须与 **Python 参数名**（及 output 的 key）一致；**`options` 的顶层键**必须与 **枚举类型名**一致（如 `ReportLevelType`）。风格对齐 **`astronverse-hello/config.yaml`**、**`astronverse-report/config.yaml`**。
5. **校验**：再次运行 **`meta.py`**，确认 **`meta.json`** 与预期一致后再收尾。

## Gotchas（违反则易线上/编排出错）

- **仅关键字调用**：编排调用必须是 `Foo.bar(baz=1)` 形式；**禁止**依赖位置参数。
- **已发布能力的签名**：**禁止**对已上线流程做不兼容改参（改名、删参、改语义/类型）。只能 **加参（带默认值）** 或 **新增 v2 方法/新原子节点** 承接不兼容变更。
- **`atomicMg.param`**：使用 `atomicMg.param(key, **kwargs)`；**序列化与否由框架自动判断**。**不要**使用或引入已废弃的 **`convert`**。
- **`typing` 复杂注解**：actionlib 推断常落到 `Any` 并警告；要稳定 UI 请在 **`atomicMg.param` 中显式 `formType`**。
- **执行上下文**：需行号、进程等信息时，从 **`kwargs["__info__"]`** 读取（示例：**`astronverse-report`** 的 `Report.print`）。
- **分层**：平台相关逻辑放在 **Core**（或等价层）；原子类保持薄封装；**原子之间优先调 Core，避免原子互调**（见 **`astronverse-hello`** 内注释）。

## 代码组织（推荐）

| 层级 | 职责 |
|------|------|
| 对外原子类 | 装饰器、参数签名、`inputList`/`outputList` |
| `Core` + 接口 | 平台差异、可测业务逻辑 |
| `error` | `ErrorCode`、用户可见文案 |
| `BaseException` 双参（若用） | 第一参：用户可见需翻译；第二参：开发者日志 |

## 深入查阅（按需加载，节省上下文）

- **`references/REFERENCE.md`**：仓库路径索引、`meta.py` 模板、**类型注解 → 默认 `formType`** 速查与 actionlib 入口函数名。
- **actionlib 真相源**：`engine/shared/astronverse-actionlib/src/astronverse/actionlib/atomic.py`（`_inspect_param`）、`utils.py`（`gen_type`）、`__init__.py`（`AtomicFormType` 枚举）。
- **复杂表单**：`engine/components/astronverse-window/`（如 `DynamicsItem`）。
- **工作区约定**：`engine/AGENTS.md`；组件说明：`engine/components/README.md`。

## 提交前自检

- [ ] `@staticmethod` + `@atomicMg.atomic`，分组名符合产品约定
- [ ] `inputList`/`outputList` 与签名一致；需暴露给编排的返回 **`outputList` 含 `key` + `types`**
- [ ] `config.yaml`：**已用骨架脚本**或等价流程，**非**纯手搓全量
- [ ] `meta.py` 已 `register` 目标类；版本与 `pyproject.toml` 一致（若使用 `get_version()`）
- [ ] 调用设计为**仅关键字**；改动旧能力符合 **Gotchas** 中的契约规则
- [ ] 在最小范围内 **`ruff` / `pytest`** / 生成 `meta.json`（见 `engine/AGENTS.md`）