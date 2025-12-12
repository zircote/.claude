---
argument-hint: <branch-name|project-slug> [--base <branch>] [--prompt <initial-prompt>]
description: Create a worktree with Claude agent for spec work. Spawns isolated environment with optional initial prompt.
model: claude-opus-4-5-20251101
allowed-tools: Read, Write, Bash, Glob, Grep
---

# /cs/wt:create - Create Worktree with Claude Agent

<role>
You are a Worktree Orchestrator. Your job is to create isolated git worktrees for spec planning and implementation work, then launch Claude Code agents in those environments.
</role>

<command_argument>
$ARGUMENTS
</command_argument>

<worktree_protocol>

## Step 1: Parse Arguments

Extract from `$ARGUMENTS`:
- **branch-name**: Required - the name for the new branch/worktree
- **--base**: Optional - base branch to branch from (default: main)
- **--prompt**: Optional - initial prompt to run in the new worktree

```
Examples:
  /cs/wt:create user-auth-system
  /cs/wt:create user-auth --base develop
  /cs/wt:create user-auth --prompt "/cs/p user authentication"
```

## Step 2: Validate Prerequisites

```bash
# Check if in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "ERROR: Not in a git repository"
    exit 1
fi

# Check if worktree already exists
WORKTREE_BASE="${HOME}/worktrees"
REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
WORKTREE_PATH="${WORKTREE_BASE}/${REPO_NAME}/${BRANCH_NAME}"

if [ -d "$WORKTREE_PATH" ]; then
    echo "ERROR: Worktree already exists at ${WORKTREE_PATH}"
    exit 1
fi

# Check if branch already exists
if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
    echo "WARNING: Branch ${BRANCH_NAME} already exists"
    # Could still create worktree from existing branch
fi
```

## Step 3: Determine Branch Pattern

Apply naming conventions based on context:

```
IF branch-name starts with recognized prefix:
  USE branch-name as-is
  Prefixes: plan/, spec/, feature/, fix/, chore/

ELSE:
  IF context is planning (/cs/p):
    PREFIX = "plan/"
  ELSE IF context is implementation (/cs/i):
    PREFIX = "feature/"
  ELSE:
    PREFIX = "spec/"

  FULL_BRANCH = "${PREFIX}${branch-name}"
```

## Step 4: Create Worktree

```bash
# Ensure worktree base directory exists
mkdir -p "${WORKTREE_BASE}/${REPO_NAME}"

# Get base branch
BASE_BRANCH="${BASE:-main}"

# Fetch latest from remote
git fetch origin "${BASE_BRANCH}" 2>/dev/null || true

# Create the worktree with new branch
git worktree add -b "${FULL_BRANCH}" "${WORKTREE_PATH}" "origin/${BASE_BRANCH}"

# Verify creation
if [ -d "$WORKTREE_PATH" ]; then
    echo "[OK] Worktree created at: ${WORKTREE_PATH}"
    echo "[OK] Branch: ${FULL_BRANCH}"
else
    echo "[ERROR] Failed to create worktree"
    exit 1
fi
```

## Step 5: Configure Worktree Environment

```bash
# Copy any necessary config files
cd "${WORKTREE_PATH}"

# Ensure .claude directory structure if needed
if [ -d "${HOME}/.claude" ]; then
    # The main .claude config is global, no need to copy
    echo "[OK] Using global Claude configuration"
fi

# Create worktree metadata file
cat > "${WORKTREE_PATH}/.worktree-info" << EOF
created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
branch: ${FULL_BRANCH}
base_branch: ${BASE_BRANCH}
purpose: spec-work
created_by: /cs/wt:create
EOF

echo "[OK] Worktree configured"
```

## Step 6: Launch Claude Agent

Use the plugin's launch script if available, otherwise use osascript:

```bash
# Check for plugin launch script
LAUNCH_SCRIPT="${CLAUDE_PLUGIN_ROOT}/worktree/scripts/launch-agent.sh"

if [ -x "$LAUNCH_SCRIPT" ]; then
    # Use plugin script
    "$LAUNCH_SCRIPT" "${WORKTREE_PATH}" "${INITIAL_PROMPT:-Spec worktree ready}"
else
    # Fallback: Launch new terminal with Claude Code
    osascript <<EOF
    tell application "Terminal"
        activate
        do script "cd '${WORKTREE_PATH}' && claude"
    end tell
EOF
fi

echo "[OK] Claude agent launched in new terminal"
```

## Step 7: Display Completion Message

```
+---------------------------------------------------------------+
| WORKTREE CREATED SUCCESSFULLY                                  |
+---------------------------------------------------------------+
|                                                                |
| Location: ${WORKTREE_PATH}                                    |
| Branch:   ${FULL_BRANCH}                                      |
| Base:     ${BASE_BRANCH}                                      |
|                                                                |
| A new terminal window has been opened with Claude Code.        |
|                                                                |
+---------------------------------------------------------------+
| NEXT STEPS                                                     |
+---------------------------------------------------------------+
|                                                                |
| 1. Switch to the new terminal window                          |
|                                                                |
| 2. Run your spec command:                                     |
|    /cs/p <your-project-idea>    - Start planning              |
|    /cs/i <project-slug>         - Continue implementation     |
|                                                                |
| 3. When done, clean up with:                                  |
|    /cs/wt:cleanup               - Remove stale worktrees      |
|                                                                |
| You can close THIS terminal when ready.                        |
+---------------------------------------------------------------+
```

**STOP after displaying this message. Do not continue with any other work.**

</worktree_protocol>

<with_initial_prompt>

## Handling --prompt Flag

If `--prompt` is provided:

1. **Store the prompt** for the new session
2. **Launch agent with auto-execution**:

```bash
# Launch with initial prompt
osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '${WORKTREE_PATH}' && claude '${INITIAL_PROMPT}'"
end tell
EOF
```

The initial prompt can use template variables:
- `{{branch}}` - Branch name
- `{{project}}` - Derived project name from branch
- `{{path}}` - Worktree path

Example:
```
/cs/wt:create user-auth --prompt "/cs/p user authentication system"
```

This will:
1. Create worktree at `~/worktrees/repo/plan-user-auth`
2. Open new terminal
3. Start Claude Code
4. Automatically run `/cs/p user authentication system`

</with_initial_prompt>

<edge_cases>

### Branch Already Exists
```
Branch 'plan/user-auth' already exists.

Options:
[1] Create worktree from existing branch
[2] Create new branch with suffix (plan/user-auth-2)
[3] Cancel

Which option? [1/2/3]
```

### Worktree Path Exists
```
[ERROR] A worktree already exists at:
${WORKTREE_PATH}

Options:
[1] Open existing worktree in new terminal
[2] Remove existing and create fresh
[3] Cancel

Which option? [1/2/3]
```

### Git Conflicts
```
[ERROR] Cannot create worktree - uncommitted changes in base branch.

Please commit or stash your changes first:
  git stash
  /cs/wt:create ${BRANCH_NAME}
  # In new worktree: git stash pop (if needed)
```

### Not a Git Repository
```
[ERROR] Current directory is not a git repository.

Please navigate to a git repository first:
  cd /path/to/your/repo
  /cs/wt:create ${BRANCH_NAME}
```

</edge_cases>

<cleanup_reminder>

After completing work in a worktree:

1. **Commit all changes** in the worktree
2. **Create PR** if ready: `/git:pr`
3. **Merge** when approved
4. **Clean up** with `/cs/wt:cleanup`

Or use the full workflow:
```
/cs/wt:create feature-x
# ... do work ...
/git:cp
/git:pr
# ... PR merged ...
/cs/wt:cleanup
```

</cleanup_reminder>
