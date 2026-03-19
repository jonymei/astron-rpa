# 原子能力 Skill — 参考附录

主说明见 [../SKILL.md](../SKILL.md)。以下供 **按需打开**，避免挤占主 Skill 上下文。

## 1. 仓库路径索引

| 用途 | 路径 |
|------|------|
| meta → config 骨架脚本 | `.agents/skills/action/scripts/meta_json_to_config_yaml.py` |
| 默认表单推断 | `engine/shared/astronverse-actionlib/src/astronverse/actionlib/atomic.py`（`_inspect_param`） |
| 类型分类 | `engine/shared/astronverse-actionlib/src/astronverse/actionlib/utils.py`（`gen_type`、`InspectType`） |
| `AtomicFormType` 枚举 | `engine/shared/astronverse-actionlib/src/astronverse/actionlib/__init__.py` |
| 设计器类型文案（辅助） | `engine/shared/astronverse-actionlib/config_type.yaml` |
| Demo：Core + `outputList` | `engine/components/astronverse-hello/src/astronverse/hello/hello.py`、`core.py` |
| Demo 配置 | `engine/components/astronverse-hello/config.yaml`、`meta.py` |
| 生产：`inputList`、`__info__`、`outputList: []` | `engine/components/astronverse-report/src/astronverse/report/report.py`、`config.yaml`、`meta.py` |
| 复杂表单 | `engine/components/astronverse-window/src/astronverse/window/window.py` |

## 2. `meta.py` 模板

```python
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.baseline.config.config import load_config
from astronverse.<包>.<模块> import <原子类>


def get_version():
    return load_config("pyproject.toml")["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(<原子类>, version=get_version())
    atomicMg.meta()
```

将 `<包>`、`<模块>`、`<原子类>` 换成实际符号。

## 3. 类型注解 → 默认 `formType`（速查）

**规则以源码为准**；未写 `formType` 时由 `_inspect_param` + `gen_type` 推断。已写 **`formType`** 则以代码为准。

| 注解 / 类型 | 默认 `formType`（摘要） |
|-------------|-------------------------|
| 一般入参基线 | `INPUT_VARIABLE_PYTHON` |
| Python `bool` | `SWITCH`（是/否） |
| `enum.Enum` 子类 | 选项 ≤3 → `RADIO`，否则 `SELECT`；`types` 为枚举类名 |
| `astronverse.actionlib.types.Bool` | `SWITCH` |
| `Pick` 族 | `PICK`（`params` 含 `use`） |
| `Date` | `DEFAULTDATEPICKER` |
| `str`/`int`/`float`/`list`/`tuple`/`dict`（非 `bool`） | 基线 `INPUT_VARIABLE_PYTHON` |
| `typing` 复杂形态 | 常视为 `Any` + 警告 → **请显式 `formType`** |
| `outputList` 项 | 注册时统一补 **`RESULT`**（见 `atomic.py` 对 output 的 `update`） |

## 4. 参数与 Meta 要点（摘录）

- 暴露给编排的参数宜 **可序列化**；否则走 **参数传递**，框架不强行转换。
- **返回值**反射不完备：必须在 **`outputList`** 中声明 **`key` + `types`**；不需要给用户看时可 **`outputList=[]`**。
- **`meta.json`** 由 `meta.py` 写出，供前端渲染与字段绑定。
