# Component Patterns

## Purpose

Use this file to choose the right production reference before editing.

## Pattern Map

### Minimal component layout

Inspect these files to confirm the expected package shape:

- `engine/components/astronverse-hello/pyproject.toml`
- `engine/components/astronverse-hello/meta.py`
- `engine/components/astronverse-hello/config.yaml`

`astronverse-hello` is the official recommended minimal template for new components.

Use it for:

- new component directory layout
- minimal `meta.py`
- minimal `config.yaml`
- minimal test shape

Before finalizing, still validate the design against production components with similar behavior when the component needs richer forms, type metadata, or internal service access.

### Reusable object outputs and type metadata

Inspect these packages when outputs should become typed variables:

- `engine/components/astronverse-browser/`
- `engine/components/astronverse-excel/`
- `engine/components/astronverse-word/`

Focus on:

- `meta.py`
- `config_type.yaml`
- generated type metadata

### Rich form contracts and dynamic fields

Inspect these packages when inputs need options, default values, or conditional visibility:

- `engine/components/astronverse-word/`
- `engine/components/astronverse-excel/`
- `engine/components/astronverse-encrypt/`
- `engine/components/astronverse-email/`
- `engine/components/astronverse-vision/`

Focus on:

- `config.yaml`
- atomic parameter metadata in source files
- generated `meta.json`

### Internal-service-backed components

Inspect these packages when the component needs repository-owned backend capabilities through local routing:

- `engine/components/astronverse-ai/`
- `engine/components/astronverse-openapi/`

Focus on:

- local gateway URL construction
- use of `GATEWAY_PORT`
- requests routed to `127.0.0.1:<port>/api/...`

Treat the stable pattern as: component code talks to a local gateway or proxy route, not directly to an internal backend service endpoint.

## How To Compare References

When picking a reference, compare these dimensions:

- Does it have the same kind of runtime side effect
- Does it expose the same kind of user-facing form
- Does it emit the same kind of output variable
- Does it depend on local gateway access

Prefer one primary reference and at most one secondary reference. Too many references usually means the task boundary is still unclear.
