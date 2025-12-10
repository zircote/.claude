# Python CI/CD Workflow Patterns

## CI Workflow Structure

### Quality Job
Runs linting, formatting, type checking, and security scans:
- **ruff format** - Code formatting check
- **ruff check** - Linting with auto-fix disabled
- **mypy** - Static type checking
- **bandit** - Security vulnerability scanning

### Test Job
Matrix testing across Python versions:
- Default: 3.10, 3.11, 3.12, 3.13, 3.14
- Uses `uv` for fast dependency installation
- Coverage reporting with fail threshold
- Uploads coverage to Codecov

### Build Job
Package building and validation:
- Runs after quality and test pass
- Uses `uv build` for package creation
- Validates with `twine check`
- Uploads artifacts for release

## Release Workflow

### Trigger
- On push of tags matching `v*` pattern
- Example: `v1.0.0`, `v2.1.3`

### Jobs
1. **Build** - Create distribution packages
2. **Release** - Create GitHub Release with artifacts
3. **Publish** (optional) - Upload to PyPI using trusted publishing

## Tool Versions

| Tool | Version | Purpose |
|------|---------|---------|
| ruff | 0.14+ | Formatting and linting |
| mypy | 1.18+ | Type checking |
| bandit | 1.8+ | Security scanning |
| pytest | 9.0+ | Testing |
| uv | 0.9+ | Package management |

## Coverage Threshold

Default: 80%

Customize in pyproject.toml:
```toml
[tool.coverage.report]
fail_under = 80
```

## Secrets Required

For PyPI publishing (optional):
- Configure trusted publishing on PyPI.org
- No secrets needed with OIDC authentication

## Customization Points

### Python Version Matrix
Edit the `matrix.python-version` in ci.yml:
```yaml
matrix:
  python-version: ["3.12", "3.13", "3.14"]
```

### Coverage Threshold
Pass `coverage_threshold` parameter when generating.

### Additional Quality Checks
Add steps to the quality job for:
- pip-audit (dependency vulnerabilities)
- safety (deprecated, use pip-audit)
- pyright (alternative type checker)
