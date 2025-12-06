# Python Environment Standards

## Runtime & Package Management
- **Python version**: 3.14+ (use `python3.14` explicitly when needed)
- **Package manager**: Astral uv 0.9+ (NOT pip, poetry, or pipenv)
- **Virtual environments**: `uv venv` or `uv sync` (auto-creates venv)

### uv Commands
```bash
# Project init
uv init --python 3.14

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
1. `uv run ruff format .` — Format code (replaces Black)
2. `uv run ruff check . --fix` — Lint and auto-fix
3. `uv run mypy .` — Type check
4. `uv run bandit -r src/` — Security scan (SAST)
5. `uv run pip-audit` — Dependency vulnerability scan

### Ruff Configuration (v0.14+)
```toml
# pyproject.toml
[tool.ruff]
target-version = "py314"
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

### mypy Configuration (v1.19+, Strict)
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.14"
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

## Security Tools

### Bandit Configuration (v1.9+)
Static Application Security Testing (SAST) for Python code.
```toml
# pyproject.toml
[tool.bandit]
exclude_dirs = ["tests", "venv", ".venv"]
skips = ["B101"]  # Skip assert warnings in production code if needed

[tool.bandit.assert_used]
skips = ["*_test.py", "test_*.py"]
```

### pip-audit
Scans dependencies for known vulnerabilities.
```bash
# Scan current environment
uv run pip-audit

# Scan requirements file
uv run pip-audit -r requirements.txt

# Auto-fix vulnerabilities (upgrade to safe versions)
uv run pip-audit --fix

# Output as JSON for CI/CD
uv run pip-audit --format=json
```

### Installing Security Tools
```bash
uv add --dev bandit pip-audit
```

## Testing with pytest (v9.0+)
```toml
# pyproject.toml — Native TOML format (pytest 9.0+)
[tool.pytest]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = ["-ra", "--strict-markers", "--strict-config", "-v"]
filterwarnings = ["error"]
required_plugins = ["pytest-cov", "pytest-asyncio"]
```

### Recommended pytest Plugins (Dec 2025)
```bash
# Core testing (requires Python >=3.10)
uv add --dev pytest              # v9.0.1
uv add --dev pytest-cov          # v7.0.0
uv add --dev pytest-asyncio      # v1.3.0
uv add --dev pytest-mock         # v3.15.1
uv add --dev hypothesis          # v6.148+ (requires Python >=3.10.2)
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

### Pydantic Models (v2.12+)
```python
from pydantic import BaseModel, Field, ConfigDict, field_validator

class Config(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
    )

    name: str = Field(..., min_length=1)
    count: int = Field(default=0, ge=0)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be whitespace only")
        return v.strip()
```
