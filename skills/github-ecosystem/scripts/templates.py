#!/usr/bin/env python3
"""GitHub ecosystem templates as Python string constants.

All templates use f-string formatting with named placeholders.
"""

from __future__ import annotations

# =============================================================================
# PYTHON WORKFLOWS
# =============================================================================


def ci_python(
    project_name: str,
    package_name: str,
    python_versions: list[str],
    coverage_threshold: int = 80,
) -> str:
    """Generate Python CI workflow."""
    versions_yaml = ", ".join(f'"{v}"' for v in python_versions)
    return f'''name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{{{ github.workflow }}}}-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  quality:
    name: Code Quality
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Install uv
      uses: astral-sh/setup-uv@v4

    - name: Set up Python
      run: uv python install 3.14

    - name: Install dependencies
      run: uv sync

    - name: Check formatting
      run: uv run ruff format --check src/ tests/

    - name: Lint
      run: uv run ruff check src/ tests/

    - name: Type check
      run: uv run mypy src/

    - name: Security scan
      run: uv run bandit -r src/ -ll

  test:
    name: Test Python ${{{{ matrix.python-version }}}}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: [{versions_yaml}]

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Install uv
      uses: astral-sh/setup-uv@v4

    - name: Set up Python ${{{{ matrix.python-version }}}}
      run: uv python install ${{{{ matrix.python-version }}}}

    - name: Install dependencies
      run: uv sync

    - name: Run tests
      run: uv run pytest --cov={package_name} --cov-report=xml --cov-report=term-missing --cov-fail-under={coverage_threshold} -v

    - name: Upload coverage
      uses: codecov/codecov-action@v4
      if: matrix.python-version == '{python_versions[-1]}'
      with:
        file: ./coverage.xml
        fail_ci_if_error: false

  build:
    name: Build Package
    needs: [quality, test]
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Install uv
      uses: astral-sh/setup-uv@v4

    - name: Build package
      run: uv build

    - name: Check package
      run: uvx twine check dist/*

    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist
        path: dist/
'''


def release_python(project_name: str, package_name: str) -> str:
    """Generate Python release workflow."""
    return f'''name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write
  id-token: write

jobs:
  build:
    name: Build Package
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Install uv
      uses: astral-sh/setup-uv@v4

    - name: Build package
      run: uv build

    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist
        path: dist/

  release:
    name: Create GitHub Release
    needs: build
    runs-on: ubuntu-latest

    steps:
    - name: Download artifacts
      uses: actions/download-artifact@v4
      with:
        name: dist
        path: dist/

    - name: Create Release
      uses: softprops/action-gh-release@v2
      with:
        files: dist/*
        generate_release_notes: true

  # Uncomment to publish to PyPI
  # publish:
  #   name: Publish to PyPI
  #   needs: release
  #   runs-on: ubuntu-latest
  #   environment: pypi
  #
  #   steps:
  #   - name: Download artifacts
  #     uses: actions/download-artifact@v4
  #     with:
  #       name: dist
  #       path: dist/
  #
  #   - name: Publish to PyPI
  #     uses: pypa/gh-action-pypi-publish@release/v1
'''


# =============================================================================
# GO WORKFLOWS
# =============================================================================


def ci_go(
    project_name: str,
    go_module: str,
    go_versions: list[str],
    coverage_threshold: int = 80,
) -> str:
    """Generate Go CI workflow."""
    versions_yaml = ", ".join(f'"{v}"' for v in go_versions)
    return f'''name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{{{ github.workflow }}}}-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Go
      uses: actions/setup-go@v5
      with:
        go-version: '{go_versions[-1]}'

    - name: Run golangci-lint
      uses: golangci/golangci-lint-action@v6
      with:
        version: latest

  test:
    name: Test Go ${{{{ matrix.go-version }}}}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        go-version: [{versions_yaml}]

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Go ${{{{ matrix.go-version }}}}
      uses: actions/setup-go@v5
      with:
        go-version: ${{{{ matrix.go-version }}}}

    - name: Run tests
      run: go test -race -coverprofile=coverage.out -covermode=atomic ./...

    - name: Check coverage
      run: |
        COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{{print $3}}' | sed 's/%//')
        echo "Coverage: $COVERAGE%"
        if [ $(echo "$COVERAGE < {coverage_threshold}" | bc) -eq 1 ]; then
          echo "Coverage $COVERAGE% is below threshold {coverage_threshold}%"
          exit 1
        fi

    - name: Upload coverage
      uses: codecov/codecov-action@v4
      if: matrix.go-version == '{go_versions[-1]}'
      with:
        file: ./coverage.out
        fail_ci_if_error: false

  build:
    name: Build
    needs: [lint, test]
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Go
      uses: actions/setup-go@v5
      with:
        go-version: '{go_versions[-1]}'

    - name: Build
      run: go build -v ./...
'''


def release_go(project_name: str, go_module: str) -> str:
    """Generate Go release workflow using GoReleaser."""
    return f'''name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Set up Go
      uses: actions/setup-go@v5
      with:
        go-version: stable

    - name: Run GoReleaser
      uses: goreleaser/goreleaser-action@v6
      with:
        distribution: goreleaser
        version: latest
        args: release --clean
      env:
        GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
'''


# =============================================================================
# TYPESCRIPT WORKFLOWS
# =============================================================================


def ci_typescript(
    project_name: str,
    node_versions: list[str],
    package_manager: str = "npm",
    test_framework: str = "vitest",
    coverage_threshold: int = 80,
) -> str:
    """Generate TypeScript CI workflow."""
    versions_yaml = ", ".join(f'"{v}"' for v in node_versions)

    # Package manager commands
    install_cmd = {
        "npm": "npm ci",
        "pnpm": "pnpm install --frozen-lockfile",
        "yarn": "yarn install --frozen-lockfile",
    }.get(package_manager, "npm ci")

    run_cmd = {
        "npm": "npm run",
        "pnpm": "pnpm",
        "yarn": "yarn",
    }.get(package_manager, "npm run")

    # Test command
    test_cmd = f"{run_cmd} test -- --coverage" if test_framework == "vitest" else f"{run_cmd} test -- --coverage"

    return f'''name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{{{ github.workflow }}}}-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  quality:
    name: Code Quality
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '{node_versions[-1]}'
        cache: '{package_manager}'

    - name: Install dependencies
      run: {install_cmd}

    - name: Check formatting
      run: {run_cmd} format:check

    - name: Lint
      run: {run_cmd} lint

    - name: Type check
      run: {run_cmd} typecheck

  test:
    name: Test Node ${{{{ matrix.node-version }}}}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        node-version: [{versions_yaml}]

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Node.js ${{{{ matrix.node-version }}}}
      uses: actions/setup-node@v4
      with:
        node-version: ${{{{ matrix.node-version }}}}
        cache: '{package_manager}'

    - name: Install dependencies
      run: {install_cmd}

    - name: Run tests
      run: {test_cmd}

    - name: Upload coverage
      uses: codecov/codecov-action@v4
      if: matrix.node-version == '{node_versions[-1]}'
      with:
        fail_ci_if_error: false

  build:
    name: Build
    needs: [quality, test]
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '{node_versions[-1]}'
        cache: '{package_manager}'

    - name: Install dependencies
      run: {install_cmd}

    - name: Build
      run: {run_cmd} build

    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist
        path: dist/
'''


def release_typescript(project_name: str, package_manager: str = "npm") -> str:
    """Generate TypeScript release workflow."""
    install_cmd = {
        "npm": "npm ci",
        "pnpm": "pnpm install --frozen-lockfile",
        "yarn": "yarn install --frozen-lockfile",
    }.get(package_manager, "npm ci")

    run_cmd = {
        "npm": "npm run",
        "pnpm": "pnpm",
        "yarn": "yarn",
    }.get(package_manager, "npm run")

    return f'''name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write
  id-token: write

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '22'
        cache: '{package_manager}'

    - name: Install dependencies
      run: {install_cmd}

    - name: Build
      run: {run_cmd} build

    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist
        path: dist/

  release:
    name: Create GitHub Release
    needs: build
    runs-on: ubuntu-latest

    steps:
    - name: Download artifacts
      uses: actions/download-artifact@v4
      with:
        name: dist
        path: dist/

    - name: Create Release
      uses: softprops/action-gh-release@v2
      with:
        files: dist/*
        generate_release_notes: true

  # Uncomment to publish to npm
  # publish:
  #   name: Publish to npm
  #   needs: release
  #   runs-on: ubuntu-latest
  #
  #   steps:
  #   - name: Checkout code
  #     uses: actions/checkout@v4
  #
  #   - name: Set up Node.js
  #     uses: actions/setup-node@v4
  #     with:
  #       node-version: '22'
  #       registry-url: 'https://registry.npmjs.org'
  #       cache: '{package_manager}'
  #
  #   - name: Install dependencies
  #     run: {install_cmd}
  #
  #   - name: Build
  #     run: {run_cmd} build
  #
  #   - name: Publish
  #     run: npm publish --provenance --access public
  #     env:
  #       NODE_AUTH_TOKEN: ${{{{ secrets.NPM_TOKEN }}}}
'''


# =============================================================================
# DOCKER WORKFLOW
# =============================================================================


def docker_workflow(project_name: str, language: str) -> str:
    """Generate Docker build workflow."""
    return f'''name: Docker

on:
  push:
    branches: [main]
    tags:
      - 'v*'
  pull_request:
    branches: [main]

concurrency:
  group: ${{{{ github.workflow }}}}-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Container Registry
      if: github.event_name != 'pull_request'
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{{{ github.actor }}}}
        password: ${{{{ secrets.GITHUB_TOKEN }}}}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ghcr.io/${{{{ github.repository }}}}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{{{version}}}}
          type=semver,pattern={{{{major}}}}.{{{{minor}}}}
          type=raw,value=latest,enable=${{{{ github.ref == 'refs/heads/main' }}}}

    - name: Build and push
      uses: docker/build-push-action@v6
      with:
        context: .
        push: ${{{{ github.event_name != 'pull_request' }}}}
        tags: ${{{{ steps.meta.outputs.tags }}}}
        labels: ${{{{ steps.meta.outputs.labels }}}}
        platforms: linux/amd64,linux/arm64
        cache-from: type=gha
        cache-to: type=gha,mode=max
'''


# =============================================================================
# ISSUE TEMPLATES
# =============================================================================


def bug_report_template(project_name: str, language: str) -> str:
    """Generate bug report issue template."""
    code_examples = {
        "python": '''```python
# Minimal code sample to reproduce the issue
# Add your code here
```''',
        "go": '''```go
// Minimal code sample to reproduce the issue
// Add your code here
```''',
        "typescript": '''```typescript
// Minimal code sample to reproduce the issue
// Add your code here
```''',
    }
    code_block = code_examples.get(language, code_examples["python"])

    return f'''---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description

A clear and concise description of what the bug is.

## To Reproduce

Steps to reproduce the behavior:

1. Import '...'
2. Call method '...'
3. With parameters '...'
4. See error

## Expected Behavior

A clear and concise description of what you expected to happen.

## Actual Behavior

What actually happened.

## Code Sample

{code_block}

## Error Message

```
Paste the full error message and stack trace here
```

## Environment

- OS: [e.g., macOS 14.0, Ubuntu 22.04, Windows 11]
- Version: [e.g., 1.0.0]
- Runtime version: [e.g., Python 3.12, Go 1.22, Node 22]

## Additional Context

Add any other context about the problem here.

## Possible Solution

If you have suggestions on how to fix the bug, please describe them here.
'''


def feature_request_template(project_name: str, language: str) -> str:
    """Generate feature request issue template."""
    code_examples = {
        "python": '''```python
# Example of how the new feature would be used
```''',
        "go": '''```go
// Example of how the new feature would be used
```''',
        "typescript": '''```typescript
// Example of how the new feature would be used
```''',
    }
    code_block = code_examples.get(language, code_examples["python"])

    return f'''---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description

A clear and concise description of the feature you'd like to see.

## Problem Statement

Is your feature request related to a problem? Please describe.
Example: "I'm always frustrated when..."

## Proposed Solution

Describe the solution you'd like to see implemented.

## API Usage Example

Show how you would like to use this feature:

{code_block}

## Alternatives Considered

Describe any alternative solutions or features you've considered.

## Additional Context

Add any other context, screenshots, or examples about the feature request here.

## Potential Implementation

If you have ideas about how this could be implemented, share them here.

## Benefits

What are the benefits of implementing this feature?

-
-
-

## Breaking Changes

Would this feature introduce any breaking changes?

- [ ] Yes
- [ ] No

If yes, please describe what would break.
'''


def issue_config_template(project_name: str) -> str:
    """Generate issue template config."""
    return f'''blank_issues_enabled: false
contact_links:
  - name: Documentation
    url: https://github.com/OWNER/{project_name}#readme
    about: Read the documentation before opening an issue
  - name: Discussions
    url: https://github.com/OWNER/{project_name}/discussions
    about: Ask questions and discuss ideas
'''


# =============================================================================
# OTHER TEMPLATES
# =============================================================================


def pr_template() -> str:
    """Generate PR template."""
    return '''## Description

<!-- Provide a brief description of your changes -->

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code quality improvement
- [ ] Performance improvement

## Changes Made

<!-- List the specific changes you made -->

-
-
-

## Testing

<!-- Describe how you tested your changes -->

- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist

<!-- Mark items with an "x" when completed -->

- [ ] My code follows the project's code style
- [ ] I have run the formatter
- [ ] I have run the linter and all checks pass
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] I have added necessary documentation (if appropriate)
- [ ] My changes generate no new warnings

## Additional Notes

<!-- Add any additional notes, screenshots, or context -->
'''


def dependabot_template(language: str) -> str:
    """Generate dependabot.yml template."""
    ecosystems = {
        "python": '''  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "python"
    groups:
      python-dependencies:
        patterns:
          - "*"
''',
        "go": '''  - package-ecosystem: "gomod"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "go"
''',
        "typescript": '''  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "npm"
    groups:
      npm-dependencies:
        patterns:
          - "*"
''',
    }

    ecosystem_config = ecosystems.get(language, ecosystems["python"])

    return f'''version: 2
updates:
  # Maintain dependencies for GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"

  # Maintain dependencies for {language}
{ecosystem_config}'''


def codeowners_template(owners: list[str]) -> str:
    """Generate CODEOWNERS template."""
    owners_str = " ".join(owners) if owners else "@OWNER"
    return f'''# Default owners for everything
* {owners_str}

# Workflow files need admin review
.github/ {owners_str}
'''


def copilot_instructions_template(project_name: str, language: str) -> str:
    """Generate GitHub Copilot instructions."""
    language_specific = {
        "python": '''## Python Guidelines

- Use Python 3.14+ features and syntax
- Type hints are required for all functions
- Use `uv` for package management
- Follow ruff formatting and linting rules
- Use pytest for testing with high coverage
''',
        "go": '''## Go Guidelines

- Target Go 1.23+
- Follow standard Go project layout
- Use golangci-lint for linting
- Prefer table-driven tests
- Handle errors explicitly
''',
        "typescript": '''## TypeScript Guidelines

- Use strict TypeScript configuration
- Prefer functional patterns where appropriate
- Use ESLint and Prettier for code quality
- Write comprehensive tests with good coverage
''',
    }

    lang_section = language_specific.get(language, "")

    return f'''# {project_name} - Copilot Instructions

This file provides context to GitHub Copilot for better code suggestions.

## Project Overview

{project_name} is a {language} project following modern best practices.

{lang_section}
## Code Style

- Write clean, readable, maintainable code
- Prefer explicit over implicit
- Keep functions small and focused
- Add comments only when necessary (code should be self-documenting)
- Use descriptive names for variables and functions

## Testing

- Write tests for new functionality
- Aim for high test coverage
- Test edge cases and error conditions
- Use meaningful test names that describe the expected behavior

## Documentation

- Keep documentation up to date with code changes
- Document public APIs thoroughly
- Include examples in documentation when helpful
'''
