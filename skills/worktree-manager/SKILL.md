---
name: worktree-manager
description: Create, manage, and cleanup git worktrees with Claude Code agents across all projects. USE THIS SKILL when user says "create worktree", "spin up worktrees", "new worktree for X", "worktree status", "cleanup worktrees", or wants parallel development branches. Handles worktree creation, dependency installation, validation, agent launching in iTerm2/Ghostty, and global registry management.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Task
---

# Global Worktree Manager

Manage parallel development across ALL projects using git worktrees with Claude Code agents. Each worktree is an isolated copy of the repo on a different branch, stored centrally at `~/Projects/worktrees/`.

**IMPORTANT**: You (Claude) can perform ALL operations manually using standard tools (jq, git, bash). Scripts are helpers, not requirements. If a script fails, fall back to manual operations described in this document.

---

## ⚠️ MANDATORY FIRST STEP - READ CONFIG BEFORE ANY ACTION

**YOU MUST READ `~/.claude/skills/worktree-manager/config.json` BEFORE doing ANYTHING else.**

This is NON-NEGOTIABLE. The config contains user-specific settings that MUST be respected:

```bash
# ALWAYS do this FIRST:
cat ~/.claude/skills/worktree-manager/config.json
```

**Extract and use these values:**
| Config Key | What It Controls | NEVER Assume |
|------------|------------------|--------------|
| `terminal` | Which terminal app to use (iterm2, ghostty, tmux, etc.) | Don't guess "Ghostty" or "Terminal.app" |
| `claudeCommand` | The exact command to run Claude | Don't omit flags like `--dangerously-skip-permissions` |
| `shell` | bash, zsh, or fish | Don't assume bash |
| `portsPerWorktree` | How many ports per worktree | Don't hardcode 2 |
| `worktreeBase` | Where worktrees are stored | Don't assume ~/Projects/worktrees |
| `defaultCopyDirs` | What to copy into worktrees | Don't guess |

**Terminal launch commands MUST use config values:**

```bash
# For iterm2 (from config):
osascript <<EOF
tell application "iTerm2"
  create window with default profile
  tell current session of current window
    write text "cd '$WORKTREE_PATH' && $CLAUDE_COMMAND"
  end tell
end tell
EOF

# For ghostty (from config):
open -na "Ghostty.app" --args -e $SHELL -c "cd '$WORKTREE_PATH' && $CLAUDE_COMMAND"

# For tmux (from config):
tmux new-session -d -s "wt-$SLUG" -c "$WORKTREE_PATH" "$SHELL -c '$CLAUDE_COMMAND'"
```

**FAILURE TO READ CONFIG FIRST = BROKEN WORKTREES**

---

## When This Skill Activates

**Trigger phrases:**
- "spin up worktrees for X, Y, Z"
- "spin up worktrees for X, Y, Z with prompt '...'"
- "spin up worktrees for X, Y, Z with prompt '...' --headless"
- "create 3 worktrees for features A, B, C"
- "new worktree for feature/auth"
- "new worktree for feature/auth with prompt '...'"
- "what's the status of my worktrees?"
- "show all worktrees" / "show worktrees for this project"
- "clean up merged worktrees"
- "clean up the auth worktree"
- "launch agent in worktree X"
- "launch agent in worktree X with prompt '...'"
- "launch agent in worktree X with prompt '...' --headless"

---

## File Locations

| File | Purpose |
|------|---------|
| `~/.claude/worktree-registry.json` | **Global registry** - tracks all worktrees across all projects |
| `~/.claude/skills/worktree-manager/config.json` | **Skill config** - terminal, shell, port range settings |
| `~/.claude/skills/worktree-manager/scripts/` | **Helper scripts** - optional, can do everything manually |
| `~/Projects/worktrees/` | **Worktree storage** - all worktrees live here |
| `.claude/worktree.json` (per-project) | **Project config** - optional custom settings |

---

## Core Concepts

### Centralized Worktree Storage
All worktrees live in `~/Projects/worktrees/<project-name>/<branch-slug>/`

```
~/Projects/worktrees/
├── obsidian-ai-agent/
│   ├── feature-auth/           # branch: feature/auth
│   ├── feature-payments/       # branch: feature/payments
│   └── fix-login-bug/          # branch: fix/login-bug
└── another-project/
    └── feature-dark-mode/
```

### Branch Slug Convention
Branch names are slugified for filesystem safety by replacing `/` with `-`:
- `feature/auth` → `feature-auth`
- `fix/login-bug` → `fix-login-bug`
- `feat/user-profile` → `feat-user-profile`

**Slugify manually:** `echo "feature/auth" | tr '/' '-'` → `feature-auth`

### Port Allocation Rules
- **Global pool**: 8100-8199 (100 ports total)
- **Per worktree**: 2 ports allocated (for API + frontend patterns)
- **Globally unique**: Ports are tracked globally to avoid conflicts across projects
- **Check before use**: Always verify port isn't in use by system: `lsof -i :<port>`

---

## Global Registry

### Location
`~/.claude/worktree-registry.json`

### Schema
```json
{
  "worktrees": [
    {
      "id": "unique-uuid",
      "project": "obsidian-ai-agent",
      "repoPath": "/Users/User_1/Projects/obsidian-ai-agent",
      "branch": "feature/auth",
      "branchSlug": "feature-auth",
      "worktreePath": "/Users/User_1/Projects/worktrees/obsidian-ai-agent/feature-auth",
      "ports": [8100, 8101],
      "createdAt": "2025-12-04T10:00:00Z",
      "validatedAt": "2025-12-04T10:02:00Z",
      "agentLaunchedAt": "2025-12-04T10:03:00Z",
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

### Field Descriptions

**Worktree entry fields:**
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (UUID) |
| `project` | string | Project name (from git remote or directory) |
| `repoPath` | string | Absolute path to original repository |
| `branch` | string | Full branch name (e.g., `feature/auth`) |
| `branchSlug` | string | Filesystem-safe name (e.g., `feature-auth`) |
| `worktreePath` | string | Absolute path to worktree |
| `ports` | number[] | Allocated port numbers (usually 2) |
| `createdAt` | string | ISO 8601 timestamp |
| `validatedAt` | string\|null | When validation passed |
| `agentLaunchedAt` | string\|null | When agent was launched |
| `task` | string\|null | Task description for the agent |
| `prNumber` | number\|null | Associated PR number if exists |
| `status` | string | `active`, `orphaned`, or `merged` |

**Port pool fields:**
| Field | Type | Description |
|-------|------|-------------|
| `start` | number | First port in pool (default: 8100) |
| `end` | number | Last port in pool (default: 8199) |
| `allocated` | number[] | Currently allocated ports |

### Manual Registry Operations

**Read entire registry:**
```bash
cat ~/.claude/worktree-registry.json | jq '.'
```

**List all worktrees:**
```bash
cat ~/.claude/worktree-registry.json | jq '.worktrees[]'
```

**List worktrees for specific project:**
```bash
cat ~/.claude/worktree-registry.json | jq '.worktrees[] | select(.project == "my-project")'
```

**Get allocated ports:**
```bash
cat ~/.claude/worktree-registry.json | jq '.portPool.allocated'
```

**Find worktree by branch (partial match):**
```bash
cat ~/.claude/worktree-registry.json | jq '.worktrees[] | select(.branch | contains("auth"))'
```

**Add worktree entry manually:**
```bash
TMP=$(mktemp)
jq '.worktrees += [{
  "id": "'$(uuidgen)'",
  "project": "my-project",
  "repoPath": "/path/to/repo",
  "branch": "feature/auth",
  "branchSlug": "feature-auth",
  "worktreePath": "/Users/User_1/Projects/worktrees/my-project/feature-auth",
  "ports": [8100, 8101],
  "createdAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
  "validatedAt": null,
  "agentLaunchedAt": null,
  "task": "My task",
  "prNumber": null,
  "status": "active"
}]' ~/.claude/worktree-registry.json > "$TMP" && mv "$TMP" ~/.claude/worktree-registry.json
```

**Add ports to allocated pool:**
```bash
TMP=$(mktemp)
jq '.portPool.allocated += [8100, 8101] | .portPool.allocated |= unique | .portPool.allocated |= sort_by(.)' \
  ~/.claude/worktree-registry.json > "$TMP" && mv "$TMP" ~/.claude/worktree-registry.json
```

**Remove worktree entry:**
```bash
TMP=$(mktemp)
jq 'del(.worktrees[] | select(.project == "my-project" and .branch == "feature/auth"))' \
  ~/.claude/worktree-registry.json > "$TMP" && mv "$TMP" ~/.claude/worktree-registry.json
```

**Release ports from pool:**
```bash
TMP=$(mktemp)
jq '.portPool.allocated = (.portPool.allocated | map(select(. != 8100 and . != 8101)))' \
  ~/.claude/worktree-registry.json > "$TMP" && mv "$TMP" ~/.claude/worktree-registry.json
```

**Initialize empty registry (if missing):**
```bash
mkdir -p ~/.claude
cat > ~/.claude/worktree-registry.json << 'EOF'
{
  "worktrees": [],
  "portPool": {
    "start": 8100,
    "end": 8199,
    "allocated": []
  }
}
EOF
```

---

## Manual Port Allocation

If `scripts/allocate-ports.sh` fails, allocate ports manually:

**Step 1: Get currently allocated ports**
```bash
ALLOCATED=$(cat ~/.claude/worktree-registry.json | jq -r '.portPool.allocated[]' | sort -n)
echo "Currently allocated: $ALLOCATED"
```

**Step 2: Find first available port (not in allocated list AND not in use by system)**
```bash
for PORT in $(seq 8100 8199); do
  # Check if in registry
  if ! echo "$ALLOCATED" | grep -q "^${PORT}$"; then
    # Check if in use by system
    if ! lsof -i :"$PORT" &>/dev/null; then
      echo "Available: $PORT"
      break
    fi
  fi
done
```

**Step 3: Add to allocated pool**
```bash
TMP=$(mktemp)
jq '.portPool.allocated += [8100] | .portPool.allocated |= unique | .portPool.allocated |= sort_by(.)' \
  ~/.claude/worktree-registry.json > "$TMP" && mv "$TMP" ~/.claude/worktree-registry.json
```

---

## What You (Claude) Do vs What Scripts Do

| Task | Script Available | Manual Fallback |
|------|------------------|-----------------|
| Determine project name | No | Parse `git remote get-url origin` or `basename $(pwd)` |
| Detect package manager | No | Check for lockfiles (see Detection section) |
| Create git worktree | No | `git worktree add <path> -b <branch>` |
| Copy .agents/ directory | No | `cp -r .agents <worktree-path>/` |
| Install dependencies | No | Run detected install command |
| Validate (health check) | No | Start server, curl endpoint, stop server |
| Allocate ports | `scripts/allocate-ports.sh 2` | Manual (see above) |
| Register worktree | `scripts/register.sh` | Manual jq (see above) |
| Launch agent in terminal | `scripts/launch-agent.sh` | Manual (see below) |
| Show status | `scripts/status.sh` | `cat ~/.claude/worktree-registry.json \| jq ...` |
| Cleanup worktree | `scripts/cleanup.sh` | Manual (see Cleanup section) |

---

## Workflows

### 1. Create Multiple Worktrees with Agents

**User says:** "Spin up 3 worktrees for feature/auth, feature/payments, and fix/login-bug"

**You do (can parallelize with subagents):**

```
⚠️ STEP 0 - MANDATORY CONFIG READ (do this ONCE, before anything else):
   CONFIG=$(cat ~/.claude/skills/worktree-manager/config.json)
   TERMINAL=$(echo "$CONFIG" | jq -r '.terminal')
   CLAUDE_CMD=$(echo "$CONFIG" | jq -r '.claudeCommand')
   SHELL_TYPE=$(echo "$CONFIG" | jq -r '.shell')
   PORTS_PER_WT=$(echo "$CONFIG" | jq -r '.portsPerWorktree')
   WT_BASE=$(echo "$CONFIG" | jq -r '.worktreeBase' | sed "s|~|$HOME|")
   COPY_DIRS=$(echo "$CONFIG" | jq -r '.defaultCopyDirs[]')

For EACH branch (can run in parallel):

1. SETUP
   a. Get project name:
      PROJECT=$(basename $(git remote get-url origin 2>/dev/null | sed 's/\.git$//') 2>/dev/null || basename $(pwd))
   b. Get repo root:
      REPO_ROOT=$(git rev-parse --show-toplevel)
   c. Slugify branch:
      BRANCH_SLUG=$(echo "feature/auth" | tr '/' '-')
   d. Determine worktree path:
      WORKTREE_PATH=~/Projects/worktrees/$PROJECT/$BRANCH_SLUG

2. ALLOCATE PORTS
   Option A (script): ~/.claude/skills/worktree-manager/scripts/allocate-ports.sh 2
   Option B (manual): Find 2 unused ports from 8100-8199, add to registry

3. CREATE WORKTREE
   mkdir -p ~/Projects/worktrees/$PROJECT
   git worktree add $WORKTREE_PATH -b $BRANCH
   # If branch exists already, omit -b flag

4. COPY UNCOMMITTED RESOURCES
   cp -r .agents $WORKTREE_PATH/ 2>/dev/null || true
   cp .env.example $WORKTREE_PATH/.env 2>/dev/null || true

5. INSTALL DEPENDENCIES
   cd $WORKTREE_PATH
   # Detect and run: npm install / uv sync / etc.

6. VALIDATE (start server, health check, stop)
   a. Start server with allocated port
   b. Wait and health check: curl -sf http://localhost:$PORT/health
   c. Stop server
   d. If FAILS: report error but continue with other worktrees

7. REGISTER IN GLOBAL REGISTRY
   Option A (script): ~/.claude/skills/worktree-manager/scripts/register.sh ...
   Option B (manual): Update ~/.claude/worktree-registry.json with jq

8. LAUNCH AGENT (USE CONFIG VALUES FROM STEP 0!)
   Option A (script with interactive prompt - default):
     ~/.claude/skills/worktree-manager/scripts/launch-agent.sh $WORKTREE_PATH "task" --prompt "template"
   Option B (script with headless prompt - auto-executes):
     ~/.claude/skills/worktree-manager/scripts/launch-agent.sh $WORKTREE_PATH "task" --prompt "template" --headless
   Option C (script without prompt):
     ~/.claude/skills/worktree-manager/scripts/launch-agent.sh $WORKTREE_PATH "task"
   Option D (manual): Substitute template vars, choose mode:
      SUBSTITUTED=$(echo "$PROMPT" | sed "s/{{service}}/$BRANCH_SLUG/g; s/{{branch}}/$BRANCH/g; s/{{project}}/$PROJECT/g")
      Interactive: $CLAUDE_CMD '$SUBSTITUTED'
      Headless:    $CLAUDE_CMD -p '$SUBSTITUTED'
   ⚠️ NEVER hardcode terminal app or claude command - ALWAYS use config values!
   ⚠️ When user provides a prompt template, ALWAYS substitute variables before launching

AFTER ALL COMPLETE:
- Report summary table to user
- Note any failures with details
```

### 2. Check Status

**With script:**
```bash
~/.claude/skills/worktree-manager/scripts/status.sh
~/.claude/skills/worktree-manager/scripts/status.sh --project my-project
```

**Manual:**
```bash
# All worktrees
cat ~/.claude/worktree-registry.json | jq -r '.worktrees[] | "\(.project)\t\(.branch)\t\(.ports | join(","))\t\(.status)\t\(.task // "-")"'

# For current project
PROJECT=$(basename $(git remote get-url origin 2>/dev/null | sed 's/\.git$//'))
cat ~/.claude/worktree-registry.json | jq -r ".worktrees[] | select(.project == \"$PROJECT\") | \"\(.branch)\t\(.ports | join(\",\"))\t\(.status)\""
```

### 3. Launch Agent Manually

⚠️ **FIRST: Read config to get terminal and claudeCommand:**
```bash
CONFIG=$(cat ~/.claude/skills/worktree-manager/config.json)
TERMINAL=$(echo "$CONFIG" | jq -r '.terminal')
CLAUDE_CMD=$(echo "$CONFIG" | jq -r '.claudeCommand')
```

**Then use the CONFIGURED terminal (examples below):**

**For iTerm2** (when `"terminal": "iterm2"`):
```bash
osascript <<EOF
tell application "iTerm2"
  create window with default profile
  tell current session of current window
    write text "cd '$WORKTREE_PATH' && $CLAUDE_CMD"
  end tell
end tell
EOF
```

**For Ghostty** (when `"terminal": "ghostty"`):
```bash
open -na "Ghostty.app" --args -e bash -c "cd '$WORKTREE_PATH' && $CLAUDE_CMD"
```

**For tmux** (when `"terminal": "tmux"`):
```bash
tmux new-session -d -s "wt-$PROJECT-$BRANCH_SLUG" -c "$WORKTREE_PATH" "bash -c '$CLAUDE_CMD'"
```

⚠️ **NEVER assume which terminal to use - ALWAYS check config.json first!**

### 4. Cleanup Worktree

**With script:**
```bash
~/.claude/skills/worktree-manager/scripts/cleanup.sh my-project feature/auth --delete-branch
```

**Manual cleanup:**
```bash
# 1. Get worktree info from registry
ENTRY=$(cat ~/.claude/worktree-registry.json | jq '.worktrees[] | select(.project == "my-project" and .branch == "feature/auth")')
WORKTREE_PATH=$(echo "$ENTRY" | jq -r '.worktreePath')
PORTS=$(echo "$ENTRY" | jq -r '.ports[]')
REPO_PATH=$(echo "$ENTRY" | jq -r '.repoPath')

# 2. Kill processes on ports
for PORT in $PORTS; do
  lsof -ti:"$PORT" | xargs kill -9 2>/dev/null || true
done

# 3. Remove worktree
cd "$REPO_PATH"
git worktree remove "$WORKTREE_PATH" --force 2>/dev/null || rm -rf "$WORKTREE_PATH"
git worktree prune

# 4. Remove from registry
TMP=$(mktemp)
jq 'del(.worktrees[] | select(.project == "my-project" and .branch == "feature/auth"))' \
  ~/.claude/worktree-registry.json > "$TMP" && mv "$TMP" ~/.claude/worktree-registry.json

# 5. Release ports
TMP=$(mktemp)
for PORT in $PORTS; do
  jq ".portPool.allocated = (.portPool.allocated | map(select(. != $PORT)))" \
    ~/.claude/worktree-registry.json > "$TMP" && mv "$TMP" ~/.claude/worktree-registry.json
done

# 6. Optionally delete branch
git branch -D feature/auth
git push origin --delete feature/auth
```

---

## Package Manager Detection

Detect by checking for lockfiles in priority order:

| File | Package Manager | Install Command |
|------|-----------------|-----------------|
| `bun.lockb` | bun | `bun install` |
| `pnpm-lock.yaml` | pnpm | `pnpm install` |
| `yarn.lock` | yarn | `yarn install` |
| `package-lock.json` | npm | `npm install` |
| `uv.lock` | uv | `uv sync` |
| `pyproject.toml` (no uv.lock) | uv | `uv sync` |
| `requirements.txt` | pip | `pip install -r requirements.txt` |
| `go.mod` | go | `go mod download` |
| `Cargo.toml` | cargo | `cargo build` |

**Detection logic:**
```bash
cd $WORKTREE_PATH
if [ -f "bun.lockb" ]; then bun install
elif [ -f "pnpm-lock.yaml" ]; then pnpm install
elif [ -f "yarn.lock" ]; then yarn install
elif [ -f "package-lock.json" ]; then npm install
elif [ -f "uv.lock" ]; then uv sync
elif [ -f "pyproject.toml" ]; then uv sync
elif [ -f "requirements.txt" ]; then pip install -r requirements.txt
elif [ -f "go.mod" ]; then go mod download
elif [ -f "Cargo.toml" ]; then cargo build
fi
```

---

## Dev Server Detection

Look for dev commands in this order:

1. **docker-compose.yml / compose.yml**: `docker-compose up -d` or `docker compose up -d`
2. **package.json scripts**: Look for `dev`, `start:dev`, `serve`
3. **Python with uvicorn**: `uv run uvicorn app.main:app --port $PORT`
4. **Python with Flask**: `flask run --port $PORT`
5. **Go**: `go run .`

**Port injection**: Most servers accept `PORT` env var or `--port` flag

---

## Project-Specific Config (Optional)

Projects can provide `.claude/worktree.json` for custom settings:

```json
{
  "ports": {
    "count": 2,
    "services": ["api", "frontend"]
  },
  "install": "uv sync && cd frontend && npm install",
  "validate": {
    "start": "docker-compose up -d",
    "healthCheck": "curl -sf http://localhost:{{PORT}}/health",
    "stop": "docker-compose down"
  },
  "copyDirs": [".agents", ".env.example", "data/fixtures"]
}
```

If this file exists, use its settings. Otherwise, auto-detect.

---

## Parallel Worktree Creation

When creating multiple worktrees, use subagents for parallelization:

```
User: "Spin up worktrees for feature/a, feature/b, feature/c"

You:
1. Allocate ports for ALL worktrees upfront (6 ports total)
2. Spawn 3 subagents, one per worktree
3. Each subagent:
   - Creates its worktree
   - Installs deps
   - Validates
   - Registers (with its pre-allocated ports)
   - Launches agent
4. Collect results from all subagents
5. Report unified summary with any failures noted
```

---

## Initial Prompts

Launch Claude Code agents with a prompt that's ready when the instance starts. Choose interactive or headless mode.

### Prompt Modes

| Mode | Flag | Behavior |
|------|------|----------|
| **Interactive** (default) | `--prompt "..."` | Passes prompt as argument, pre-filled in Claude's input (`cc "prompt"`) |
| **Headless** | `--prompt "..." --headless` | Uses `-p` flag, auto-executes and exits (`cc -p "prompt"`) |

### Syntax

Interactive (default):
```bash
~/.claude/skills/worktree-manager/scripts/launch-agent.sh $WORKTREE_PATH "$TASK" --prompt "template"
```

Headless (auto-execute):
```bash
~/.claude/skills/worktree-manager/scripts/launch-agent.sh $WORKTREE_PATH "$TASK" --prompt "template" --headless
```

Or in natural language:
```
spin up worktrees for auth, payments with prompt "run tests for {{service}}"
spin up worktrees for auth, payments with prompt "/review-code" --headless
```

### Template Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{{service}}` | Branch slug | `feature-auth` |
| `{{branch}}` | Full branch name | `feature/auth` |
| `{{branch_slug}}` | Same as service | `feature-auth` |
| `{{project}}` | Project name | `my-api` |
| `{{worktree_path}}` | Full path | `/Users/.../worktrees/my-api/feature-auth` |
| `{{port}}` | First allocated port | `8100` |
| `{{ports}}` | All ports (comma-sep) | `8100,8101` |

### How It Works

1. User provides prompt template with optional `{{variable}}` placeholders
2. `launch-agent.sh` substitutes variables with worktree-specific values
3. Claude Code launches with prompt:
   - **Interactive**: `cc "substituted-prompt"` - prompt pre-filled in input
   - **Headless**: `cc -p "substituted-prompt"` - auto-executes and exits

### Batch Example

```
User: "spin up worktrees for auth, payments with prompt 'analyze {{service}}'"

Result (interactive mode): 2 Claude instances launched with prompts pre-filled:
  - auth worktree:     `cc 'analyze auth'` - prompt ready in input
  - payments worktree: `cc 'analyze payments'` - prompt ready in input

With --headless: Uses -p flag, auto-executes immediately (`cc -p 'analyze auth'`)
```

### Valid Prompt Types

- Slash commands: `"/explore"`, `"/review-code"`, `"/deep-research auth flow"`
- Natural language: `"fix all TypeScript errors"`, `"refactor {{service}} for performance"`
- Multi-line instructions (escape newlines or use slash commands)

---

## Safety Guidelines

1. **Before cleanup**, check PR status:
   - PR merged → safe to clean everything
   - PR open → warn user, confirm before proceeding
   - No PR → warn about unsubmitted work

2. **Before deleting branches**, confirm if:
   - PR not merged
   - No PR exists
   - Worktree has uncommitted changes

3. **Port conflicts**: If port in use by non-worktree process, pick different port

4. **Orphaned worktrees**: If original repo deleted, mark as `orphaned` in status

5. **Max worktrees**: With 100-port pool and 2 ports each, max ~50 concurrent worktrees

---

## Script Reference

Scripts are in `~/.claude/skills/worktree-manager/scripts/`

### allocate-ports.sh
```bash
~/.claude/skills/worktree-manager/scripts/allocate-ports.sh <count>
# Returns: space-separated port numbers (e.g., "8100 8101")
# Automatically updates registry
```

### register.sh
```bash
~/.claude/skills/worktree-manager/scripts/register.sh \
  <project> <branch> <branch-slug> <worktree-path> <repo-path> <ports> [task]
# Example:
~/.claude/skills/worktree-manager/scripts/register.sh \
  "my-project" "feature/auth" "feature-auth" \
  "$HOME/Projects/worktrees/my-project/feature-auth" \
  "/path/to/repo" "8100,8101" "Implement OAuth"
```

### launch-agent.sh
```bash
~/.claude/skills/worktree-manager/scripts/launch-agent.sh <worktree-path> [task] [--prompt "template"] [--headless]
# Opens new terminal window (uses config.json terminal setting) with Claude Code
#
# Prompt Modes:
#   --prompt "template"            Interactive (default): passes prompt as argument (cc "prompt")
#   --prompt "template" --headless Headless: uses -p flag, auto-executes (cc -p "prompt")
#
# Template Variables:
#   {{service}}       - Branch slug (e.g., "feature-auth")
#   {{branch}}        - Full branch name (e.g., "feature/auth")
#   {{branch_slug}}   - Same as {{service}}
#   {{project}}       - Project name
#   {{worktree_path}} - Full worktree path
#   {{ports}}         - Allocated ports (comma-separated)
#   {{port}}          - First allocated port
#
# Examples:
#   launch-agent.sh ~/Projects/worktrees/proj/auth "Optimize"
#   launch-agent.sh ~/Projects/worktrees/proj/auth "" --prompt "/explore"
#   launch-agent.sh ~/Projects/worktrees/proj/auth "" --prompt "/review-code" --headless
#   launch-agent.sh ~/Projects/worktrees/proj/auth "" --prompt "analyze {{service}}"
```

### status.sh
```bash
~/.claude/skills/worktree-manager/scripts/status.sh [--project <name>]
# Shows all worktrees, or filtered by project
```

### cleanup.sh
```bash
~/.claude/skills/worktree-manager/scripts/cleanup.sh <project> <branch> [--delete-branch]
# Kills ports, removes worktree, updates registry
# --delete-branch also removes local and remote git branches
```

### release-ports.sh
```bash
~/.claude/skills/worktree-manager/scripts/release-ports.sh <port1> [port2] ...
# Releases ports back to pool
```

---

## Skill Config

Location: `~/.claude/skills/worktree-manager/config.json`

```json
{
  "terminal": "ghostty",
  "shell": "bash",
  "claudeCommand": "claude --dangerously-skip-permissions",
  "portPool": {
    "start": 8100,
    "end": 8199
  },
  "portsPerWorktree": 2,
  "worktreeBase": "~/Projects/worktrees",
  "defaultCopyDirs": [".agents", ".env.example"]
}
```

**Options:**
- **terminal**: `ghostty`, `iterm2`, `tmux`, `wezterm`, `kitty`, `alacritty`
- **shell**: `bash`, `zsh`, `fish` (adjust syntax in claudeCommand if using fish)
- **claudeCommand**: The command to launch Claude Code (default uses `--dangerously-skip-permissions` for autonomous operation)

---

## Common Issues

### "Worktree already exists"
```bash
git worktree list
git worktree remove <path> --force
git worktree prune
```

### "Branch already exists"
```bash
# Use existing branch (omit -b flag)
git worktree add <path> <branch>
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

# Remove orphaned entries or add missing ones
```

### Validation failed
1. Check stderr/logs for error message
2. Common issues: missing env vars, database not running, wrong port
3. Report to user with details
4. Continue with other worktrees
5. User can fix and re-validate manually

---

## Example Session

**User:** "Spin up 2 worktrees for feature/dark-mode and fix/login-bug"

**You:**
1. **⚠️ READ CONFIG FIRST:**
   ```bash
   cat ~/.claude/skills/worktree-manager/config.json
   # Returns: {"terminal": "iterm2", "claudeCommand": "claude --dangerously-skip-permissions", ...}
   ```
   Extract: `TERMINAL=iterm2`, `CLAUDE_CMD="claude --dangerously-skip-permissions"`

2. Detect project: `obsidian-ai-agent` (from git remote)
3. Detect package manager: `uv` (found uv.lock)
4. Allocate 4 ports: `~/.claude/skills/worktree-manager/scripts/allocate-ports.sh 4` → `8100 8101 8102 8103`
5. Create worktrees:
   ```bash
   mkdir -p ~/Projects/worktrees/obsidian-ai-agent
   git worktree add ~/Projects/worktrees/obsidian-ai-agent/feature-dark-mode -b feature/dark-mode
   git worktree add ~/Projects/worktrees/obsidian-ai-agent/fix-login-bug -b fix/login-bug
   ```
6. Copy .agents/:
   ```bash
   cp -r .agents ~/Projects/worktrees/obsidian-ai-agent/feature-dark-mode/
   cp -r .agents ~/Projects/worktrees/obsidian-ai-agent/fix-login-bug/
   ```
7. Install deps in each worktree:
   ```bash
   (cd ~/Projects/worktrees/obsidian-ai-agent/feature-dark-mode && uv sync)
   (cd ~/Projects/worktrees/obsidian-ai-agent/fix-login-bug && uv sync)
   ```
8. Validate each (start server, health check, stop)
9. Register both worktrees in `~/.claude/worktree-registry.json`
10. **Launch agents using CONFIGURED terminal (`iterm2`) and command:**
    ```bash
    # Using iTerm2 as specified in config.json:
    for path in ~/Projects/worktrees/obsidian-ai-agent/feature-dark-mode ~/Projects/worktrees/obsidian-ai-agent/fix-login-bug; do
      osascript <<EOF
    tell application "iTerm2"
      create window with default profile
      tell current session of current window
        write text "cd '$path' && claude --dangerously-skip-permissions"
      end tell
    end tell
    EOF
    done
    ```
11. Report:
    ```
    Created 2 worktrees with agents:

    | Branch | Ports | Path | Task |
    |--------|-------|------|------|
    | feature/dark-mode | 8100, 8101 | ~/Projects/worktrees/.../feature-dark-mode | Implement dark mode |
    | fix/login-bug | 8102, 8103 | ~/Projects/worktrees/.../fix-login-bug | Fix login redirect |

    Both agents running in iTerm2 windows (per config.json: terminal=iterm2, claudeCommand=claude --dangerously-skip-permissions).
    ```
