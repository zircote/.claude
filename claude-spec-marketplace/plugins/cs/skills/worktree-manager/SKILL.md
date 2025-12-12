---
name: worktree-manager
description: Create, manage, and cleanup git worktrees with Claude Code agents across all projects. USE THIS SKILL when user says "create worktree", "spin up worktrees", "new worktree for X", "worktree status", "cleanup worktrees", or wants parallel development branches. Handles worktree creation, dependency installation, validation, agent launching, and global registry management.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Task
attribution: Migrated from ~/.claude/skills/worktree-manager
---

# Git Worktree Manager

Manage parallel development across ALL projects using git worktrees with Claude Code agents. Each worktree is an isolated copy of the repo on a different branch, stored centrally at the configured `worktreeBase` directory.

## Trigger Phrases

- "spin up worktrees for X, Y, Z"
- "spin up worktrees for X, Y, Z with prompt '...'"
- "create worktrees for features A, B, C"
- "new worktree for feature/auth"
- "worktree status" / "show all worktrees"
- "cleanup worktrees" / "clean up the auth worktree"
- "launch agent in worktree X"

## File Locations

| File | Purpose |
|------|---------|
| `~/.claude/worktree-registry.json` | **Global registry** - tracks all worktrees across all projects |
| `./config.json` | **Skill config** - terminal, shell, port range settings |
| `./scripts/` | **Helper scripts** - port allocation, registration, launch, cleanup |

## Quick Start

### 1. Check Status

```bash
./scripts/status.sh
./scripts/status.sh --project my-project
```

### 2. Create a Worktree

```bash
# Allocate ports
PORTS=$(./scripts/allocate-ports.sh 2)

# Create git worktree
git worktree add ~/Projects/worktrees/my-project/feature-auth -b feature/auth

# Register it
./scripts/register.sh my-project feature/auth feature-auth \
  ~/Projects/worktrees/my-project/feature-auth \
  /path/to/repo \
  "8100,8101" "Implement OAuth"

# Launch Claude agent
./scripts/launch-agent.sh ~/Projects/worktrees/my-project/feature-auth "Implement OAuth"
```

### 3. Cleanup

```bash
./scripts/cleanup.sh my-project feature/auth
./scripts/cleanup.sh my-project feature/auth --delete-branch
```

## Scripts Reference

### allocate-ports.sh

Allocate N unused ports from the global pool (default: 8100-8199).

```bash
./scripts/allocate-ports.sh <count>
# Returns: space-separated port numbers (e.g., "8100 8101")
```

### register.sh

Register a worktree in the global registry.

```bash
./scripts/register.sh <project> <branch> <branch-slug> <worktree-path> <repo-path> <ports> [task]
```

### launch-agent.sh

Launch Claude Code in a new terminal for a worktree.

```bash
./scripts/launch-agent.sh <worktree-path> [task] [--prompt "template"] [--headless]
```

**Prompt Modes:**
- `--prompt "template"` - Interactive mode (default): prompt pre-filled in Claude's input
- `--prompt "template" --headless` - Headless mode: auto-executes immediately with `-p` flag

**Template Variables:**
- `{{service}}` / `{{branch_slug}}` - Branch slug (e.g., "feature-auth")
- `{{branch}}` - Full branch name (e.g., "feature/auth")
- `{{project}}` - Project name
- `{{worktree_path}}` - Full worktree path
- `{{port}}` - First allocated port
- `{{ports}}` - All ports (comma-separated)

### status.sh

Show status of all managed worktrees.

```bash
./scripts/status.sh [--project <name>]
```

### cleanup.sh

Full cleanup of a worktree (ports, directory, registry, optionally branch).

```bash
./scripts/cleanup.sh <project> <branch> [--delete-branch]
```

### release-ports.sh

Release ports back to the global pool.

```bash
./scripts/release-ports.sh <port1> [port2] ...
```

## Configuration

Edit `config.json` to customize:

```json
{
  "terminal": "iterm2",
  "shell": "bash",
  "claudeCommand": "cc",
  "portPool": { "start": 8100, "end": 8199 },
  "portsPerWorktree": 2,
  "worktreeBase": "~/Projects/worktrees",
  "registryPath": "~/.claude/worktree-registry.json",
  "defaultCopyDirs": [".agents", ".env.example", ".env"],
  "healthCheckTimeout": 30,
  "healthCheckRetries": 6
}
```

**Terminal options:** `ghostty`, `iterm2`, `tmux`, `wezterm`, `kitty`, `alacritty`

## Global Registry Schema

Location: `~/.claude/worktree-registry.json`

```json
{
  "worktrees": [
    {
      "id": "unique-uuid",
      "project": "my-project",
      "repoPath": "/path/to/repo",
      "branch": "feature/auth",
      "branchSlug": "feature-auth",
      "worktreePath": "/Users/.../worktrees/my-project/feature-auth",
      "ports": [8100, 8101],
      "createdAt": "2025-12-04T10:00:00Z",
      "validatedAt": null,
      "agentLaunchedAt": null,
      "task": "Implement OAuth login",
      "prNumber": null,
      "status": "active"
    }
  ],
  "portPool": {
    "start": 8100,
    "end": 8199,
    "allocated": [8100, 8101]
  }
}
```

## Common Workflows

### Parallel Development

When user says "spin up worktrees for feature/a, feature/b, feature/c":

1. Read config.json to get terminal and claude command settings
2. Allocate ports for all worktrees upfront
3. For each branch (can parallelize):
   - Create git worktree
   - Copy required directories (.agents, .env, etc.)
   - Install dependencies
   - Validate (optional health check)
   - Register in global registry
   - Launch Claude agent
4. Report summary with paths and ports

### Initial Prompts

Launch agents with pre-configured prompts:

```bash
# Interactive - prompt ready in input
./scripts/launch-agent.sh ~/worktrees/proj/auth "" --prompt "/explore"

# Headless - auto-executes
./scripts/launch-agent.sh ~/worktrees/proj/auth "" --prompt "/review-code" --headless

# With template substitution
./scripts/launch-agent.sh ~/worktrees/proj/auth "" --prompt "analyze {{service}}"
```

## Safety Guidelines

1. **Before cleanup**, check PR status (merged = safe, open = warn)
2. **Before deleting branches**, confirm no uncommitted work
3. **Port conflicts**: If port in use by non-worktree process, pick different port
4. **Max worktrees**: With 100-port pool and 2 ports each, max ~50 concurrent worktrees

## Troubleshooting

### "Worktree already exists"
```bash
git worktree list
git worktree remove <path> --force
git worktree prune
```

### "Port already in use"
```bash
lsof -i :<port>
# Kill if stale, or pick different port
```

### Registry out of sync
```bash
# Compare registry to actual worktrees
cat ~/.claude/worktree-registry.json | jq '.worktrees[].worktreePath'
find ~/Projects/worktrees -maxdepth 2 -type d
```
