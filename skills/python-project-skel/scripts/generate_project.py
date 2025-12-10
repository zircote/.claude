#!/usr/bin/env python3
"""Python project skeleton generator.

Generates production-ready Python project structures with modern tooling.
Templates are embedded as f-strings for zero dependencies.

Usage:
    python generate_project.py --name my-project
    python generate_project.py --name my-project --output-path /path/to/dir
    python generate_project.py --name my-project --output-mode tarball
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tarfile
from datetime import datetime
from pathlib import Path
from typing import NamedTuple


class ProjectConfig(NamedTuple):
    """Project configuration."""

    project_name: str
    package_name: str
    python_version: str
    license_type: str
    author_name: str
    author_email: str
    description: str


def validate_project_name(name: str) -> str:
    """Validate and normalize project name to kebab-case."""
    # Convert to lowercase and replace underscores/spaces with hyphens
    normalized = re.sub(r"[_\s]+", "-", name.lower().strip())
    # Remove any characters that aren't alphanumeric or hyphens
    normalized = re.sub(r"[^a-z0-9-]", "", normalized)
    # Remove leading/trailing hyphens and collapse multiple hyphens
    normalized = re.sub(r"-+", "-", normalized).strip("-")

    if not normalized:
        raise ValueError(f"Invalid project name: {name!r}")

    if not re.match(r"^[a-z][a-z0-9-]*$", normalized):
        raise ValueError(f"Project name must start with a letter: {normalized!r}")

    return normalized


def to_package_name(project_name: str) -> str:
    """Convert project name (kebab-case) to package name (snake_case)."""
    return project_name.replace("-", "_")


# =============================================================================
# TEMPLATES
# =============================================================================


def template_pyproject_toml(cfg: ProjectConfig) -> str:
    """Generate pyproject.toml content."""
    author_section = ""
    if cfg.author_name:
        email_part = f', email = "{cfg.author_email}"' if cfg.author_email else ""
        author_section = f"""
authors = [
    {{name = "{cfg.author_name}"{email_part}}}
]"""

    return f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{cfg.project_name}"
dynamic = ["version"]
description = "{cfg.description or f'A Python project: {cfg.project_name}'}"
readme = "README.md"
license = {{text = "{cfg.license_type}"}}{author_section}
keywords = []
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: {cfg.python_version}",
    "Typing :: Typed",
]
requires-python = ">={cfg.python_version}"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=9.0.0",
    "pytest-cov>=7.0.0",
    "pytest-asyncio>=1.0.0",
    "ruff>=0.14.0",
    "mypy>=1.18.0",
    "bandit>=1.8.0",
    "pip-audit>=2.9.0",
    "build>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/OWNER/{cfg.project_name}"
Documentation = "https://github.com/OWNER/{cfg.project_name}#readme"
Repository = "https://github.com/OWNER/{cfg.project_name}.git"
"Bug Tracker" = "https://github.com/OWNER/{cfg.project_name}/issues"

[project.scripts]
{cfg.project_name} = "{cfg.package_name}.main:main"

# UV/Astral dependency groups (modern tooling)
[dependency-groups]
dev = [
    "pytest>=9.0.0",
    "pytest-cov>=7.0.0",
    "pytest-asyncio>=1.0.0",
    "ruff>=0.14.0",
    "mypy>=1.18.0",
    "bandit>=1.8.0",
    "pip-audit>=2.9.0",
    "build>=1.0.0",
]

# Hatch build configuration
[tool.hatch.version]
path = "src/{cfg.package_name}/__init__.py"

[tool.hatch.build.targets.wheel]
packages = ["src/{cfg.package_name}"]

[tool.hatch.build.targets.sdist]
include = ["src/{cfg.package_name}/**/*.py"]

# Ruff - Linting and Formatting
[tool.ruff]
target-version = "py{cfg.python_version.replace('.', '')}"
line-length = 88
src = ["src", "tests"]

[tool.ruff.format]
docstring-code-format = true

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
    "S",      # flake8-bandit (security)
]
ignore = ["E501"]  # line length handled by formatter

[tool.ruff.lint.isort]
known-first-party = ["{cfg.package_name}"]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "S105", "S106", "ARG001"]

# mypy - Type Checking
[tool.mypy]
python_version = "{cfg.python_version}"
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

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

# pytest - Testing
[tool.pytest]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = ["-ra", "--strict-markers", "--strict-config", "-v"]
filterwarnings = ["error"]

# Coverage
[tool.coverage.run]
source = ["src/{cfg.package_name}"]
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

# Bandit - Security
[tool.bandit]
exclude_dirs = ["tests", ".venv", "venv"]
skips = ["B101"]  # assert_used OK in tests
'''


def template_makefile(cfg: ProjectConfig) -> str:
    """Generate Makefile content."""
    return f'''.PHONY: help install install-dev test test-cov lint typecheck security coverage format format-check clean build quality

.DEFAULT_GOAL := help

help:  ## Show this help message
	@echo '================================'
	@echo '{cfg.project_name} - Make Targets'
	@echo '================================'
	@echo ''
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Installation:'
	@grep -E '^(install|install-dev):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  \\033[36m%-18s\\033[0m %s\\n", $$1, $$2}}'
	@echo ''
	@echo 'Quality:'
	@grep -E '^(quality|lint|typecheck|security|format|format-check):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  \\033[36m%-18s\\033[0m %s\\n", $$1, $$2}}'
	@echo ''
	@echo 'Testing:'
	@grep -E '^(test|test-cov|coverage):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  \\033[36m%-18s\\033[0m %s\\n", $$1, $$2}}'
	@echo ''
	@echo 'Build:'
	@grep -E '^(build|clean):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  \\033[36m%-18s\\033[0m %s\\n", $$1, $$2}}'
	@echo ''

install:  ## Install package
	uv pip install -e .

install-dev:  ## Install with dev dependencies
	uv sync

test:  ## Run tests
	uv run pytest

test-cov:  ## Run tests with coverage
	uv run pytest --cov={cfg.package_name} --cov-report=html --cov-report=term-missing

lint:  ## Run linter (ruff)
	uv run ruff check src/ tests/

typecheck:  ## Run type checker (mypy)
	uv run mypy src/

security:  ## Run security scan (bandit)
	uv run bandit -r src/ -ll

format:  ## Format code (ruff)
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

format-check:  ## Check formatting
	uv run ruff format --check src/ tests/
	uv run ruff check src/ tests/

coverage:  ## Run tests with coverage threshold
	uv run pytest --cov={cfg.package_name} --cov-report=term-missing --cov-fail-under=80

quality:  ## Run all quality checks
	@echo "Running quality checks..."
	@echo ""
	@echo "1. Formatting..."
	@uv run ruff format src/ tests/
	@uv run ruff check --fix src/ tests/
	@echo "Formatting: PASS"
	@echo ""
	@echo "2. Linting..."
	@uv run ruff check src/ tests/
	@echo "Linting: PASS"
	@echo ""
	@echo "3. Type checking..."
	@uv run mypy src/
	@echo "Type checking: PASS"
	@echo ""
	@echo "4. Security..."
	@uv run bandit -r src/ -ll -q
	@echo "Security: PASS"
	@echo ""
	@echo "5. Tests with coverage..."
	@uv run pytest --cov={cfg.package_name} --cov-report=term-missing --cov-fail-under=80 -q
	@echo ""
	@echo "ALL QUALITY CHECKS PASSED"

build:  ## Build distribution packages
	uv run python -m build

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {{}} + 2>/dev/null || true
'''


def template_readme(cfg: ProjectConfig) -> str:
    """Generate README.md content."""
    return f'''# {cfg.project_name}

{cfg.description or f'A Python project: {cfg.project_name}'}

## Installation

```bash
# Using uv (recommended)
uv add {cfg.project_name}

# Using pip
pip install {cfg.project_name}
```

## Development

```bash
# Clone the repository
git clone https://github.com/OWNER/{cfg.project_name}.git
cd {cfg.project_name}

# Install with dev dependencies
uv sync

# Run tests
make test

# Run all quality checks
make quality
```

## Usage

```python
from {cfg.package_name} import main

# Example usage
main()
```

## License

{cfg.license_type}
'''


def template_license_mit(cfg: ProjectConfig) -> str:
    """Generate MIT LICENSE content."""
    year = datetime.now().year
    holder = cfg.author_name or "The Authors"
    return f'''MIT License

Copyright (c) {year} {holder}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


def template_init_py(cfg: ProjectConfig) -> str:
    """Generate __init__.py content."""
    return f'''"""{cfg.description or cfg.project_name}"""

__version__ = "0.1.0"
__all__ = ["__version__"]
'''


def template_main_py(cfg: ProjectConfig) -> str:
    """Generate main.py content."""
    return f'''"""Main entry point for {cfg.package_name}."""

from __future__ import annotations


def main() -> int:
    """Application entry point.

    Returns:
        Exit code (0 for success).
    """
    print("Hello from {cfg.package_name}!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def template_py_typed() -> str:
    """Generate py.typed marker content."""
    return ""  # Empty file is valid PEP 561 marker


def template_conftest_py(cfg: ProjectConfig) -> str:
    """Generate conftest.py content."""
    return f'''"""Shared pytest fixtures for {cfg.package_name} tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_fixture() -> str:
    """Example fixture - replace with project-specific fixtures."""
    return "sample_value"
'''


def template_test_main_py(cfg: ProjectConfig) -> str:
    """Generate test_main.py content."""
    return f'''"""Tests for {cfg.package_name}.main module."""

from __future__ import annotations

from {cfg.package_name} import __version__
from {cfg.package_name}.main import main


def test_version() -> None:
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_main_returns_zero() -> None:
    """Test that main() returns 0."""
    result = main()
    assert result == 0
'''


def template_tests_init_py() -> str:
    """Generate tests/__init__.py content."""
    return '"""Test suite."""\n'


# =============================================================================
# PROJECT GENERATION
# =============================================================================


def create_project_structure(
    project_name: str,
    package_name: str | None = None,
    python_version: str = "3.14",
    license_type: str = "MIT",
    author_name: str = "",
    author_email: str = "",
    description: str = "",
    output_path: Path | None = None,
) -> Path:
    """Create complete project structure.

    Args:
        project_name: Kebab-case project name.
        package_name: Snake_case package name (derived if not provided).
        python_version: Minimum Python version.
        license_type: License type (MIT, Apache-2.0, etc.).
        author_name: Author name for pyproject.toml.
        author_email: Author email for pyproject.toml.
        description: Project description.
        output_path: Output directory (uses CWD/project_name if not specified).

    Returns:
        Path to the created project directory.
    """
    # Validate and normalize names
    project_name = validate_project_name(project_name)
    if package_name is None:
        package_name = to_package_name(project_name)

    # Determine output path
    if output_path is None:
        project_path = Path.cwd() / project_name
    else:
        project_path = Path(output_path).resolve()
        if project_path.name != project_name:
            project_path = project_path / project_name

    # Check if directory already exists
    if project_path.exists():
        raise FileExistsError(f"Directory already exists: {project_path}")

    # Create config
    cfg = ProjectConfig(
        project_name=project_name,
        package_name=package_name,
        python_version=python_version,
        license_type=license_type,
        author_name=author_name,
        author_email=author_email,
        description=description,
    )

    # Create directory structure
    src_dir = project_path / "src" / package_name
    tests_dir = project_path / "tests"

    src_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)

    # Write files
    files = {
        project_path / "pyproject.toml": template_pyproject_toml(cfg),
        project_path / "Makefile": template_makefile(cfg),
        project_path / "README.md": template_readme(cfg),
        project_path / "LICENSE": template_license_mit(cfg),
        src_dir / "__init__.py": template_init_py(cfg),
        src_dir / "main.py": template_main_py(cfg),
        src_dir / "py.typed": template_py_typed(),
        tests_dir / "__init__.py": template_tests_init_py(),
        tests_dir / "conftest.py": template_conftest_py(cfg),
        tests_dir / "test_main.py": template_test_main_py(cfg),
    }

    for file_path, content in files.items():
        file_path.write_text(content)

    return project_path


def create_tarball(project_path: Path, output_dir: Path | None = None) -> Path:
    """Create .tar.gz from project directory.

    Args:
        project_path: Path to the project directory.
        output_dir: Directory for the tarball (uses CWD if not specified).

    Returns:
        Path to the created tarball.
    """
    if output_dir is None:
        output_dir = Path.cwd()

    tarball_name = f"{project_path.name}.tar.gz"
    tarball_path = output_dir / tarball_name

    with tarfile.open(tarball_path, "w:gz") as tar:
        tar.add(project_path, arcname=project_path.name)

    # Clean up the temporary directory
    shutil.rmtree(project_path)

    return tarball_path


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a production-ready Python project skeleton.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --name my-project
  %(prog)s --name my-project --python-version 3.12
  %(prog)s --name my-project --output-mode tarball
  %(prog)s --name my-project --output-path /path/to/projects
        """,
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Project name (kebab-case, e.g., my-awesome-project)",
    )
    parser.add_argument(
        "--package-name",
        help="Package name (snake_case, derived from project name if not specified)",
    )
    parser.add_argument(
        "--python-version",
        default="3.14",
        help="Minimum Python version (default: 3.14)",
    )
    parser.add_argument(
        "--license",
        default="MIT",
        dest="license_type",
        help="License type (default: MIT)",
    )
    parser.add_argument(
        "--author",
        default="",
        help="Author name",
    )
    parser.add_argument(
        "--email",
        default="",
        help="Author email",
    )
    parser.add_argument(
        "--description",
        default="",
        help="Project description",
    )
    parser.add_argument(
        "--output-mode",
        choices=["cwd", "path", "tarball"],
        default="cwd",
        help="Output mode: cwd (current directory), path (specified path), tarball (.tar.gz)",
    )
    parser.add_argument(
        "--output-path",
        help="Output path (used with --output-mode path or tarball)",
    )

    args = parser.parse_args()

    try:
        # Determine output path based on mode
        output_path = None
        if args.output_mode == "path" and args.output_path:
            output_path = Path(args.output_path)
        elif args.output_mode == "tarball":
            # Create in temp location first
            import tempfile

            output_path = Path(tempfile.mkdtemp())

        # Create project
        project_path = create_project_structure(
            project_name=args.name,
            package_name=args.package_name,
            python_version=args.python_version,
            license_type=args.license_type,
            author_name=args.author,
            author_email=args.email,
            description=args.description,
            output_path=output_path,
        )

        # Handle tarball mode
        if args.output_mode == "tarball":
            tarball_dir = Path(args.output_path) if args.output_path else Path.cwd()
            tarball_path = create_tarball(project_path, tarball_dir)
            print(f"Created tarball: {tarball_path}")
        else:
            print(f"Created project: {project_path}")
            print()
            print("Next steps:")
            print(f"  cd {project_path.name}")
            print("  uv sync")
            print("  make test")

        return 0

    except (ValueError, FileExistsError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
