# GitHub Actions Standards

## Specialist Agents

| Agent | Category | Use For |
|-------|----------|---------|
| `devops-engineer` | 03-infrastructure | CI/CD pipeline design, workflow optimization |
| `deployment-engineer` | 03-infrastructure | Deployment workflows, release automation |
| `sre-engineer` | 03-infrastructure | Reliability, monitoring integration |
| `security-engineer` | 03-infrastructure | Workflow security, secret management |
| `cloud-architect` | 03-infrastructure | Multi-cloud deployments, OIDC setup |

## Claude Code Tool Authorization

Recommended tool authorizations for GitHub Actions tasks:

```json
{
  "permissions": {
    "allow": [
      "Bash(gh:*)",
      "Bash(git:*)",
      "Bash(act:*)",
      "WebSearch",
      "WebFetch"
    ]
  }
}
```

### Tool Usage Patterns

```bash
# Workflow management
gh workflow list                    # List all workflows
gh workflow view [name]             # View workflow details
gh workflow run [name]              # Manually trigger workflow
gh workflow disable [name]          # Disable a workflow

# Run inspection
gh run list                         # List recent runs
gh run view [id]                    # View run details
gh run view [id] --log              # View run logs
gh run watch [id]                   # Watch run in progress
gh run rerun [id]                   # Re-run a workflow

# Secret management
gh secret list                      # List repository secrets
gh secret set [name]                # Set a secret
gh secret delete [name]             # Delete a secret

# Environment management
gh api repos/{owner}/{repo}/environments  # List environments

# Local testing with act
act -l                              # List workflow jobs
act -j [job-name]                   # Run specific job
act push                            # Simulate push event
act pull_request                    # Simulate PR event
act -s GITHUB_TOKEN=[token]         # Pass secrets
```

## Version Discovery (CRITICAL)

**Reference**: `~/.claude/includes/version-discovery.md`

Before specifying ANY action version, verify using the discovery protocol:

1. **Use context7 MCP** (if available) for authoritative docs
2. **Use WebSearch**: `"actions/[name] latest version 2025"`
3. **Verify at source**: `github.com/actions/[name]/releases`

### Common Actions Discovery

| Action | Search Query | Releases Page |
|--------|--------------|---------------|
| `actions/checkout` | "actions/checkout latest version" | github.com/actions/checkout/releases |
| `actions/setup-node` | "actions/setup-node current version" | github.com/actions/setup-node/releases |
| `actions/setup-python` | "actions/setup-python latest" | github.com/actions/setup-python/releases |
| `actions/setup-go` | "actions/setup-go current version" | github.com/actions/setup-go/releases |
| `actions/cache` | "github actions cache latest" | github.com/actions/cache/releases |
| `actions/upload-artifact` | "actions/upload-artifact current" | github.com/actions/upload-artifact/releases |
| `actions/download-artifact` | "actions/download-artifact latest" | github.com/actions/download-artifact/releases |

**Never hardcode versions from memory.** Always discover current versions.

## Workflow Fundamentals

### File Structure
```
.github/
  workflows/
    ci.yml              # Continuous Integration
    cd.yml              # Continuous Deployment
    release.yml         # Release automation
    codeql.yml          # Security scanning
  actions/
    custom-action/      # Composite actions
      action.yml
```

### Workflow Anatomy
```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@vX  # Discover current version
      - name: Build
        run: npm run build
```

### Trigger Events

| Event | Use Case |
|-------|----------|
| `push` | CI on commits to specific branches |
| `pull_request` | PR validation, status checks |
| `workflow_dispatch` | Manual triggers with inputs |
| `schedule` | Cron-based automation |
| `release` | Release-triggered deployments |
| `workflow_call` | Reusable workflow invocation |
| `repository_dispatch` | External event triggers |

### Schedule Syntax (Cron)
```yaml
on:
  schedule:
    - cron: '0 0 * * *'    # Daily at midnight UTC
    - cron: '0 */6 * * *'  # Every 6 hours
    - cron: '0 0 * * 0'    # Weekly on Sunday
```

## GitHub Actions Permissions (GITHUB_TOKEN)

### Default Permissions
```yaml
permissions:
  contents: read
  metadata: read
```

### Permission Reference

| Permission | Values | Use Case |
|------------|--------|----------|
| `contents` | read/write | Repository content access |
| `pull-requests` | read/write | PR comments, labels, reviews |
| `issues` | read/write | Issue management |
| `packages` | read/write | GitHub Packages (GHCR) |
| `id-token` | write | OIDC token for cloud auth |
| `actions` | read/write | Workflow management |
| `security-events` | read/write | Code scanning uploads |
| `deployments` | read/write | Deployment status |
| `statuses` | read/write | Commit status checks |

### Permission Patterns by Use Case

```yaml
# Read-only CI (most restrictive)
permissions:
  contents: read

# PR automation (comments, labels)
permissions:
  contents: read
  pull-requests: write

# Release and publish
permissions:
  contents: write
  packages: write

# OIDC cloud authentication
permissions:
  id-token: write
  contents: read

# Code scanning
permissions:
  contents: read
  security-events: write

# Full deployment workflow
permissions:
  contents: read
  id-token: write
  deployments: write
  packages: write
```

### Job-Level vs Workflow-Level
```yaml
# Workflow-level (applies to all jobs)
permissions:
  contents: read

jobs:
  deploy:
    # Job-level override (more specific)
    permissions:
      contents: read
      id-token: write
```

## Self-Hosted Runners

### Setup
```bash
# Download runner (check GitHub for current version)
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64.tar.gz -L [runner-url]
tar xzf ./actions-runner-linux-x64.tar.gz

# Configure
./config.sh --url https://github.com/[org]/[repo] --token [token]

# Run as service
sudo ./svc.sh install
sudo ./svc.sh start
```

### Labels and Targeting
```yaml
jobs:
  build:
    runs-on: [self-hosted, linux, x64, gpu]  # Multiple labels
```

### Runner Groups (Organization)
```yaml
jobs:
  deploy:
    runs-on:
      group: production-runners
      labels: [self-hosted, linux]
```

### Security Considerations
- Use separate runners for public/private repos
- Avoid running untrusted code on self-hosted runners
- Use ephemeral runners for sensitive workloads
- Regularly update runner software
- Isolate runner environments (containers/VMs)

## Reusable Workflows

### Creating a Reusable Workflow
```yaml
# .github/workflows/reusable-build.yml
name: Reusable Build

on:
  workflow_call:
    inputs:
      node-version:
        description: 'Node.js version'
        required: true
        type: string
      environment:
        required: false
        type: string
        default: 'development'
    secrets:
      NPM_TOKEN:
        required: true
    outputs:
      artifact-name:
        description: 'Name of uploaded artifact'
        value: ${{ jobs.build.outputs.artifact }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      artifact: ${{ steps.upload.outputs.name }}
    steps:
      - uses: actions/checkout@vX
      - uses: actions/setup-node@vX
        with:
          node-version: ${{ inputs.node-version }}
      - run: npm ci
        env:
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
      - run: npm run build
      - id: upload
        uses: actions/upload-artifact@vX
        with:
          name: build-${{ github.sha }}
          path: dist/
```

### Calling a Reusable Workflow
```yaml
jobs:
  call-build:
    uses: ./.github/workflows/reusable-build.yml
    with:
      node-version: '20'
      environment: production
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
    # Or inherit all secrets
    secrets: inherit
```

### Reusable Workflow Limitations
- Max 4 levels of nesting
- Max 20 reusable workflows per workflow file
- Environment variables don't propagate (pass as inputs)
- Cannot use `workflow_dispatch` inputs directly

## Composite Actions

### When to Use
| Composite Action | Reusable Workflow |
|------------------|-------------------|
| Shared steps within a job | Shared entire jobs |
| No secrets handling needed | Secrets handling required |
| Simpler, fewer dependencies | Complex multi-job logic |
| Published to marketplace | Organization-internal |

### Creating a Composite Action
```yaml
# .github/actions/setup-project/action.yml
name: 'Setup Project'
description: 'Setup Node.js and install dependencies'

inputs:
  node-version:
    description: 'Node.js version'
    required: false
    default: '20'
  install-command:
    description: 'Install command'
    required: false
    default: 'npm ci'

outputs:
  cache-hit:
    description: 'Whether cache was hit'
    value: ${{ steps.cache.outputs.cache-hit }}

runs:
  using: 'composite'
  steps:
    - uses: actions/setup-node@vX
      with:
        node-version: ${{ inputs.node-version }}
        cache: 'npm'

    - id: cache
      uses: actions/cache@vX
      with:
        path: node_modules
        key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}

    - if: steps.cache.outputs.cache-hit != 'true'
      shell: bash
      run: ${{ inputs.install-command }}
```

### Using a Composite Action
```yaml
- uses: ./.github/actions/setup-project
  with:
    node-version: '20'
```

## OIDC & Cloud Authentication

### GitHub OIDC Provider
OIDC eliminates long-lived secrets by using short-lived tokens.

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@vX
```

### AWS Integration
```yaml
- uses: aws-actions/configure-aws-credentials@vX
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
    aws-region: us-east-1
    # No access keys needed!
```

AWS IAM Trust Policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:org/repo:*"
        }
      }
    }
  ]
}
```

### GCP Integration
```yaml
- uses: google-github-actions/auth@vX
  with:
    workload_identity_provider: projects/123456789/locations/global/workloadIdentityPools/github/providers/github
    service_account: github-actions@project.iam.gserviceaccount.com
```

### Azure Integration
```yaml
- uses: azure/login@vX
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

## Security Best Practices

### Least Privilege Permissions
```yaml
# Always start with minimum permissions
permissions:
  contents: read

# Add only what's needed per job
jobs:
  deploy:
    permissions:
      contents: read
      id-token: write
```

### Pin Third-Party Actions to SHA
```yaml
# Risky - tag can be moved
- uses: actions/checkout@v4

# Safer - pin to full SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
```

### Secret Management
```yaml
# Environment-specific secrets
jobs:
  deploy:
    environment: production  # Uses production secrets
    steps:
      - run: deploy --token ${{ secrets.DEPLOY_TOKEN }}

# Mask sensitive output
- run: |
    echo "::add-mask::${{ secrets.API_KEY }}"
    ./script-that-uses-key.sh
```

### Input Validation
```yaml
- name: Validate input
  run: |
    if [[ ! "${{ github.event.inputs.version }}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      echo "Invalid version format"
      exit 1
    fi
```

### Fork PR Restrictions
```yaml
on:
  pull_request_target:  # Use carefully - has write access
    types: [labeled]

jobs:
  build:
    if: github.event.label.name == 'safe-to-test'  # Require maintainer approval
```

## Common Patterns

### CI Pipeline
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@vX
      - uses: actions/setup-node@vX
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@vX
      - uses: actions/setup-node@vX
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@vX
      - uses: actions/setup-node@vX
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@vX
        with:
          name: build
          path: dist/
```

### Matrix Builds
```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node: [18, 20, 22]
        exclude:
          - os: windows-latest
            node: 18
        include:
          - os: ubuntu-latest
            node: 20
            coverage: true
    steps:
      - uses: actions/checkout@vX
      - uses: actions/setup-node@vX
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
      - if: matrix.coverage
        run: npm run coverage
```

### Caching Strategies
```yaml
# npm cache
- uses: actions/setup-node@vX
  with:
    cache: 'npm'

# Custom cache
- uses: actions/cache@vX
  with:
    path: |
      ~/.cache
      node_modules
    key: ${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-
```

### Release Workflow
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write
  packages: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@vX
      - uses: actions/setup-node@vX
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
      - run: npm run build
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
      - uses: softprops/action-gh-release@vX
        with:
          files: dist/*
          generate_release_notes: true
```

## Runner Image Discovery

### Finding Current Runner Versions
```bash
# Via GitHub API
gh api repos/actions/runner-images/releases/latest --jq '.tag_name'

# Check installed software
# In workflow:
- run: |
    cat /etc/os-release
    node --version
    python3 --version
```

### Runner Image Software Lists
- **ubuntu-latest**: github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md
- **windows-latest**: github.com/actions/runner-images/blob/main/images/windows/Windows2022-Readme.md
- **macos-latest**: github.com/actions/runner-images/blob/main/images/macos/macos-14-Readme.md

### Pinning Runner Versions
```yaml
# Use specific version instead of -latest
runs-on: ubuntu-24.04  # Instead of ubuntu-latest
runs-on: macos-14      # Instead of macos-latest
runs-on: windows-2022  # Instead of windows-latest
```

## Related Includes

- `~/.claude/includes/version-discovery.md` - Version discovery protocol
- `~/.claude/includes/git.md` - Git workflow standards
- `~/.claude/includes/devops.md` - Deployment patterns (if available)
