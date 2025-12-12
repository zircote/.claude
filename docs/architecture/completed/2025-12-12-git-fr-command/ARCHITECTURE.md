---
document_type: architecture
project_id: ARCH-2025-12-12-001
version: 1.0.0
last_updated: 2025-12-12T00:00:00Z
status: draft
---

# Git Workflow Commands Suite - Technical Architecture

## System Overview

This project adds four new slash command files to the existing `commands/git/` directory. Each command is a markdown file that Claude Code interprets as a prompt template, guiding Claude's behavior when the user invokes the command.

### Architecture Diagram

```
commands/
└── git/
    ├── cm.md          # Existing: commit
    ├── cp.md          # Existing: commit + push
    ├── pr.md          # Existing: pull request
    ├── fr.md          # NEW: fetch + rebase
    ├── sync.md        # NEW: fetch + rebase + push
    ├── ff.md          # NEW: fast-forward merge
    └── prune.md       # NEW: clean stale branches
```

### Key Design Decisions

1. **Stateless commands with context persistence**: Commands don't store state; session preferences (like custom remote) persist through Claude's conversation memory
2. **Prompt-based architecture**: Commands are prompts, not scripts—Claude interprets and executes
3. **Safety-first defaults**: Dry-runs, confirmations, and warnings built into prompt instructions
4. **Pattern consistency**: All commands follow the established frontmatter + numbered steps format

## Component Design

### Component 1: `/git:fr` (fr.md)

- **Purpose**: Fetch from remote and rebase current branch onto remote branch
- **Responsibilities**:
  - Check for dirty working directory
  - Fetch from specified/default remote
  - Rebase onto specified/default branch
  - Guide user through conflicts if they occur
- **Interfaces**: Arguments `[remote] [branch]`, defaults to `origin` and tracking branch
- **Dependencies**: Git CLI

### Component 2: `/git:sync` (sync.md)

- **Purpose**: Complete sync cycle—fetch, rebase, and push
- **Responsibilities**:
  - All responsibilities of `/git:fr`
  - Push changes after successful rebase
  - Confirm before pushing (safety for shared branches)
- **Interfaces**: Arguments `[remote] [branch]`
- **Dependencies**: Git CLI, builds on `/git:fr` patterns

### Component 3: `/git:ff` (ff.md)

- **Purpose**: Fast-forward merge only (no rebase, no merge commits)
- **Responsibilities**:
  - Fetch from remote
  - Attempt fast-forward merge
  - Fail gracefully if fast-forward not possible
  - Suggest alternatives when FF fails
- **Interfaces**: Arguments `[remote] [branch]`
- **Dependencies**: Git CLI

### Component 4: `/git:prune` (prune.md)

- **Purpose**: Clean up local branches that no longer exist on remote
- **Responsibilities**:
  - Fetch with prune to update remote tracking info
  - List branches marked as "gone"
  - Dry-run by default (list only)
  - Delete branches only with `--force` flag
- **Interfaces**: Optional `--force` flag
- **Dependencies**: Git CLI

## Command File Structure

All commands follow this template structure:

```markdown
---
description: [Brief description for help/discovery]
argument-hint: [Optional argument placeholder]
---

## Variables (if applicable)

REMOTE: $1 (defaults to `origin`)
BRANCH: $2 (defaults to upstream tracking branch)

## Pre-flight Checks

1. [Safety checks before main operation]

## Workflow

1. [Step-by-step instructions]
2. [Each step is imperative]
3. [Include decision points]

## Error Handling

### [Error Scenario]
[How to handle and guide user]

## Notes

- [Additional context]
- [Safety reminders]
```

## Behavioral Specifications

### Smart Default Resolution

```
REMOTE Resolution:
  IF $1 provided → use $1, remember for session
  ELSE IF session has previous override → use that
  ELSE → use "origin"

BRANCH Resolution:
  IF $2 provided → use $2
  ELSE IF current branch has upstream → use upstream branch name
  ELSE → prompt user: "No tracking branch found. Which branch to sync with?"
```

### Dirty Working Directory Handling

```
IF git status shows uncommitted changes:
  → Display warning with file list
  → Ask user: "You have uncommitted changes. Options:
     A) Stash changes, proceed, then pop stash
     B) Abort and commit/stash manually first
     C) Proceed anyway (risky)"
  → Wait for user choice
  → Execute chosen path
```

### Conflict Resolution Guidance

When rebase encounters conflicts, provide:

```markdown
## Rebase Conflict Detected

The rebase stopped due to conflicts in the following files:
- [file1]
- [file2]

### To resolve:

1. Open each conflicted file and resolve the conflicts
   - Look for `<<<<<<<`, `=======`, and `>>>>>>>` markers
   - Keep the changes you want, remove the markers

2. After resolving each file:
   ```bash
   git add <resolved-file>
   ```

3. Continue the rebase:
   ```bash
   git rebase --continue
   ```

### If you want to abort:
```bash
git rebase --abort
```
This will restore your branch to its state before the rebase.

### Need help with a specific conflict?
Tell me which file and I'll help analyze the conflicting changes.
```

### Prune Safety Protocol

```
ALWAYS:
  1. Run `git fetch --prune` to update remote tracking info
  2. List branches where upstream is "gone":
     git branch -vv | grep ': gone]'
  3. Display list to user

IF --force NOT provided:
  → Display: "These branches would be deleted. Run with --force to delete."
  → STOP (dry-run complete)

IF --force provided:
  → Confirm: "Delete these N branches? (y/n)"
  → IF confirmed → delete each branch
  → Display summary of deleted branches
```

## Integration Points

### Internal Integrations

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| Existing `/git` commands | Pattern reference | Consistency |
| Conversation context | Memory | Session preferences |

### External Integrations

| Service | Integration Type | Purpose |
|---------|-----------------|---------|
| Git CLI | Command execution | All git operations |

## Security Considerations

### Data Protection

- **Uncommitted changes**: Always warn before operations that could lose work
- **Branch deletion**: Require explicit `--force` flag
- **Push operations**: Confirm before pushing to shared branches

### Safe Defaults

| Operation | Default Behavior | Override |
|-----------|------------------|----------|
| Rebase with dirty tree | Ask user | User choice |
| Branch deletion | Dry-run only | `--force` flag |
| Push after sync | Confirm first | User approval |

## Testing Strategy

### Manual Testing Checklist

For each command, verify:

- [ ] Works with no arguments (uses defaults)
- [ ] Works with explicit remote argument
- [ ] Works with explicit remote and branch arguments
- [ ] Handles dirty working directory appropriately
- [ ] Handles missing tracking branch gracefully
- [ ] Provides clear error messages
- [ ] Conflict guidance is actionable (for fr/sync)
- [ ] Dry-run works correctly (for prune)
- [ ] `--force` works correctly (for prune)

### Edge Cases to Test

| Scenario | Expected Behavior |
|----------|-------------------|
| No upstream tracking branch | Prompt user for branch |
| Already up-to-date | Inform user, no action needed |
| Fast-forward not possible (for ff) | Clear message with alternatives |
| No stale branches (for prune) | "No branches to clean up" |
| Rebase in progress | Detect and offer to continue/abort |

## Deployment Considerations

### File Placement

All files go in `commands/git/` directory:

```bash
commands/git/fr.md
commands/git/sync.md
commands/git/ff.md
commands/git/prune.md
```

### Documentation Updates

After implementation:

1. Update `CLAUDE.md` with new commands in Git Workflow table
2. Commands auto-discovered by Claude Code from `commands/` directory

## Future Considerations

- **`/git:fr --interactive`**: Preview commits before rebasing
- **`/git:sync --no-push`**: Fetch+rebase without push
- **`/git:prune --include-merged`**: Also prune merged branches
- **Integration with worktree-manager**: Sync across worktrees
