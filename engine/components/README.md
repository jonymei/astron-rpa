English | [简体中文](README.zh.md)
# Build an RPA Component in 10 Minutes

This guide focuses on one thing: getting a runnable, testable component in this repository that can generate `meta.json`.

If you want a real minimal example, start with [`astronverse-hello/`](./astronverse-hello/).
If you need the full reference for form contracts, type metadata, gateway-backed components, and validation, read the [component development reference](./DEVELOPMENT.md).

## 1. Prepare the Environment

From the repository root:

```bash
uv sync --project engine
```

This creates and syncs the virtual environment for `engine`.

## 2. Understand the Smallest Possible Component

Example directory:

```text
engine/components/astronverse-hello/
├── config.yaml
├── meta.py
├── pyproject.toml
├── src/astronverse/hello/
│   ├── __init__.py
│   └── hello.py
└── tests/test_hello.py
```

What each file does:

- `pyproject.toml`: package name, dependencies, and build config
- `src/astronverse/hello/hello.py`: actual component code
- `config.yaml`: designer-facing metadata such as title, comment, and icon
- `meta.py`: generates `meta.json`
- `tests/test_hello.py`: minimal behavior test

## 3. Write a Hello World Component Method

The core code lives in [`astronverse-hello/src/astronverse/hello/hello.py`](./astronverse-hello/src/astronverse/hello/hello.py):

```python
from astronverse.actionlib.atomic import atomicMg


class Hello:
    @staticmethod
    @atomicMg.atomic(
        "Hello",
        outputList=[atomicMg.param("greeting", types="Str")],
    )
    def say_hello(name: str = "World") -> str:
        return f"Hello, {name}!"
```

The two important ideas are:

- expose a method to the designer with `@atomicMg.atomic(...)`
- define inputs from the Python function signature and outputs with `outputList`

## 4. Generate the Component `meta.json`

Run:

```bash
uv run --project engine python engine/components/astronverse-hello/meta.py
```

That generates or updates:

```text
engine/components/astronverse-hello/meta.json
```

## 5. Wire the Component into Engine

Creating the component directory is not enough. You also need to update [`engine/pyproject.toml`](../pyproject.toml):

- add the package name to `[project].dependencies`
- add the local editable path to `[tool.uv.sources]`

Example:

```toml
"astronverse-hello",
astronverse-hello = {path = "./components/astronverse-hello", editable = true}
```

Without that step, `uv run --project engine ...` will not see your new component.

## 6. Test the Component

Run:

```bash
uv run --project engine python -m unittest engine/components/astronverse-hello/tests/test_hello.py
```

## 7. Copy This Template for Your Own Component

The fastest path is:

1. Copy `engine/components/astronverse-hello/`
2. Rename the directory to `astronverse-your-component`
3. Rename `astronverse.hello`, `Hello`, and `say_hello`
4. Update `config.yaml` and the root `engine/pyproject.toml`
5. Re-run the test and `meta.py`

### Does every new component need `meta.py`?

In the current repository conventions, yes. `meta.py` exports `meta.json`.

### Do I need frontend work first?

Not for the minimal path. First make the Python component, tests, and `meta.json` work. Then evaluate whether the designer side needs anything else.

## Next

- Explore the example component: [`astronverse-hello/`](./astronverse-hello/)
- Read the full reference: [`DEVELOPMENT.md`](./DEVELOPMENT.md)
- Go back to the engine script guide: [`../README.md`](../README.md)
