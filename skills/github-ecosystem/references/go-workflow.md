# Go CI/CD Workflow Patterns

## CI Workflow Structure

### Lint Job
Static analysis with golangci-lint:
- Uses official golangci-lint-action
- Runs comprehensive linter suite
- Caches results for faster runs

### Test Job
Matrix testing across Go versions:
- Default: 1.21, 1.22, 1.23
- Race detection enabled (`-race`)
- Coverage profiling
- Atomic coverage mode for accuracy

### Build Job
Compilation verification:
- Runs after lint and test pass
- Verifies successful compilation
- Uses latest stable Go version

## Release Workflow

### Trigger
- On push of tags matching `v*` pattern
- Example: `v1.0.0`, `v2.1.3`

### GoReleaser
Uses GoReleaser for:
- Cross-platform builds (Linux, macOS, Windows)
- Multiple architectures (amd64, arm64)
- Changelog generation
- GitHub Release creation
- Homebrew formula (optional)

## Tool Versions

| Tool | Version | Purpose |
|------|---------|---------|
| Go | 1.21+ | Runtime |
| golangci-lint | latest | Linting |
| GoReleaser | latest | Release automation |

## Coverage Threshold

Default: 80%

Calculated from coverage.out using:
```bash
go tool cover -func=coverage.out | grep total
```

## GoReleaser Setup

Create `.goreleaser.yaml` for customization:
```yaml
version: 2
builds:
  - main: ./cmd/main.go
    binary: myapp
    goos:
      - linux
      - darwin
      - windows
    goarch:
      - amd64
      - arm64
```

## Secrets Required

- `GITHUB_TOKEN` - Automatically provided
- No additional secrets needed for GitHub releases

## Customization Points

### Go Version Matrix
Edit the `matrix.go-version` in ci.yml:
```yaml
matrix:
  go-version: ["1.22", "1.23"]
```

### Linter Configuration
Create `.golangci.yml` in project root:
```yaml
linters:
  enable:
    - gofmt
    - govet
    - errcheck
    - staticcheck
    - gosimple
    - ineffassign
```

### CGO Handling
For projects requiring CGO:
```yaml
env:
  CGO_ENABLED: 1
```
