# Python Environment Standards

## Runtime & Package Management
- **Python version**: 3.13+ (use `python3.13` explicitly when needed)
- **Package manager**: Astral uv (NOT pip, poetry, or pipenv)
- **Virtual environments**: `uv venv` or `uv sync` (auto-creates venv)

### uv Commands
```bash
# Project init
uv init --python 3.13

# Dependencies
uv add <package>              # Add dependency
uv add --dev <package>        # Add dev dependency
uv remove <package>           # Remove dependency
uv sync                       # Install all deps from pyproject.toml
uv lock                       # Update lock file

# Running
uv run python script.py       # Run with project's venv
uv run pytest                 # Run tools in venv context
```

## Code Quality Pipeline
Execute in this order:
1. `uv run ruff format .` — Format code
2. `uv run ruff check . --fix` — Lint and auto-fix
3. `uv run mypy .` — Type check
4. `uv run black .` — Format code

### Ruff Configuration
```toml
# pyproject.toml
[tool.ruff]
target-version = "py313"
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
]
ignore = ["E501"]  # line length handled by formatter

[tool.ruff.lint.isort]
known-first-party = ["src"]
```

### mypy Configuration (Strict)
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_configs = true
show_error_codes = true
plugins = []  # Add "pydantic.mypy" if using Pydantic
```

## Testing with pytest
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "-v",
]
filterwarnings = ["error"]
```

### Recommended pytest Plugins
```bash
uv add --dev pytest pytest-cov pytest-asyncio pytest-mock hypothesis
```

### Coverage Configuration
```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
fail_under = 80
```

## Docstrings (Google Style)
```python
def function_name(param1: str, param2: int) -> bool:
    """Short description of function.

    Longer description if needed. Explain behavior,
    side effects, or important details.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param2 is negative.

    Example:
        >>> function_name("test", 42)
        True
    """
```

## Project Structure
```
project-root/
├── pyproject.toml          # Single source of config
├── uv.lock                  # Locked dependencies
├── README.md
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── py.typed         # PEP 561 marker
│       └── module.py
└── tests/
    ├── __init__.py
    ├── conftest.py          # Shared fixtures
    └── test_module.py
```

## Type Annotation Patterns
```python
from typing import TypeAlias, Self
from collections.abc import Callable, Iterator, Sequence

# Type aliases (Python 3.12+)
JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]

# Generic with constraints
from typing import TypeVar
T = TypeVar("T", bound="BaseClass")

# Self type for fluent interfaces
class Builder:
    def with_name(self, name: str) -> Self:
        self.name = name
        return self
```

## Common Patterns

### Async Context Manager
```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

@asynccontextmanager
async def managed_resource() -> AsyncIterator[Resource]:
    resource = await Resource.create()
    try:
        yield resource
    finally:
        await resource.close()
```

### Pydantic Models (if using)
```python
from pydantic import BaseModel, Field, ConfigDict

class Config(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)

    name: str = Field(..., min_length=1)
    count: int = Field(default=0, ge=0)
```
