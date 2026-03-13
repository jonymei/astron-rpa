from __future__ import annotations

import argparse
import tomllib
from dataclasses import dataclass
from pathlib import Path


class ManifestError(Exception):
    pass


@dataclass
class ComponentSelection:
    discovered: list[str]
    included: list[str]
    ignored: list[str]

    @property
    def workspace_members(self) -> list[str]:
        return [f"components/{name}" for name in self.included]


def load_manifest_components(manifest_path: Path) -> list[str]:
    if not manifest_path.exists():
        raise ManifestError(f"Manifest file not found: {manifest_path}")

    with manifest_path.open("rb") as file:
        data = tomllib.load(file)

    include = data.get("components", {}).get("include")
    if not isinstance(include, list) or not include:
        raise ManifestError("Manifest must define a non-empty [components].include list")

    invalid = [item for item in include if not isinstance(item, str) or not item.strip()]
    if invalid:
        raise ManifestError("Manifest contains invalid component names")

    return [item.strip() for item in include]


def collect_component_selection(components_dir: Path, manifest_path: Path) -> ComponentSelection:
    discovered = sorted(
        path.name
        for path in components_dir.iterdir()
        if path.is_dir() and (path / "pyproject.toml").exists()
    )

    included = load_manifest_components(manifest_path)
    missing = sorted(set(included) - set(discovered))
    if missing:
        raise ManifestError(f"Manifest references missing components: {', '.join(missing)}")

    filtered_included = [name for name in discovered if name in set(included)]
    ignored = [name for name in discovered if name not in set(included)]
    return ComponentSelection(discovered=discovered, included=filtered_included, ignored=ignored)


def format_for_batch(selection: ComponentSelection) -> str:
    lines = [
        f"DISCOVERED_COMPONENTS={'|'.join(selection.discovered)}",
        f"INCLUDED_COMPONENTS={'|'.join(selection.included)}",
        f"IGNORED_COMPONENTS={'|'.join(selection.ignored)}",
        f"WORKSPACE_COMPONENT_MEMBERS={'|'.join(selection.workspace_members)}",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--components-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--format", choices=["batch"], default="batch")
    args = parser.parse_args()

    try:
        selection = collect_component_selection(Path(args.components_dir), Path(args.manifest))
    except ManifestError as exc:
        print(f"ERROR={exc}")
        return 1

    if args.format == "batch":
        print(format_for_batch(selection))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
