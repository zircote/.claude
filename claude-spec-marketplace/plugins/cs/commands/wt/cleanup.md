---
argument-hint: [--force|--dry-run|--stale-days <N>]
description: Clean up stale and orphaned worktrees. By default runs interactively, --force removes all stale.
model: claude-sonnet-4-5-20250929
allowed-tools: Read, Bash, Glob, Grep
---

# /cs/wt:cleanup - Worktree Cleanup

<role>
You are a Worktree Cleanup Specialist. Your job is to identify and safely remove stale, merged, or orphaned worktrees while preserving active work.
</role>

<command_argument>
$ARGUMENTS
</command_argument>

<cleanup_protocol>

## Step 1: Parse Arguments

- **--dry-run**: Show what would be removed without removing
- **--force**: Remove all stale worktrees without confirmation
- **--stale-days N**: Consider worktrees stale after N days (default: 7)

## Step 2: Gather Worktree Information

```bash
# Get repository info
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
WORKTREE_BASE="${HOME}/worktrees/${REPO_NAME}"
STALE_DAYS=${STALE_DAYS:-7}

# Prune any already-removed worktrees
git worktree prune

# Get all worktrees
WORKTREES=$(git worktree list --porcelain | grep "^worktree " | cut -d' ' -f2)
```

## Step 3: Classify Each Worktree

```bash
CLEANUP_CANDIDATES=""
ACTIVE_WORKTREES=""
ORPHANED=""

for worktree in $WORKTREES; do
    # Skip main working directory
    if [ "$worktree" = "$REPO_ROOT" ]; then
        continue
    fi

    # Check if directory exists
    if [ ! -d "$worktree" ]; then
        ORPHANED="$ORPHANED $worktree"
        continue
    fi

    cd "$worktree"

    # Check for uncommitted changes
    HAS_CHANGES=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

    # Get branch name
    BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")

    # Check if branch is merged to main
    IS_MERGED=$(git branch --merged main 2>/dev/null | grep -c "^\s*${BRANCH}$" || echo 0)

    # Get last commit timestamp
    LAST_COMMIT_EPOCH=$(git log -1 --format="%ct" 2>/dev/null || echo 0)
    NOW_EPOCH=$(date +%s)
    DAYS_AGO=$(( (NOW_EPOCH - LAST_COMMIT_EPOCH) / 86400 ))

    # Classify
    if [ "$HAS_CHANGES" -gt 0 ]; then
        # Has uncommitted changes - NEVER auto-remove
        ACTIVE_WORKTREES="$ACTIVE_WORKTREES|$worktree:$BRANCH:uncommitted"
    elif [ "$IS_MERGED" -gt 0 ]; then
        # Branch merged - safe to remove
        CLEANUP_CANDIDATES="$CLEANUP_CANDIDATES|$worktree:$BRANCH:merged"
    elif [ "$DAYS_AGO" -gt "$STALE_DAYS" ]; then
        # Stale - no activity
        CLEANUP_CANDIDATES="$CLEANUP_CANDIDATES|$worktree:$BRANCH:stale($DAYS_AGO days)"
    else
        # Active
        ACTIVE_WORKTREES="$ACTIVE_WORKTREES|$worktree:$BRANCH:active"
    fi
done
```

## Step 4: Display Analysis

### Dry Run Mode (--dry-run)

```
Worktree Cleanup Analysis (DRY RUN)
Repository: ${REPO_NAME}

+---------------------------------------------------------------+
| WOULD BE REMOVED                                               |
+---------------------------------------------------------------+
| [1] ~/worktrees/repo/old-experiment                           |
|     Branch: plan/old-experiment                                |
|     Reason: stale (27 days inactive)                          |
|     Status: clean (no uncommitted changes)                     |
|                                                                |
| [2] ~/worktrees/repo/merged-feature                           |
|     Branch: feature/login-fix                                  |
|     Reason: merged to main                                     |
|     Status: clean                                              |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| WOULD BE PRESERVED                                             |
+---------------------------------------------------------------+
| [A] ~/worktrees/repo/user-auth                                |
|     Branch: plan/user-auth                                     |
|     Reason: has uncommitted changes (3 files)                  |
|                                                                |
| [B] ~/worktrees/repo/api-work                                 |
|     Branch: feature/api-work                                   |
|     Reason: active (last commit 2 days ago)                    |
+---------------------------------------------------------------+

Summary:
  Would remove: 2 worktrees
  Would preserve: 2 worktrees
  Disk space freed: ~45 MB (estimated)

To execute cleanup, run:
  /cs/wt:cleanup
  /cs/wt:cleanup --force  (no confirmation)
```

### Interactive Mode (default)

```
Worktree Cleanup
Repository: ${REPO_NAME}

Found 2 worktrees eligible for cleanup:

+---------------------------------------------------------------+
| [1] plan/old-experiment                                        |
+---------------------------------------------------------------+
| Path:   ~/worktrees/repo/old-experiment                       |
| Reason: stale (27 days inactive)                              |
| Status: clean                                                  |
| PR:     None                                                   |
+---------------------------------------------------------------+

Remove this worktree? [y/n/s(kip all)/q(uit)]
> y

[OK] Removed: ~/worktrees/repo/old-experiment
[OK] Branch plan/old-experiment preserved (use git branch -d to delete)

+---------------------------------------------------------------+
| [2] feature/login-fix                                          |
+---------------------------------------------------------------+
| Path:   ~/worktrees/repo/merged-feature                       |
| Reason: merged to main                                         |
| Status: clean                                                  |
| PR:     #35 - Merged                                          |
+---------------------------------------------------------------+

Remove this worktree AND delete branch? [y/n/b(ranch only)/s/q]
> y

[OK] Removed: ~/worktrees/repo/merged-feature
[OK] Branch feature/login-fix deleted

+---------------------------------------------------------------+
| CLEANUP COMPLETE                                               |
+---------------------------------------------------------------+
| Removed: 2 worktrees                                           |
| Deleted: 1 branch                                              |
| Preserved: 2 worktrees (active/uncommitted)                    |
| Disk freed: ~45 MB                                             |
+---------------------------------------------------------------+
```

### Force Mode (--force)

```
Worktree Cleanup (FORCE MODE)
Repository: ${REPO_NAME}

Removing stale and merged worktrees...

[OK] Removed: ~/worktrees/repo/old-experiment (stale)
[OK] Removed: ~/worktrees/repo/merged-feature (merged)
[OK] Deleted branch: feature/login-fix (was merged)

Skipped (uncommitted changes):
[!] ~/worktrees/repo/in-progress-work
    Has 3 uncommitted files - not removed

+---------------------------------------------------------------+
| CLEANUP COMPLETE                                               |
+---------------------------------------------------------------+
| Removed: 2 worktrees                                           |
| Skipped: 1 worktree (uncommitted changes)                      |
| Disk freed: ~45 MB                                             |
+---------------------------------------------------------------+
```

</cleanup_protocol>

<removal_commands>

## Worktree Removal

```bash
remove_worktree() {
    local WORKTREE_PATH="$1"
    local BRANCH="$2"
    local DELETE_BRANCH="$3"

    # Remove the worktree
    git worktree remove "$WORKTREE_PATH" --force

    # Optionally delete the branch
    if [ "$DELETE_BRANCH" = "yes" ]; then
        # Check if branch is fully merged
        if git branch --merged main | grep -q "$BRANCH"; then
            git branch -d "$BRANCH"
            echo "[OK] Branch $BRANCH deleted"
        else
            echo "[!] Branch $BRANCH not deleted (not fully merged)"
        fi
    fi
}
```

## Orphaned Worktree Cleanup

```bash
# Prune references to removed worktrees
git worktree prune

# Remove any leftover directories
if [ -d "$WORKTREE_PATH" ] && [ ! -f "$WORKTREE_PATH/.git" ]; then
    echo "[!] Found orphaned directory (no .git): $WORKTREE_PATH"
    echo "    Remove manually: rm -rf '$WORKTREE_PATH'"
fi
```

</removal_commands>

<safety_checks>

## Safety Rules

**NEVER remove a worktree that:**
1. Has uncommitted changes
2. Has unpushed commits
3. Is currently checked out elsewhere

**ALWAYS preserve:**
1. The main working directory
2. Worktrees with open PRs (warn only)
3. Recently active worktrees (< stale threshold)

**WARN but allow removal:**
1. Worktrees with open draft PRs
2. Unmerged branches (require explicit confirmation)

```bash
check_safety() {
    local WORKTREE_PATH="$1"

    cd "$WORKTREE_PATH"

    # Check uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "UNSAFE: Has uncommitted changes"
        return 1
    fi

    # Check unpushed commits
    BRANCH=$(git branch --show-current)
    UNPUSHED=$(git log origin/${BRANCH}..HEAD 2>/dev/null | wc -l)
    if [ "$UNPUSHED" -gt 0 ]; then
        echo "UNSAFE: Has unpushed commits"
        return 1
    fi

    echo "SAFE: Can be removed"
    return 0
}
```

</safety_checks>

<edge_cases>

### No Cleanup Candidates

```
Worktree Cleanup
Repository: ${REPO_NAME}

No worktrees eligible for cleanup.

Current worktrees:
  - ~/worktrees/repo/active-feature (active, 2 days ago)
  - ~/worktrees/repo/in-progress (has uncommitted changes)

All worktrees are either:
  - Recently active (within 7 days)
  - Have uncommitted changes
  - Main working directory

Nothing to clean up!
```

### Worktree with Open PR

```
+---------------------------------------------------------------+
| [!] WARNING: Open PR Found                                     |
+---------------------------------------------------------------+
| Worktree: ~/worktrees/repo/feature-branch                     |
| PR #42: "Add user authentication" (OPEN)                       |
|                                                                |
| This worktree has an open pull request.                        |
| Removing it won't close the PR, but you'll lose local context.|
+---------------------------------------------------------------+

Remove anyway? [y/n]
```

### Force Delete Unmerged Branch

```
+---------------------------------------------------------------+
| [!] WARNING: Unmerged Branch                                   |
+---------------------------------------------------------------+
| Branch: feature/experimental                                   |
| Status: NOT merged to main                                     |
|                                                                |
| Deleting this branch will lose all commits not in main.       |
+---------------------------------------------------------------+

Type 'DELETE' to confirm branch deletion, or press Enter to keep branch:
>
```

### Git Worktree Prune Needed

```
[!] Stale worktree references detected

Git has references to worktrees that no longer exist.
Running: git worktree prune

[OK] Pruned 2 stale worktree references
```

</edge_cases>
