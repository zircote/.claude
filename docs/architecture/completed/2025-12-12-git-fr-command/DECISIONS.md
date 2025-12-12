---
document_type: decisions
project_id: ARCH-2025-12-12-001
---

# Git Workflow Commands Suite - Architecture Decision Records

## ADR-001: Rebase Over Merge for Sync Operations

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

When synchronizing a local branch with a remote branch, there are two primary strategies:
1. **Merge**: Creates a merge commit, preserves exact history
2. **Rebase**: Replays commits on top of remote, creates linear history

### Decision

Use rebase as the default synchronization strategy for `/git:fr` and `/git:sync`.

### Consequences

**Positive:**
- Cleaner, linear commit history
- Easier to understand project evolution
- Avoids merge commit clutter

**Negative:**
- Rewrites commit history (problematic for shared branches)
- Can cause conflicts that need manual resolution
- Requires more git knowledge from users

**Neutral:**
- Consistent with many team workflows that prefer rebase

### Alternatives Considered

1. **Merge by default**: Safer but creates messier history
2. **User choice each time**: Too much friction for common operation
3. **Provide both**: Implemented via `/git:ff` for fast-forward-only merge option

---

## ADR-002: Ask User for Dirty Working Directory

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

When a user runs a sync command with uncommitted changes, we need to decide how to handle this safely.

Options considered:
- A) Abort with warning (safest, but blocks workflow)
- B) Auto-stash, operate, pop stash (convenient, but risky)
- C) Ask user each time (balanced approach)

### Decision

Ask the user each time (Option C).

### Consequences

**Positive:**
- User maintains control over their uncommitted work
- Educates user about the risks
- Flexible for different situations

**Negative:**
- Extra step in common workflow
- Could become tedious for frequent users

**Neutral:**
- Consistent with safety-first philosophy

### Alternatives Considered

1. **Auto-abort**: Too restrictive, blocks legitimate workflows
2. **Auto-stash**: Risk of stash conflicts, user may forget changes exist

---

## ADR-003: Dry-Run Default for Branch Deletion

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

The `/git:prune` command deletes local branches. Accidental deletion could cause data loss (unmerged work).

### Decision

Dry-run by default; require explicit `--force` flag to execute deletion.

### Consequences

**Positive:**
- Prevents accidental data loss
- Users see what would be deleted before committing
- Follows principle of least surprise

**Negative:**
- Two-step process for actual cleanup
- Slightly more friction than auto-delete

**Neutral:**
- Consistent with destructive git operations (e.g., `git clean -n`)

### Alternatives Considered

1. **Auto-delete with confirmation**: Still risky if user clicks through
2. **Interactive selection**: More complex, out of scope for MVP

---

## ADR-004: Session Persistence via Conversation Context

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

Users may want to specify a non-default remote (e.g., `upstream` instead of `origin`) and have that choice persist during a working session.

### Decision

Rely on Claude's conversation memory to persist remote override within a session. No external state storage.

### Consequences

**Positive:**
- Zero configuration required
- Works naturally with Claude Code's architecture
- No file pollution or state management complexity

**Negative:**
- Persistence limited to conversation session
- Not visible/editable by user outside conversation
- Resets on new session

**Neutral:**
- Acceptable limitation for this use case

### Alternatives Considered

1. **Config file**: Overkill for session preference
2. **Environment variable**: Complex to manage
3. **Per-command argument required**: Too much friction

---

## ADR-005: Smart Default Branch Detection with Fallback Prompts

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

Users may invoke sync commands on branches without upstream tracking configured.

### Decision

Implement smart detection: use tracking branch if available, prompt user if not.

### Consequences

**Positive:**
- Works seamlessly for common case (tracking branch exists)
- Graceful degradation for edge cases
- User isn't blocked by missing configuration

**Negative:**
- Extra prompt in edge cases
- User must know which branch to sync with

**Neutral:**
- Educational moment for git beginners

### Alternatives Considered

1. **Fail if no tracking branch**: Too restrictive
2. **Always require explicit branch**: Too much friction
3. **Guess from remote branches**: Risky, could sync to wrong branch

---

## ADR-006: Provide Conflict Resolution Guidance Over Auto-Abort

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

When rebase encounters conflicts, we could either abort automatically or guide the user through resolution.

### Decision

Provide step-by-step conflict resolution guidance.

### Consequences

**Positive:**
- Users learn to handle conflicts
- Completes more rebases successfully
- Reduces fear of rebasing

**Negative:**
- Requires more user engagement
- Claude needs to provide clear, actionable guidance
- May still be intimidating for git beginners

**Neutral:**
- Matches Claude Code's educational approach

### Alternatives Considered

1. **Auto-abort**: User never learns, problem persists
2. **Minimal intervention (just show error)**: Not helpful enough
3. **Auto-resolve with AI**: Out of scope, risky
