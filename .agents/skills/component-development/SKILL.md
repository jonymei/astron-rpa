---
name: component-development
description: Build or extend components under `engine/components` in this repository, including Python atomic implementations, `config.yaml`, `meta.py`, generated `meta.json`, optional type metadata, and designer-facing form contracts. Use when Codex needs to add a new engine component, extend an existing component, adjust component form configuration, register reusable object types, or determine whether a requested form capability can be expressed with existing form types or requires frontend adaptation.
---

# Component Development

## Overview

Build component changes from existing production patterns, not from a blank-slate design. Treat the stable contract as the combination of Python atomic definitions, `config.yaml` overrides, generated `meta.json`, optional type metadata, and the current designer form pipeline.

Read only the reference file you need:

- For the step-by-step execution order, read `references/workflow.md`.
- For `inputList`, `outputList`, `formType`, `options`, and `dynamics`, read `references/form-contracts.md`.
- For example components and where to copy patterns from, read `references/component-patterns.md`.
- For the minimum validation and release checklist, read `references/verification.md`.

## Workflow

1. Identify the smallest owning package under `engine/components/<component-name>/`.
2. Classify the task before editing:
   - Plain atomic capability with normal inputs and outputs
   - Component that returns a reusable object type and needs type metadata
   - Component that needs non-trivial form behavior such as `SELECT`, `RADIO`, `FILE`, `PICK`, `CVPICK`, or `dynamics`
   - Component that depends on an internal backend service
   - Component request that cannot fit existing form types and may require frontend adaptation
3. Find the closest production component pattern before writing code.
4. Reuse existing form types whenever they already express the requested UX.
5. Add or update Python implementation, `config.yaml`, `meta.py`, tests, and `engine/pyproject.toml` in the narrowest scope necessary.
6. Generate metadata and run the smallest relevant verification set before claiming completion.

## Decision Gates

### Form Types

- Prefer existing form types and existing `formType.params` semantics.
- Treat a new `formType` or a new meaning for existing `params` as a cross-boundary change, not a component-only tweak.
- If the requested UX cannot be represented by the current form vocabulary, state explicitly that frontend adaptation is required in addition to engine changes.

### Internal Services

- When a component needs a repository-owned backend capability, route requests through the local gateway or local proxy chain.
- Do not hard-code direct calls to backend service endpoints when an existing local route pattern already exists.
- If no suitable local proxy path exists, surface that the task expands beyond `engine/components` and requires coordinated backend or frontend work.

### Reusable Object Outputs

- If the component outputs a reusable object such as a browser, document, or spreadsheet handle, add type registration and type metadata in addition to the normal component metadata.
- Keep type naming and registration aligned with existing variable-selection behavior rather than inventing parallel abstractions.

## Implementation Rules

- Treat `config.yaml` as the user-facing contract layer. Titles, tips, comments, option labels, default values, and dynamic visibility belong there unless the atomic library requires them in Python metadata.
- Keep Python implementations focused on runtime behavior. Keep designer wording and option presentation in configuration.
- Follow the nearest production component layout before introducing new files or helper modules.
- If you need a component to call an internal service, inspect current local gateway usage and reuse that structure.
- Do not assume the minimal example component reflects every production requirement. Verify against real shipped components before finalizing structure or field usage.

## Output Requirements

When you finish a task with this skill, report:

- Which existing component patterns you reused
- Whether the form contract stayed within existing form types
- Whether the change required or still requires frontend adaptation
- Whether the component uses local proxy routing for internal services
- Which metadata generation and tests you ran
