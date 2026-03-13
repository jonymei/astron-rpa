简体中文 | [English](README.md)
# 10 分钟开发一个 RPA 组件

这份文档只解决一件事：让你在当前仓库里快速做出一个可运行、可测试、可生成 `meta.json` 的组件。

如果你想看一个真实最小示例，直接看 [`astronverse-hello/`](./astronverse-hello/)。

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

如果这个组件还需要进入最终打包产物，还要同步更新 [`manifest.toml`](./manifest.toml)。
没有出现在 manifest 中的组件，构建脚本会明确提示为 ignored，并且不会参与产品打包。

## 6. 测试组件

执行：

```bash
uv run --project engine python -m unittest engine/components/astronverse-hello/tests/test_hello.py
```

## 7. 复制这个模板开发你自己的组件

最直接的方式就是：

1. 复制 `engine/components/astronverse-hello/`
2. 将目录名改成 `astronverse-你的组件名`
3. 把 `astronverse.hello`、`Hello`、`say_hello` 改成你的实际命名
4. 更新 `config.yaml`、根 `engine/pyproject.toml`，以及 [`manifest.toml`](./manifest.toml)
5. 重新运行测试与 `meta.py`

### 新组件一定要有 `meta.py` 吗？

在当前仓库约定里，答案是要。`meta.py` 负责导出 `meta.json`。

### 我需要先写前端配置吗？

这个最小路径不需要。先让 Python 组件、测试和 `meta.json` 跑通，再看设计器侧是否还要补额外配置。

## 下一步

- 看示例组件：[`astronverse-hello/`](./astronverse-hello/)
- 回到 `engine` 脚本文档：[`../README.zh.md`](../README.zh.md)
