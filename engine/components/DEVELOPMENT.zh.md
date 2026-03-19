简体中文 | [English](DEVELOPMENT.md)
# Engine 组件开发参考手册

这份文档是 `engine/components` 的完整组件开发参考手册。

当 10 分钟上手指南已经不够，需要对下面这些问题做判断时，使用这份文档：

- 组件包结构
- 面向设计器的表单元数据
- 可复用对象输出与类型元数据
- 仓库内后端服务访问方式
- 验证与文档更新

如果你只需要最短路径跑通一个组件，请先看[10 分钟上手指南](README.zh.md)。`astronverse-hello` 是当前官方推荐的最小组件模板。

## 1. 先从最小拥有者包开始

把 `engine/components/` 下的每个组件都当成独立包来看。编辑前先看局部包约定，不要假设仓库里只有一种统一模式。

至少检查这些文件：

- `pyproject.toml`
- `meta.py`
- `config.yaml`
- `error.py`
- `src/` 下源码
- 本地测试

新组件的最小目录通常是：

```text
engine/components/astronverse-your-component/
├── config.yaml
├── error.py
├── meta.py
├── pyproject.toml
├── src/astronverse/your_component/
│   ├── __init__.py
│   └── ...
└── tests/
```

如果组件输出的是可复用的类型对象，还应当有：

```text
├── config_type.yaml
└── meta_type.json
```

## 2. 编码前先选对参考组件

优先参考行为最接近的生产组件。通常一个主参考、一个次参考就够了。

常用参考分组：

- 官方最小模板：[`astronverse-hello/`](./astronverse-hello/)
- 可复用对象输出：[`astronverse-browser/`](./astronverse-browser/)、[`astronverse-excel/`](./astronverse-excel/)、[`astronverse-word/`](./astronverse-word/)
- 丰富表单与动态字段：[`astronverse-word/`](./astronverse-word/)、[`astronverse-excel/`](./astronverse-excel/)、[`astronverse-encrypt/`](./astronverse-encrypt/)、[`astronverse-email/`](./astronverse-email/)、[`astronverse-vision/`](./astronverse-vision/)
- 通过本地网关访问仓库内后端能力：[`astronverse-ai/`](./astronverse-ai/)、[`astronverse-openapi/`](./astronverse-openapi/)

选择参考时比较这几件事：

- 运行时行为是否同类
- 用户看到的表单形态是否同类
- 输出变量行为是否同类
- 是否依赖本地网关转发

默认先从 `astronverse-hello` 起步；只有目标组件需要更丰富的能力时，再借鉴更复杂的生产组件模式。

## 3. 先实现运行时能力

Python 代码负责运行时行为。通过 `@atomicMg.atomic(...)` 暴露设计器动作，在优化文案或表现形式前，先保证方法契约本身是正确的。

源码层常见职责：

- 实现运行时动作
- 在 atomic 元数据里声明输入输出结构
- 把服务访问、文件 I/O、对象创建都封装在组件包里

用户能看到的标题、标签、提示、默认值、选项展示，优先放在配置层，而不是散落在运行时代码里，除非 atomic 库本身要求放在代码中。

## 4. 在 `error.py` 中定义组件异常

每个组件都应当有自己的 `error.py`，作为该组件的异常定义入口。

建议沿用 `astronverse-hello` 和现有生产组件的模式：

- 引入 `BizCode`、`ErrorCode` 和 baseline 的 `BaseException`
- 在组件自己的 `error.py` 里重新导出 `BaseException`
- 在这里定义组件域内的 `ErrorCode` 常量
- 用户可见文案通过 `_()` 做翻译

推荐分层：

- `core.py` 或等价模块负责运行时实现
- `error.py` 负责组件异常定义
- 原子暴露层负责把运行时失败映射为组件域异常

抛出组件异常时，建议保持：

- 第一个参数是来自组件 `ErrorCode` 的、面向用户的翻译文案
- 第二个参数是面向开发者日志的细节信息

不要把组件域错误文案零散写成 runtime 代码里的字面量。

## 5. 把 `config.yaml` 当作设计器契约层

`config.yaml` 是组件在设计器侧的主要用户契约。只要是“这个组件在设计器里怎么显示”，优先先看这里。

常见职责包括：

- `title`
- `comment`
- `icon`
- `helpManual`
- `inputList`
- `outputList`
- `options`

实际链路可以理解为：

1. Python atomic 定义基础结构
2. `config.yaml` 补齐设计器文案和配置
3. `meta.py` 生成 `meta.json`
4. 设计器消费生成后的元数据

所以改表单时，不要只看源码，要看生成后的 `meta.json`。

## 6. 已上线流程必须保持向后兼容

一旦某个原子能力可能已经被已上线流程使用，就要把它当成兼容性契约来维护。

禁止做这些不兼容改动：

- 重命名已有参数
- 删除已有参数
- 不兼容地修改已有参数类型
- 不兼容地改变已有参数语义

允许的演进方式只有：

- 新增一个带安全默认值的参数
- 新增一个 `v2` 方法
- 新增一个原子节点或新能力承接不兼容行为

如果确实需要不兼容变更，保留旧原子，新增后继版本，而不是直接改坏旧能力。

## 7. 尽量落在现有表单类型里

大多数组件开发都应该复用现有表单语义，而不是新增一套。

当前常见表单类型包括：

- 普通输入和变量输入
- `SELECT`
- `RADIO`
- `SWITCH`
- `FILE`
- `TEXTAREAMODAL`
- `PICK`
- `CVPICK`
- `REMOTEPARAMS`
- `REMOTEFOLDERS`
- `RESULT`

离散选项优先用 `options`，条件显示优先用 `dynamics`。

典型场景：

- 只有选择“保存”模式时才显示文件路径
- 只有某一种处理模式下才显示额外配置

不要轻易新增 `formType`，也不要为现有 `formType.params` 发明前端还不理解的新语义。

### 什么情况下需要前端适配

出现以下任一情况，任务就不再只是 `engine` 内部改动：

- 需要新的 `formType`
- 现有渲染行为无法表达目标交互
- 需要新的 `formType.params` 语义，而当前前端渲染或序列化链路并不理解

这时要明确说明：该改动还需要前端适配。

## 8. 输出要复用的对象时，补齐类型注册

有些组件输出的不只是标量，而是后续节点还要继续引用的对象。

这种情况下，普通 `outputList` 不够，还需要：

- 增加 `config_type.yaml`
- 在 `meta.py` 里通过 `typesMg.register_types(...)` 注册类型
- 生成类型元数据
- 保证输出类型名与当前变量选择行为一致

可参考：

- [`astronverse-browser/meta.py`](./astronverse-browser/meta.py)
- [`astronverse-browser/config_type.yaml`](./astronverse-browser/config_type.yaml)
- [`astronverse-word/meta.py`](./astronverse-word/meta.py)
- [`astronverse-excel/meta.py`](./astronverse-excel/meta.py)

这几块少一块，后续变量流转就可能退化或出错。

## 9. 访问仓库内后端能力时走本地网关

如果组件依赖的是仓库内后端服务能力，组件侧应当走本地路由或网关链路，而不是直接请求后端服务 Endpoint。

当前稳定模式通常是：

```text
http://127.0.0.1:{GATEWAY_PORT}/api/...
```

可参考：

- [`astronverse-ai/src/astronverse/ai/api/llm.py`](./astronverse-ai/src/astronverse/ai/api/llm.py)
- [`astronverse-openapi/src/astronverse/openapi/client.py`](./astronverse-openapi/src/astronverse/openapi/client.py)

规则是：

- 本地端口优先从当前配置如 `GATEWAY_PORT` 推导
- 访问仓库内后端能力时优先沿用本地代理链
- 如果已经有本地路由，不要再硬编码直连服务地址

如果当前没有合适的本地网关或代理链路，就把任务视为 `engine + backend` 的联动工作，而不是在组件里临时直连。

## 10. 新组件要接入 engine workspace

仅仅创建目录还不够。新增组件包时，还要修改 [`engine/pyproject.toml`](../pyproject.toml)：

- 在 `[project].dependencies` 里加入组件名
- 在 `[tool.uv.sources]` 里加入本地 editable 路径

否则 `uv run --project engine ...` 无法正确识别这个包。

## 11. 生成元数据并做聚焦验证

至少验证这些内容：

1. `meta.py` 可以成功执行
2. 生成的 `meta.json` 中包含预期的输入、输出、标题、默认值、选项和说明
3. 如果输出可复用对象，类型元数据也被正确生成
4. 本地测试通过
5. 新包已经接入 workspace
6. 已上线流程依赖的旧原子仍然保持兼容，或者不兼容能力已通过新版本承接
7. 组件域异常已在 `error.py` 中集中定义并被一致使用

常用命令：

```bash
uv run --project engine python engine/components/<component-name>/meta.py
uv run --project engine python -m unittest engine/components/<component-name>/tests/<test_file>.py
```

只在确有必要时再扩大验证范围。

## 12. 合并前检查清单

- 是否以 `astronverse-hello` 作为默认起点，除非任务明确需要更复杂模式
- 是否优先复用了最接近的生产组件模式，而不是重新发明一套
- 是否在 `error.py` 里定义了组件域异常
- 是否合理区分了用户可见错误信息和开发日志信息
- 用户层文案是否主要放在 `config.yaml`
- 是否检查了生成后的 `meta.json`
- 是否保持了已上线流程的向后兼容
- 如果必须做不兼容行为，是否通过默认值新参数、`v2` 方法或新原子承接
- 是否落在现有表单类型里
- 如果没有，是否明确指出还需要前端适配
- 如果输出可复用对象，是否补了类型注册和类型元数据
- 如果访问仓库内后端能力，是否走了本地网关或代理
- 是否执行了聚焦测试和元数据生成

## 13. 与项目 Skill 的关系

项目 Skill 位于 [`.agents/skills/component-development/`](../../.agents/skills/component-development/)，它是给 Codex 用的压缩操作规程。这份文档才是面向人的长期参考手册。

以后组件开发约定变更时，建议先更新这份参考手册，再更新 Skill，保持两者一致。
