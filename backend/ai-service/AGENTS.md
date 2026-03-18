# AGENTS.md

## Scope

This file applies to everything under `backend/ai-service/`.

## Service Role

`backend/ai-service` is a standalone Python service built with FastAPI and managed with `uv`. In the larger monorepo, it is an AI capability service rather than a shared library package. Treat it as an independently runnable backend with its own tests, dependencies, and operational concerns.

## Local Architecture Map

The current codebase is organized around a fairly standard service split:

- `app/main.py`: FastAPI application entrypoint and app assembly.
- `app/routers/`: HTTP route definitions and request-level orchestration.
- `app/services/`: business logic and service coordination.
- `app/utils/`: external integrations and lower-level helpers.
- `app/schemas/`: request and response schemas.
- `app/models/`: persistence-facing models.
- `app/dependencies/`: dependency injection wiring.
- `app/middlewares/`: cross-cutting request behavior.
- `app/internal/`: internal/admin-style interfaces.
- `tests/`: service-level tests, organized by area.

When modifying behavior:

- keep HTTP concerns in routers,
- keep business rules in services,
- keep integration details and helper logic in utils,
- and add or update tests near the affected area.

Do not move business logic into route handlers just to make a small change faster.

## Python and Tooling

- Python version: `>=3.13`
- Dependency manager: `uv`
- Default install command: `uv sync`
- Run commands with `uv run ...`

Common commands:

```bash
uv sync
uv run pytest
uv run pytest tests/routers -q
uv run ruff check .
```

If a task only affects one module or test area, run the narrowest relevant test command first, then expand if needed.

## Change Strategy

- Prefer incremental changes over broad restructuring.
- Preserve the existing layering unless the task explicitly includes refactoring.
- If a change touches OCR, chat, captcha, points, or admin behavior, inspect the corresponding router, schema, service, and tests together before editing.
- Follow existing naming and file placement patterns instead of creating parallel abstractions.

## Agent Working Documents

- Put agent-generated working documents under `backend/ai-service/docs/agent/`.
- Do not commit files from `backend/ai-service/docs/agent/` unless the user explicitly asks for that.
- User-facing or permanent project documentation should go elsewhere only when the user explicitly asks.
