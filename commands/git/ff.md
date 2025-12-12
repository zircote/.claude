---
description: Fast-forward merge only - update branch without rebase or merge commits
argument-hint: "[remote] [branch]"
---

Attempt a fast-forward merge from the remote branch (no rebase, no merge commits):

## Variables

- **REMOTE**: First argument, defaults to `origin`
- **BRANCH**: Second argument, defaults to current branch's upstream tracking branch

## Pre-flight Checks

1. **Check for uncommitted changes**:
   ```bash
   git status --porcelain
   ```

   If there are uncommitted changes:
   > "You have uncommitted changes. Fast-forward merge requires a clean working directory.
   > Please commit or stash your changes first."

   Do not proceed until working directory is clean.

2. **Determine target branch**:
   - If BRANCH not specified, get upstream:
     ```bash
     git rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null
     ```
   - If no upstream tracking branch, ask user which branch to merge from

## Workflow

1. **Fetch from remote**:
   ```bash
   git fetch ${REMOTE}
   ```

2. **Check if fast-forward is possible**:
   ```bash
   git merge-base --is-ancestor HEAD ${REMOTE}/${BRANCH}
   ```

   If exit code is 0: fast-forward is possible
   If exit code is non-0: fast-forward is NOT possible

3. **If fast-forward possible, perform merge**:
   ```bash
   git merge --ff-only ${REMOTE}/${BRANCH}
   ```

   Report success:
   > "Successfully fast-forwarded to ${REMOTE}/${BRANCH}"

   Show new commits:
   ```bash
   git log --oneline -10
   ```

4. **If fast-forward NOT possible**:
   > **Fast-forward not possible**
   >
   > Your branch has diverged from ${REMOTE}/${BRANCH}. This means you have local commits that aren't on the remote.
   >
   > Your options:
   >
   > 1. **Rebase** (recommended for feature branches):
   >    ```bash
   >    /git:fr
   >    ```
   >    This replays your commits on top of the remote branch.
   >
   > 2. **Merge** (creates a merge commit):
   >    ```bash
   >    git merge ${REMOTE}/${BRANCH}
   >    ```
   >    This preserves both histories with a merge commit.
   >
   > 3. **Reset** (discard local commits - destructive!):
   >    ```bash
   >    git reset --hard ${REMOTE}/${BRANCH}
   >    ```
   >    **Warning**: This discards your local commits permanently.

## Notes

- Fast-forward is the safest way to update a branch—no history rewriting, no merge commits
- Ideal for pulling updates on branches you haven't modified locally
- If you need to incorporate changes from a branch you've worked on, use `/git:fr` instead
- This command never creates merge commits or rewrites history
