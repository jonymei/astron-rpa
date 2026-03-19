English | [简体中文](DEVELOPMENT.zh.md)
# Engine Component Development Reference

This document is the full component-development reference for `engine/components`.

Use it when the 10-minute guide is no longer enough and you need to make decisions about:

- component package structure
- designer-facing form metadata
- reusable object outputs and type metadata
- access to repository-owned backend services
- validation and documentation updates

If you only need the shortest runnable path, start with the [10-minute guide](README.md). `astronverse-hello` is the official recommended minimal template for new components.

## 1. Start From the Smallest Owning Package

Treat each component under `engine/components/` as its own package. Before editing, inspect the local package rather than assuming one repository-wide pattern is sufficient.

At minimum, check:

- `pyproject.toml`
- `meta.py`
- `config.yaml`
- `error.py`
- source files under `src/`
- local tests

For new components, the minimum expected layout is:

```text
engine/components/astronverse-your-component/
├── config.yaml
├── error.py
├── meta.py
├── pyproject.toml
├── src/astronverse/your_component/
│   ├── __init__.py
│   └── ...
└── tests/
```

If the component outputs a reusable typed object, also expect:

```text
├── config_type.yaml
└── meta_type.json
```

## 2. Choose the Right Reference Before Coding

Prefer production components with the closest behavior. One primary reference and at most one secondary reference is usually enough.

Useful reference groups:

- Official minimal template: [`astronverse-hello/`](./astronverse-hello/)
- Typed object outputs: [`astronverse-browser/`](./astronverse-browser/), [`astronverse-excel/`](./astronverse-excel/), [`astronverse-word/`](./astronverse-word/)
- Rich form metadata and dynamic fields: [`astronverse-word/`](./astronverse-word/), [`astronverse-excel/`](./astronverse-excel/), [`astronverse-encrypt/`](./astronverse-encrypt/), [`astronverse-email/`](./astronverse-email/), [`astronverse-vision/`](./astronverse-vision/)
- Internal service access through the local gateway: [`astronverse-ai/`](./astronverse-ai/), [`astronverse-openapi/`](./astronverse-openapi/)

Compare references by:

- runtime behavior
- user-facing form shape
- output variable behavior
- dependency on local gateway routing

Start from `astronverse-hello` by default, then borrow richer patterns only when the target component needs them.

## 3. Implement the Runtime Capability First

The Python implementation owns runtime behavior. Expose designer actions through `@atomicMg.atomic(...)` and keep the method contract coherent before you optimize wording or presentation.

Typical responsibilities in source files:

- implement the runtime action
- declare input and output structure in atomic metadata
- keep service calls, file I/O, and object creation inside the package

Keep user-facing titles, labels, tips, defaults, and option presentation in configuration unless the atomic library requires them directly in code.

## 4. Define Component Errors In `error.py`

Each component should have its own `error.py` as the component-domain exception surface.

Follow the pattern shown by `astronverse-hello` and other production components:

- import `BizCode`, `ErrorCode`, and baseline `BaseException`
- re-export `BaseException` from the component package's `error.py`
- define component-local `ErrorCode` constants there
- use `_()` for translated user-facing messages

Recommended split:

- `core.py` or equivalent holds runtime behavior
- `error.py` holds component error definitions
- the atom-facing module maps runtime failures into component exceptions

When raising component errors, prefer:

- first argument: translated user-facing message derived from the component `ErrorCode`
- second argument: developer-facing detail string for logs

Do not scatter raw exception text across the runtime code when the failure belongs to the component domain.

## 5. Use `config.yaml` as the Designer Contract Layer

`config.yaml` is the main user-facing contract for a component. It should be the first place you look when changing how a component appears in the designer.

Common responsibilities:

- `title`
- `comment`
- `icon`
- `helpManual`
- `inputList`
- `outputList`
- `options`

The practical model is:

1. Python atomic definitions establish the base structure
2. `config.yaml` fills in designer wording and configuration details
3. `meta.py` generates `meta.json`
4. the designer consumes generated metadata

When changing forms, review the generated `meta.json`, not just the source files.

## 6. Preserve Backward Compatibility For Shipped Flows

Treat existing atoms as backward-compatible contracts once they may be used by shipped flows.

Do not make incompatible parameter changes such as:

- renaming an existing parameter
- deleting an existing parameter
- changing an existing parameter type incompatibly
- changing the semantics of an existing parameter incompatibly

Allowed evolution paths:

- add a new parameter with a safe default value
- add a new `v2` method
- add a new atom or node to carry the incompatible behavior

If an incompatible change is required, preserve the existing atom and introduce a successor instead.

## 7. Stay Within Existing Form Types When Possible

Most component work should reuse current form semantics instead of introducing new ones.

Common existing form types include:

- normal input and variable input
- `SELECT`
- `RADIO`
- `SWITCH`
- `FILE`
- `TEXTAREAMODAL`
- `PICK`
- `CVPICK`
- `REMOTEPARAMS`
- `REMOTEFOLDERS`
- `RESULT`

Use `options` for discrete choices and `dynamics` for conditional visibility or behavior already supported by the current pipeline.

Good examples:

- show a file-path field only when a save mode is selected
- reveal extra settings only for one processing mode

Do not add a new `formType` or invent a new meaning for `formType.params` unless the requirement truly cannot fit the current vocabulary.

### When frontend adaptation is required

The task is no longer engine-only if any of these are true:

- you need a new `formType`
- current renderer behavior cannot express the desired UX
- you need a new `formType.params` meaning that current renderers or serializers do not understand

In those cases, state explicitly that the change also needs frontend work.

## 8. Register Reusable Object Types When Outputs Are Meant to Be Reused

Some components do not just return scalar values. They return objects that downstream nodes should be able to reference as typed variables.

When that is true, you need more than a normal `outputList`:

- add `config_type.yaml`
- register the type in `meta.py` with `typesMg.register_types(...)`
- generate the type metadata artifact
- ensure the output type name matches current variable-selection behavior

See:

- [`astronverse-browser/meta.py`](./astronverse-browser/meta.py)
- [`astronverse-browser/config_type.yaml`](./astronverse-browser/config_type.yaml)
- [`astronverse-word/meta.py`](./astronverse-word/meta.py)
- [`astronverse-excel/meta.py`](./astronverse-excel/meta.py)

If any of these pieces is missing, downstream variable handling can degrade or fail.

## 9. Use the Local Gateway for Repository-Owned Backend Services

When a component needs a repository-owned backend capability, the component should call a local route or gateway path rather than directly targeting a backend service endpoint.

The established pattern is a local URL such as:

```text
http://127.0.0.1:{GATEWAY_PORT}/api/...
```

See:

- [`astronverse-ai/src/astronverse/ai/api/llm.py`](./astronverse-ai/src/astronverse/ai/api/llm.py)
- [`astronverse-openapi/src/astronverse/openapi/client.py`](./astronverse-openapi/src/astronverse/openapi/client.py)

Rules:

- derive the local port from current configuration such as `GATEWAY_PORT` when that is the established pattern
- route through the local proxy chain when accessing repository-owned backend services
- do not hard-code direct service endpoints if a local route already exists

If no local gateway or proxy route exists for the required capability, treat the work as coordinated engine and backend work rather than solving it with a one-off direct call.

## 10. Wire New Components Into the Engine Workspace

Creating a component directory is not enough. For a new package, also update [`engine/pyproject.toml`](../pyproject.toml):

- add the package to `[project].dependencies`
- add the editable local path to `[tool.uv.sources]`

Without that step, `uv run --project engine ...` will not see the package correctly.

## 11. Generate Metadata and Run Focused Validation

At minimum, verify:

1. `meta.py` runs successfully
2. generated `meta.json` contains the intended inputs, outputs, titles, defaults, options, and comments
3. type metadata is generated when the component emits reusable objects
4. local tests pass
5. new packages are wired into the workspace
6. existing shipped atoms remain backward-compatible, or incompatible work is carried by a versioned successor
7. component-domain errors are defined in `error.py` and used consistently

Typical commands:

```bash
uv run --project engine python engine/components/<component-name>/meta.py
uv run --project engine python -m unittest engine/components/<component-name>/tests/<test_file>.py
```

Use narrower or broader checks only as needed by the package you touched.

## 12. Review Checklist Before Merging

- Did you start from `astronverse-hello` unless the task clearly needed a richer pattern?
- Did you copy the closest production pattern instead of inventing a new one?
- Did you define component-domain errors in `error.py`?
- Did you keep user-facing and developer-facing error information separated appropriately?
- Did you keep user-facing wording in `config.yaml`?
- Did you confirm the generated `meta.json`, not just the source config?
- Did you preserve backward compatibility for shipped flows?
- If incompatible behavior was required, did you carry it via a defaulted new parameter, a `v2` method, or a new atom?
- Did you stay within existing form types?
- If not, did you call out frontend adaptation explicitly?
- If the component outputs a reusable object, did you add type registration and type metadata?
- If the component calls a repository-owned backend capability, did you route through the local gateway or proxy?
- Did you run focused tests and metadata generation?

## 13. Relationship to the Project Skill

The project skill at [`.agents/skills/component-development/`](../../.agents/skills/component-development/) is a condensed operating guide for Codex. This document is the human-maintained reference that the skill should follow.

When component conventions change, update this reference first, then update the skill so both stay aligned.
