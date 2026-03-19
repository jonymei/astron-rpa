# Verification

## Purpose

Use this checklist before claiming a component change is complete.

## Required Checks

1. Regenerate metadata.
2. Confirm the generated `meta.json` reflects the intended titles, tips, defaults, options, and outputs.
3. Run the smallest relevant automated tests.
4. Confirm new components are wired into `engine/pyproject.toml` when applicable.

## Type Metadata Checks

If the component emits reusable object types:

1. Regenerate type metadata through `meta.py`.
2. Confirm `config_type.yaml` and generated type metadata match the object name and intended variable behavior.

## Form Contract Checks

When changing forms:

1. Confirm requested UX fits existing form types.
2. Confirm `options` values and labels match runtime expectations.
3. Confirm `dynamics` hide and show the correct fields.
4. Confirm required fields still behave correctly when hidden or revealed.

If the request needs a new form type or new renderer semantics, do not mark the task complete as engine-only. Call out frontend adaptation explicitly.

## Internal Service Checks

If the component calls a repository-owned backend capability:

1. Confirm requests go through the local gateway or proxy route.
2. Confirm URLs are constructed from local gateway configuration such as `GATEWAY_PORT` when that is the established pattern.
3. Confirm the component does not directly call internal backend service endpoints unless that direct path is already an established local contract.

## Suggested Commands

```bash
uv run --project engine python engine/components/<component-name>/meta.py
uv run --project engine python -m unittest engine/components/<component-name>/tests/<test_file>.py
```

Add narrower or broader checks only as required by the package you touched.
