# Workflow

## Purpose

Use this checklist when implementing or extending a component under `engine/components`.

## Standard Path

1. Identify the owning component package and inspect:
   - `pyproject.toml`
   - `meta.py`
   - `config.yaml`
   - `src/...`
   - nearby tests
2. Start from `engine/components/astronverse-hello/` for the minimum skeleton unless a richer pattern is clearly required.
3. Pick one or two production components with the closest behavior and form contract.
4. Decide whether the task needs:
   - only Python atomics and `config.yaml`
   - type registration via `config_type.yaml` and `typesMg.register_types(...)`
   - local gateway or proxy access to repository-owned backend services
   - frontend adaptation because the requested form behavior is not already supported
5. Check backward compatibility before editing an existing atom:
   - keep existing parameter names, types, and semantics stable for shipped flows
   - only add new parameters if they have safe defaults
   - introduce a `v2` method or a new atom for incompatible behavior
6. Implement runtime behavior in Python first.
7. Update `config.yaml` so titles, tips, options, defaults, and comments match the intended designer UX.
8. Update `meta.py`:
   - register atomics
   - generate `meta.json`
   - register type metadata when the component emits reusable object outputs
9. Add the package to `engine/pyproject.toml` if this is a new component package.
10. Regenerate metadata.
11. Run targeted tests.
12. Review the generated metadata before declaring success.

## Classification Heuristics

### Plain atomic component

Use this path when the component has scalar inputs, standard file inputs, standard selects, or normal outputs.

Expected files:

- `config.yaml`
- `meta.py`
- `pyproject.toml`
- source package under `src/`
- tests

Default template:

- `engine/components/astronverse-hello/`

### Object-producing component

Use this path when outputs should become reusable typed variables in the designer.

Additional work:

- add `config_type.yaml`
- update `meta.py` to call `typesMg.register_types(...)`
- ensure output types match current variable-selection expectations

### Internal-service-backed component

Use this path when component logic depends on repository-owned backend services.

Additional work:

- inspect existing local gateway access patterns
- route through local proxy URLs
- avoid direct service endpoint calls from the component unless that is already the established local pattern

### New form capability request

Use this path when the desired UX cannot be represented by existing form types or current `params` semantics.

Additional work:

- confirm the limitation against current form constants and renderer support
- treat the task as coordinated engine and frontend work
- do not ship a new `formType` in component metadata without corresponding frontend support

## Reference Order

Use this priority when deciding what to trust:

1. `astronverse-hello` for the official minimum component template
2. Current production components with similar behavior
3. Current designer metadata consumers and serialization pipeline
4. Recent docs

## Minimal Commands

Run commands from the narrowest useful directory.

```bash
uv run --project engine python engine/components/<component-name>/meta.py
uv run --project engine python -m unittest engine/components/<component-name>/tests/<test_file>.py
```

If the component is part of a broader workspace test path, expand only as far as necessary.
