# AGENTS.md

## Scope

This file applies to everything under `engine/`.

## Engine Role In The Monorepo

`engine/` is a Python 3.13 RPA engine workspace managed with `uv`. It is not a single package and not a single executable. It is a multi-package workspace that combines reusable libraries, runtime services, and end-user automation components.

Read the workspace as three major layers:

- `shared/`: foundational libraries reused across the engine ecosystem.
- `servers/`: runnable engine-side services and supporting daemons.
- `components/`: end-user automation capability packages that expose concrete RPA actions.

The root `engine/pyproject.toml` aggregates these local packages through `[tool.uv.sources]`. Changes often belong to one package even when they are developed from the workspace root.

## Local Architecture Map

- `shared/`: low-level shared primitives and cross-package libraries.
- `servers/`: orchestrators, executors, pickers, schedulers, triggers, and bridge-style runtime services.
- `components/`: domain capabilities such as browser, vision, input, report, AI, and office/document automation.
- `scripts/`: workspace maintenance and support scripts.
- `tests/`: engine-level tests that are not isolated to a single leaf package.

When working in `engine/`, first decide which layer owns the behavior:

1. If the change is reusable across multiple packages, it likely belongs in `shared/`.
2. If the change is about process orchestration or a long-running service, it likely belongs in `servers/`.
3. If the change is a user-facing automation capability, it likely belongs in `components/`.

Avoid placing package-specific logic in the root workspace unless it is genuinely workspace-wide.

## Python and Tooling

- Python version: `>=3.13`
- Dependency manager: `uv`
- Workspace entrypoint: `engine/pyproject.toml`

Common commands:

```bash
uv sync
uv run ruff check .
uv run pytest
```

When possible, run commands from the narrowest affected package directory or target the smallest relevant test selection. Use the workspace root only when the change spans packages or the local package does not provide a narrower path.

## Change Strategy

- Minimize cross-package edits.
- Respect existing package boundaries before introducing new shared helpers.
- When changing one component or server, inspect its local `pyproject.toml`, source package layout, and any nearby tests before editing.
- If a fix appears to require touching both a component and shared library, confirm the dependency direction rather than duplicating code.

## Agent Working Documents

- Put agent-generated working documents under `engine/docs/agent/`.
- Do not commit files from `engine/docs/agent/` unless the user explicitly asks for that.
- This rule also applies to agent working documents created while operating on `frontend/`, unless a deeper project rule overrides it later.
