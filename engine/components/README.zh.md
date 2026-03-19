简体中文 | [English](README.md)
# 10 分钟开发一个 RPA 组件

这份文档只解决一件事：让你在当前仓库里快速做出一个可运行、可测试、可生成 `meta.json` 的组件。

如果你想看当前官方推荐的最小模板，直接看 [`astronverse-hello/`](./astronverse-hello/)。
如果你需要完整的组件开发参考，包括表单契约、类型元数据、网关代理和验证清单，请阅读[组件开发参考手册](./DEVELOPMENT.zh.md)。

## 1. 准备环境

在仓库根目录执行：

```bash
uv sync --project engine
```

这会为 `engine` 创建并同步虚拟环境。

## 2. 看懂一个最小组件

示例目录：

```text
engine/components/astronverse-hello/
├── config.yaml
├── meta.py
├── pyproject.toml
├── src/astronverse/hello/
│   ├── __init__.py
│   └── hello.py
└── tests/test_hello.py
```

各文件职责：

- `pyproject.toml`: 定义组件包名、依赖和构建方式
- `src/astronverse/hello/hello.py`: 组件实际代码
- `config.yaml`: 组件在设计器里的标题、说明、图标等配置
- `meta.py`: 生成 `meta.json`
- `tests/test_hello.py`: 最小行为测试

## 3. 写一个 Hello World 组件方法

核心代码在 [`astronverse-hello/src/astronverse/hello/hello.py`](./astronverse-hello/src/astronverse/hello/hello.py)：

```python
from astronverse.actionlib.atomic import atomicMg


class Hello:
    @staticmethod
    @atomicMg.atomic(
        "Hello",
        outputList=[atomicMg.param("greeting", types="Str")],
    )
    def say_hello(name: str = "World") -> str:
        return f"Hello, {name}!"
```

开发一个组件时，这段代码里最重要的只有两点：

- 用 `@atomicMg.atomic(...)` 把方法暴露给设计器
- 用 Python 函数签名定义输入参数，用 `outputList` 定义输出变量

## 4. 生成组件的 `meta.json`

执行：

```bash
uv run --project engine python engine/components/astronverse-hello/meta.py
```

成功后会在组件目录下生成或更新：

```text
engine/components/astronverse-hello/meta.json
```

## 5. 把新组件接入 engine

除了创建组件目录，还要改根工程的 [`engine/pyproject.toml`](../pyproject.toml)：

- 在 `[project].dependencies` 中加入组件名
- 在 `[tool.uv.sources]` 中加入本地路径，且使用 `editable = true`

示例：

```toml
"astronverse-hello",
astronverse-hello = {path = "./components/astronverse-hello", editable = true}
```

如果不做这一步，`uv run --project engine ...` 无法识别你的新组件。

## 6. 测试组件

执行：

```bash
uv run --project engine python -m unittest engine/components/astronverse-hello/tests/test_hello.py
```

## 7. 复制这个模板开发你自己的组件

`astronverse-hello` 是当前官方推荐的最小模板。最直接的方式就是：

1. 复制 `engine/components/astronverse-hello/`
2. 将目录名改成 `astronverse-你的组件名`
3. 把 `astronverse.hello`、`Hello`、`say_hello` 改成你的实际命名
4. 更新 `config.yaml` 和根 `engine/pyproject.toml`
5. 重新运行测试与 `meta.py`

### 新组件一定要有 `meta.py` 吗？

在当前仓库约定里，答案是要。`meta.py` 负责导出 `meta.json`。

### 我需要先写前端配置吗？

这个最小路径不需要。先让 Python 组件、测试和 `meta.json` 跑通，再看设计器侧是否还要补额外配置。

### 已上线流程正在用的原子，能直接改参数吗？

不要对已上线流程正在使用的原子做不兼容改参。已有参数名、类型和语义都要保持稳定。允许的演进方式只有：

- 增加一个带默认值的新参数
- 新增一个 `v2` 方法
- 新增一个原子节点或能力承接不兼容行为

## 下一步

- 看示例组件：[`astronverse-hello/`](./astronverse-hello/)
- 看完整参考手册：[`DEVELOPMENT.zh.md`](./DEVELOPMENT.zh.md)
- 回到 `engine` 脚本文档：[`../README.zh.md`](../README.zh.md)
