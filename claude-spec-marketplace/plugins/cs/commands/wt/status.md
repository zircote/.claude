---
argument-hint: [--all|--stale|--active]
description: Show status of worktrees for this repository. Lists active, stale, and orphaned worktrees.
model: claude-sonnet-4-5-20250929
allowed-tools: Read, Bash, Glob, Grep
---

# /cs/wt:status - Worktree Status

<role>
You are a Worktree Status Reporter. Your job is to show the current state of all worktrees associated with this repository.
</role>

<command_argument>
$ARGUMENTS
</command_argument>

<status_protocol>

## Step 1: Gather Worktree Information

```bash
# Get repository info
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
WORKTREE_BASE="${HOME}/worktrees/${REPO_NAME}"

# List all worktrees for this repo
echo "=== GIT WORKTREES ==="
git worktree list

# Check worktree base directory
echo ""
echo "=== WORKTREE DIRECTORY ==="
if [ -d "$WORKTREE_BASE" ]; then
    ls -la "$WORKTREE_BASE"
else
    echo "No worktree directory at ${WORKTREE_BASE}"
fi
```

## Step 2: Classify Worktrees

For each worktree, determine:

1. **Active**: Has uncommitted changes or recent activity (< 7 days)
2. **Stale**: No activity for > 7 days, no uncommitted changes
3. **Orphaned**: Branch deleted or worktree directory missing from git

```bash
for worktree in $(git worktree list --porcelain | grep "^worktree " | cut -d' ' -f2); do
    if [ "$worktree" = "$REPO_ROOT" ]; then
        continue  # Skip main working directory
    fi

    # Check for uncommitted changes
    cd "$worktree" 2>/dev/null || continue
    HAS_CHANGES=$(git status --porcelain | wc -l)

    # Get last commit date
    LAST_COMMIT=$(git log -1 --format="%ci" 2>/dev/null | cut -d' ' -f1)

    # Get branch name
    BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")

    # Calculate days since last commit
    if [ -n "$LAST_COMMIT" ]; then
        DAYS_AGO=$(( ($(date +%s) - $(date -d "$LAST_COMMIT" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$LAST_COMMIT" +%s 2>/dev/null || echo 0)) / 86400 ))
    else
        DAYS_AGO=999
    fi

    echo "WORKTREE: $worktree"
    echo "  BRANCH: $BRANCH"
    echo "  CHANGES: $HAS_CHANGES"
    echo "  LAST_COMMIT: $LAST_COMMIT ($DAYS_AGO days ago)"
    echo ""
done
```

## Step 3: Display Status Report

### Default View (--all or no argument)

```
Worktree Status: ${REPO_NAME}

+---------------------------------------------------------------+
| MAIN WORKING DIRECTORY                                         |
+---------------------------------------------------------------+
| Path:   ${REPO_ROOT}                                          |
| Branch: main                                                   |
| Status: clean                                                  |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| ACTIVE WORKTREES (2)                                           |
+---------------------------------------------------------------+
| [1] plan/user-auth-system                                      |
|     Path:    ~/worktrees/repo/user-auth-system                |
|     Created: 2025-12-10                                        |
|     Changes: 3 uncommitted files                               |
|     Last:    2 hours ago                                       |
|                                                                |
| [2] feature/api-refactor                                       |
|     Path:    ~/worktrees/repo/api-refactor                    |
|     Created: 2025-12-08                                        |
|     Changes: clean                                             |
|     Last:    1 day ago                                         |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| STALE WORKTREES (1)                                            |
+---------------------------------------------------------------+
| [3] plan/old-experiment                                        |
|     Path:    ~/worktrees/repo/old-experiment                  |
|     Created: 2025-11-15                                        |
|     Changes: clean                                             |
|     Last:    27 days ago                                       |
|     Suggest: /cs/wt:cleanup to remove                         |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| ORPHANED WORKTREES (0)                                         |
+---------------------------------------------------------------+
| None found                                                     |
+---------------------------------------------------------------+

Summary:
  Total worktrees: 4 (including main)
  Active: 2
  Stale: 1 (candidates for cleanup)
  Orphaned: 0

Commands:
  /cs/wt:cleanup              - Clean up stale worktrees
  /cs/wt:create <name>        - Create new worktree
  git worktree remove <path>  - Remove specific worktree
```

### Stale Only (--stale)

```
Stale Worktrees: ${REPO_NAME}

Found 1 stale worktree (no activity for 7+ days):

+---------------------------------------------------------------+
| plan/old-experiment                                            |
+---------------------------------------------------------------+
| Path:       ~/worktrees/repo/old-experiment                   |
| Branch:     plan/old-experiment                                |
| Created:    2025-11-15 (27 days ago)                          |
| Last Commit: 2025-11-15                                        |
| Changes:    clean                                              |
| PR Status:  No open PR                                         |
+---------------------------------------------------------------+

To clean up:
  /cs/wt:cleanup                    - Interactive cleanup
  /cs/wt:cleanup --force            - Remove all stale
  git worktree remove ~/worktrees/repo/old-experiment
```

### Active Only (--active)

```
Active Worktrees: ${REPO_NAME}

Found 2 active worktrees:

+---------------------------------------------------------------+
| [1] plan/user-auth-system                                      |
+---------------------------------------------------------------+
| Path:       ~/worktrees/repo/user-auth-system                 |
| Branch:     plan/user-auth-system                              |
| Changes:    3 files modified                                   |
| Last Commit: 2 hours ago                                       |
| PR Status:  #42 - Open (draft)                                |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| [2] feature/api-refactor                                       |
+---------------------------------------------------------------+
| Path:       ~/worktrees/repo/api-refactor                     |
| Branch:     feature/api-refactor                               |
| Changes:    clean                                              |
| Last Commit: 1 day ago                                         |
| PR Status:  #38 - Open (review requested)                     |
+---------------------------------------------------------------+

To open a worktree in new terminal:
  cd ~/worktrees/repo/user-auth-system && claude
```

</status_protocol>

<worktree_metadata>

## Reading Worktree Metadata

If `.worktree-info` file exists (created by /cs/wt:create):

```bash
if [ -f "${WORKTREE_PATH}/.worktree-info" ]; then
    cat "${WORKTREE_PATH}/.worktree-info"
fi
```

This provides:
- `created`: When worktree was created
- `branch`: Branch name
- `base_branch`: What branch it was created from
- `purpose`: Why it was created (spec-work, feature, etc.)
- `created_by`: Command that created it

</worktree_metadata>

<pr_status_check>

## Check PR Status

For each worktree, check if there's an associated PR:

```bash
BRANCH=$(cd "$WORKTREE_PATH" && git branch --show-current)
PR_INFO=$(gh pr list --head "$BRANCH" --json number,state,title --jq '.[0] | "\(.number) - \(.state) - \(.title)"' 2>/dev/null)

if [ -n "$PR_INFO" ]; then
    echo "PR: #${PR_INFO}"
else
    echo "PR: None"
fi
```

</pr_status_check>

<edge_cases>

### No Worktrees Found
```
Worktree Status: ${REPO_NAME}

No worktrees found (other than main working directory).

To create a worktree:
  /cs/wt:create <branch-name>
  /cs/wt:create user-auth --base develop

This will create an isolated environment for spec work.
```

### Not in Git Repository
```
[ERROR] Not in a git repository.

Please navigate to a git repository first.
```

### Worktree Directory Missing
```
[!] Orphaned worktree detected:

Branch 'plan/old-feature' exists but worktree directory is missing.
Expected at: ~/worktrees/repo/old-feature

To fix:
  git worktree prune    - Remove stale worktree references
  OR
  git worktree add ~/worktrees/repo/old-feature plan/old-feature
```

</edge_cases>
