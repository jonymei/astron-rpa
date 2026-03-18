# AGENTS.md

## Scope and Precedence

- This file applies to the entire repository unless a deeper `AGENTS.md` overrides it.
- When working inside `backend/ai-service/` or `engine/`, follow the closer project-level `AGENTS.md` first.

## Repository Shape

This repository is a large monorepo, not a single application. The layout is intentionally mixed by runtime and responsibility:

- `frontend/`: Vue, TypeScript, Electron, and related frontend packages.
- `backend/`: service-style backends. This area is polyglot; not every service uses the same language or runtime.
- `engine/`: Python-based RPA engine workspace with many local packages managed together.
- `docker/`: deployment and local integration environment.
- `docs/`: shared repository-level documentation and assets.

Do not assume:

- one global build command,
- one global test command,
- one dependency manager for all subprojects,
- or one uniform architectural pattern across the monorepo.

Before editing, identify the smallest active subproject and work from its local conventions outward.

## Architecture Guidance For Agents

Use the repository as a federation of subsystems:

- `frontend/` is the client-facing desktop and web surface.
- `backend/` provides service APIs and business capabilities.
- `engine/` is the automation/runtime layer and contains reusable Python packages plus executable engine services.

When a task crosses boundaries, prefer tracing from the closest user-facing entrypoint inward:

1. Start from the touched app or service.
2. Identify the package or module that owns the behavior.
3. Limit changes to the smallest boundary that can solve the problem.
4. Only expand scope when the dependency direction makes it necessary.

Avoid monorepo-wide refactors unless the task explicitly asks for them.

## Working Rules

- Follow existing structure before introducing new folders or abstractions.
- Prefer local project commands over inventing root-level wrappers.
- For Python subprojects in this repo, `uv` is the default package and command runner unless the local project says otherwise.
- Keep generated process notes, design docs, debugging logs, and other agent working documents out of version control unless the user explicitly asks to commit them.

## Agent Working Documents

Default locations for agent-generated working documents:

- backend services: place them under that service's own `docs/agent/`
- `engine/` and `frontend/`: place them under `engine/docs/agent/`

These working documents should stay uncommitted by default and are ignored in git.
