# Form Contracts

## Purpose

This file documents the stable component-side contract that the designer consumes. It focuses on what component authors must preserve or extend carefully.

## Core Model

Component metadata is materialized into `meta.json`. The practical contract is:

- Python atomic definitions establish the base parameter and output structure
- `config.yaml` fills in user-facing wording and configuration details
- generated `meta.json` is what the designer actually reads

Treat `meta.json` as a generated artifact and `config.yaml` as the primary place for user-facing metadata.

## Key Fields

### `inputList`

Use `inputList` to define designer-facing inputs. Stable fields commonly include:

- `key`
- `title`
- `tip`
- `types`
- `formType`
- `default`
- `required`
- `options`
- `dynamics`

### `outputList`

Use `outputList` to define outputs that become downstream variables. For normal outputs, the designer expects `RESULT` form behavior. For reusable object outputs, also add type metadata registration.

## Existing Form Types

Prefer existing supported form types such as:

- standard input and variable input
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

Do not invent a new form type when a current type plus options or dynamics already expresses the requirement.

## Options

Use `options` for discrete choices such as radios, selects, or switches. Keep labels user-facing and values stable for runtime logic.

Good uses:

- mode selection
- provider selection
- units, strategies, or boolean-like choices

Avoid:

- encoding business logic only in labels
- mixing persisted machine values with display-only text in the same field

## Dynamics

Use `dynamics` for conditional visibility or behavior already supported by the current form pipeline.

Good uses:

- show a path input only when a save flag is enabled
- reveal extra configuration only for a selected mode

Rules:

- keep expressions simple and traceable to nearby fields
- copy an established pattern before introducing a new expression shape
- verify that hidden required fields behave correctly after generation

## When Frontend Adaptation Is Required

Frontend changes are required when any of these are true:

- the desired form control needs a new `formType`
- the desired UX needs renderer behavior that current supported types do not provide
- the desired change relies on a new meaning of `formType.params` that current renderers and serializers do not understand
- the generated metadata shape is valid JSON but not understood by the current designer pipeline

In those cases, state clearly that the task is no longer engine-only.

## Object Types And Variable Selection

If the component outputs a reusable object, keep three things aligned:

1. Python output type
2. generated output metadata in `meta.json`
3. type registration and generated type metadata

If one of these is missing, downstream variable selection may degrade or fail.
