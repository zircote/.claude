---
description: Full sync - fetch, rebase onto remote branch, and push
argument-hint: "[remote] [branch]"
---

Perform a full sync cycle: fetch from remote, rebase current branch, and push:

## Variables

- **REMOTE**: First argument, defaults to `origin`
- **BRANCH**: Second argument, defaults to current branch's upstream tracking branch

If user previously specified a different remote in this session, use that as the default instead of `origin`.

## Pre-flight Checks

1. **Check for uncommitted changes**:
   ```bash
   git status --porcelain
   ```

   If there are uncommitted changes, display a warning with the file list and ask the user:
   > "You have uncommitted changes. How would you like to proceed?
   > A) Stash changes, proceed with sync, then pop stash
   > B) Abort and let me commit/stash manually first
   > C) Proceed anyway (risky - changes may conflict)"

   Wait for user choice before continuing.

2. **Check for existing rebase in progress**:
   ```bash
   ls .git/rebase-merge .git/rebase-apply 2>/dev/null
   ```

   If rebase is in progress, inform user and offer:
   > "A rebase is already in progress. Options:
   > - `git rebase --continue` (after resolving conflicts)
   > - `git rebase --abort` (to cancel and restore original state)"

3. **Determine target branch**:
   - If BRANCH not specified, get upstream:
     ```bash
     git rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null
     ```
   - If no upstream tracking branch, ask user which branch to sync with

## Workflow

1. **Fetch from remote**:
   ```bash
   git fetch ${REMOTE}
   ```
   Display fetch output to show what was retrieved.

2. **Show divergence** (informational):
   ```bash
   git log --oneline HEAD..${REMOTE}/${BRANCH} | head -10
   ```
   Display incoming commits (if any).

3. **Rebase onto remote branch**:
   ```bash
   git rebase ${REMOTE}/${BRANCH}
   ```

   If conflicts occur, stop and provide conflict resolution guidance (see below).

4. **Confirm before push**:
   After successful rebase, show what will be pushed:
   ```bash
   git log --oneline ${REMOTE}/${BRANCH}..HEAD
   ```

   Ask user:
   > "Ready to push these commits to ${REMOTE}/${BRANCH}? (y/n)"

   Only proceed with push if user confirms.

5. **Push to remote**:
   ```bash
   git push ${REMOTE} HEAD
   ```

   If push fails due to non-fast-forward:
   > "Push rejected - remote has new commits. This can happen if someone else pushed while you were rebasing.
   > Options:
   > - Run `/git:sync` again to incorporate new remote changes
   > - Use `git push --force-with-lease` (only if you're certain)"

6. **Report success**:
   > "Successfully synced with ${REMOTE}/${BRANCH}"

   Show final status:
   ```bash
   git status
   ```

## Conflict Resolution

If the rebase encounters conflicts:

> **Rebase Conflict Detected**
>
> The rebase stopped due to conflicts. To resolve:
>
> 1. Open each conflicted file and resolve the conflicts
>    - Look for `<<<<<<<`, `=======`, and `>>>>>>>` markers
>    - Keep the changes you want, remove the markers
>
> 2. After resolving each file:
>    ```bash
>    git add <resolved-file>
>    ```
>
> 3. Continue the rebase:
>    ```bash
>    git rebase --continue
>    ```
>
> 4. After rebase completes, I'll continue with the push step.
>
> **To abort and restore original state:**
> ```bash
> git rebase --abort
> ```
>
> Tell me which file you need help with and I'll analyze the conflicting changes.

## Notes

- If user specifies a custom REMOTE, remember it for subsequent `/git:fr` or `/git:sync` calls in this session
- Always confirm before pushing to avoid accidental pushes to shared branches
- **DO NOT** use `--force` push unless explicitly requested by user
- This command performs a full sync cycle; use `/git:fr` if you only want fetch+rebase without push
