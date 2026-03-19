#!/usr/bin/env python3
"""
将组件生成的 meta.json（顶层键为「类名.方法名」）转换为 config.yaml 骨架。

逻辑对齐历史「原子能力小工具」中的 gen_config：
- atomic.<key>：title、comment、icon、helpManual，以及精简的 inputList / outputList（仅 key、title、tip）
- options：从各 input 参数的 options 提取，按该参数的 types 作为分组键，每项为 value / label

依赖：PyYAML（`pip install pyyaml`，或在已 `uv sync` 的 engine 工作区下用 `uv run python` 调用本脚本）

用法示例：
  python meta_json_to_config_yaml.py path/to/meta.json -o path/to/config.yaml
  python meta_json_to_config_yaml.py path/to/meta.json   # 输出到 stdout
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _str_or_empty(v: Any) -> str:
    if v is None:
        return ""
    return str(v)


def meta_json_to_config_skeleton(meta: dict[str, Any]) -> dict[str, Any]:
    """meta 对象 -> config 骨架 dict（再交给 yaml.dump）。"""
    res: dict[str, Any] = {"atomic": {}, "options": {}}
    res_options_list: dict[str, list[dict[str, str]]] = {}

    for key, item in meta.items():
        if not isinstance(item, dict):
            continue

        res_input_list: list[dict[str, str]] = []
        for inp in item.get("inputList") or []:
            if not isinstance(inp, dict):
                continue
            res_input_list.append(
                {
                    "key": _str_or_empty(inp.get("key")),
                    "title": _str_or_empty(inp.get("title")),
                    "tip": _str_or_empty(inp.get("tip")),
                }
            )
            types = inp.get("types")
            opts = inp.get("options")
            if opts and types is not None:
                type_key = _str_or_empty(types)
                res_options_list[type_key] = []
                for o in opts:
                    if isinstance(o, dict):
                        res_options_list[type_key].append(
                            {
                                "value": _str_or_empty(o.get("value")),
                                "label": _str_or_empty(o.get("label")),
                            }
                        )

        res_output_list: list[dict[str, Any]] = []
        for out in item.get("outputList") or []:
            if isinstance(out, dict):
                res_output_list.append(
                    {
                        "key": out.get("key"),
                        "title": _str_or_empty(out.get("title")),
                        "tip": _str_or_empty(out.get("tip")),
                    }
                )

        res["atomic"][key] = {
            "title": _str_or_empty(item.get("title")),
            "comment": _str_or_empty(item.get("comment")),
            "icon": _str_or_empty(item.get("icon")),
            "helpManual": _str_or_empty(item.get("helpManual")),
            "inputList": res_input_list,
            "outputList": res_output_list,
        }
        res["options"] = res_options_list

    return res


def main() -> None:
    parser = argparse.ArgumentParser(
        description="由 meta.json 生成 config.yaml 骨架（与历史 gen_config 行为一致）"
    )
    parser.add_argument(
        "meta_json",
        type=Path,
        help="meta.json 路径（UTF-8 JSON，顶层为原子键 -> 元数据对象）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="输出 YAML 路径；省略则打印到 stdout",
    )
    args = parser.parse_args()

    raw = args.meta_json.read_text(encoding="utf-8")
    meta = json.loads(raw)
    if not isinstance(meta, dict):
        print("错误：meta.json 根节点必须是 JSON 对象", file=sys.stderr)
        sys.exit(1)

    skeleton = meta_json_to_config_skeleton(meta)

    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        print(
            "错误：未安装 PyYAML。请执行: pip install pyyaml\n"
            "或在 engine 目录下: uv run python "
            f'"{Path(__file__).resolve()}" {args.meta_json}',
            file=sys.stderr,
        )
        sys.exit(1)

    text = yaml.dump(
        skeleton,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )

    if args.output is not None:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
