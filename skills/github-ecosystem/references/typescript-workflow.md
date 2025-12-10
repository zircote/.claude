# TypeScript CI/CD Workflow Patterns

## CI Workflow Structure

### Quality Job
Code quality checks:
- **format:check** - Prettier formatting verification
- **lint** - ESLint static analysis
- **typecheck** - TypeScript compiler type checking

### Test Job
Matrix testing across Node versions:
- Default: 18, 20, 22
- Detects package manager (npm, pnpm, yarn)
- Coverage reporting with framework-specific commands
- Uploads coverage to Codecov

### Build Job
Bundle creation and validation:
- Runs after quality and test pass
- Creates production build
- Uploads dist artifacts

## Release Workflow

### Trigger
- On push of tags matching `v*` pattern
- Example: `v1.0.0`, `v2.1.3`

### Jobs
1. **Build** - Create production bundle
2. **Release** - Create GitHub Release with artifacts
3. **Publish** (optional) - Publish to npm registry

## Package Manager Detection

Automatically detects from lockfiles:
- `pnpm-lock.yaml` → pnpm
- `yarn.lock` → yarn
- Default → npm

## Test Framework Detection

Automatically detects from devDependencies:
- `vitest` → Vitest
- `jest` → Jest

## Tool Versions

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 18+ | Runtime |
| TypeScript | 5.0+ | Type checking |
| ESLint | 8.0+ | Linting |
| Prettier | 3.0+ | Formatting |
| Vitest/Jest | latest | Testing |

## Coverage Threshold

Default: 80%

Configure in vitest.config.ts:
```typescript
export default defineConfig({
  test: {
    coverage: {
      thresholds: {
        lines: 80,
        branches: 80,
        functions: 80,
        statements: 80,
      },
    },
  },
});
```

## npm Publishing Setup

### Using npm Provenance
The generated workflow uses npm provenance for secure publishing:
- Requires npm registry configured for OIDC
- No npm token needed with provenance

### package.json Scripts
Expected npm scripts:
```json
{
  "scripts": {
    "build": "tsc && vite build",
    "test": "vitest",
    "lint": "eslint .",
    "format:check": "prettier --check .",
    "typecheck": "tsc --noEmit"
  }
}
```

## Secrets Required

For npm publishing (optional):
- `NPM_TOKEN` - npm access token (if not using provenance)

## Customization Points

### Node Version Matrix
Edit the `matrix.node-version` in ci.yml:
```yaml
matrix:
  node-version: ["20", "22"]
```

### Package Manager Commands
Adjust install and run commands based on your package manager.

### Monorepo Support
For monorepos (nx, turborepo):
```yaml
- name: Install dependencies
  run: pnpm install --frozen-lockfile

- name: Build
  run: pnpm turbo build
```
