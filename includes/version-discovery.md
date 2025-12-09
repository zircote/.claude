# Version Discovery Protocol

## Specialist Agents

| Agent | Category | Use For |
|-------|----------|---------|
| `research-analyst` | 10-research-analysis | Complex version research across multiple sources |
| `devops-engineer` | 03-infrastructure | Infrastructure tool version discovery |

## Knowledge Cutoff Warning

**CRITICAL**: Claude's knowledge of library, tool, and action versions is often outdated. The training data has a cutoff date, and the software ecosystem evolves rapidly.

**Never assume version accuracy.** Always verify current versions before:
- Writing `package.json`, `requirements.txt`, `go.mod`, or similar dependency files
- Specifying GitHub Action versions in workflows
- Recommending tool installations
- Creating Docker images with specific base versions

## Claude Code Tool Authorization

Recommended tool authorizations for version discovery:

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch",
      "Bash(curl:*)",
      "Bash(npm view:*)",
      "Bash(pip index versions:*)",
      "Bash(go list -m:*)"
    ]
  }
}
```

## Discovery Methods (Priority Order)

### 1. context7 MCP (Preferred)
If context7 MCP is available, use it first for authoritative documentation:
```
Query: "Get current version of [package/action] from official docs"
```

### 2. WebSearch Tool
Use targeted search queries with the current year:
```
Search: "[package-name] latest version 2025"
Search: "[package-name] current stable release"
Search: "github [action-name] releases latest"
```

### 3. Official Sources via WebFetch
Fetch directly from authoritative sources:
- GitHub Releases API: `https://api.github.com/repos/[owner]/[repo]/releases/latest`
- npm Registry: `https://registry.npmjs.org/[package]/latest`
- PyPI: `https://pypi.org/pypi/[package]/json`

### 4. CLI Discovery Commands
When tools are installed locally:
```bash
# npm packages
npm view [package] version

# Python packages
pip index versions [package]

# Go modules
go list -m -versions [module]

# Docker images
docker pull [image]:latest && docker inspect [image]:latest
```

## Discovery Patterns by Category

### GitHub Actions
| Action | Discovery Query | Official Source |
|--------|-----------------|-----------------|
| `actions/checkout` | "actions/checkout latest version" | github.com/actions/checkout/releases |
| `actions/setup-node` | "actions/setup-node current version" | github.com/actions/setup-node/releases |
| `actions/setup-python` | "actions/setup-python latest" | github.com/actions/setup-python/releases |
| `actions/cache` | "github actions cache latest version" | github.com/actions/cache/releases |
| `actions/upload-artifact` | "actions/upload-artifact current" | github.com/actions/upload-artifact/releases |

### npm/Node.js Packages
```bash
# Current stable version
npm view [package] version

# All available versions
npm view [package] versions

# Via API
curl -s https://registry.npmjs.org/[package]/latest | jq '.version'
```

### Python Packages (PyPI)
```bash
# Via pip (if installed)
pip index versions [package]

# Via API
curl -s https://pypi.org/pypi/[package]/json | jq '.info.version'
```

### Go Modules
```bash
# List available versions
go list -m -versions [module]@latest

# Via proxy API
curl -s https://proxy.golang.org/[module]/@latest | jq '.Version'
```

### Docker Images
```bash
# Official images - check Docker Hub
# For specific tags, query the registry API or use:
docker pull [image]:latest
docker inspect [image]:latest --format '{{.RepoDigests}}'
```

### Cloud Provider SDKs
| SDK | Discovery Method |
|-----|------------------|
| AWS SDK | WebSearch "aws-sdk-js latest version 2025" |
| Google Cloud | WebSearch "google-cloud-python latest release" |
| Azure SDK | WebSearch "azure-sdk-for-js current version" |

## Verification Requirements

### Before Writing Dependency Files
1. **Discover** current version using methods above
2. **Verify** version exists (check release page or registry)
3. **Note** discovery date in comments when helpful
4. **Consider** stability (prefer stable over pre-release unless requested)

### Version Specification Best Practices
```json
// package.json - use caret for minor updates
{
  "dependencies": {
    "package": "^X.Y.Z"  // Discovered 2025-01-XX
  }
}
```

```python
# requirements.txt - pin or use compatible release
package>=X.Y.Z,<X+1.0.0  # Discovered 2025-01-XX
```

```yaml
# GitHub Actions - pin to major version or SHA
- uses: actions/checkout@vX  # Discovered 2025-01-XX
# Or for security-critical: pin to SHA
- uses: actions/checkout@abc123...
```

## Quick Reference Templates

### Version Discovery Checklist
```markdown
- [ ] Identified package/tool to version
- [ ] Checked context7 MCP (if available)
- [ ] Ran WebSearch with current year
- [ ] Verified at official source
- [ ] Noted discovery date
- [ ] Selected appropriate version constraint
```

### Discovery Query Templates
```
# Generic
"[name] latest stable version [current-year]"
"[name] current release changelog"

# GitHub Actions specific
"github actions [name] latest version"
"[owner]/[action] releases"

# Security-focused
"[name] security advisories [current-year]"
"[name] CVE vulnerabilities recent"
```

## When Discovery Fails

If version discovery is unsuccessful:
1. **State uncertainty** - "I couldn't verify the current version of X"
2. **Provide last known** - "As of my knowledge cutoff, version Y was current"
3. **Recommend verification** - "Please verify at [official-source] before using"
4. **Offer alternatives** - Suggest checking official docs or running local commands

## Related Includes

- `~/.claude/includes/github-actions.md` - GitHub Actions specific version patterns
- `~/.claude/includes/python.md` - Python package management
- `~/.claude/includes/react.md` - Node.js/npm patterns
