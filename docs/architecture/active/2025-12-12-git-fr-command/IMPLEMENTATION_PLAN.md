---
document_type: implementation_plan
project_id: ARCH-2025-12-12-001
version: 1.0.0
last_updated: 2025-12-12T00:00:00Z
status: draft
estimated_effort: Low (4 command files + documentation)
---

# Git Workflow Commands Suite - Implementation Plan

## Overview

Implementation of four new `/git` slash commands following established patterns. Each command is a markdown file in `commands/git/` that Claude Code interprets as a prompt template.

## Phase Summary

| Phase | Key Deliverables |
|-------|------------------|
| Phase 1: Foundation | `/git:fr` - core fetch+rebase command |
| Phase 2: Extensions | `/git:sync`, `/git:ff` - sync and fast-forward |
| Phase 3: Maintenance | `/git:prune` - stale branch cleanup |
| Phase 4: Documentation | CLAUDE.md updates, testing |

---

## Phase 1: Foundation

**Goal**: Implement the core `/git:fr` command with all safety features

### Tasks

#### Task 1.1: Create fr.md command file

- **Description**: Create the fetch-rebase command following existing patterns
- **File**: `commands/git/fr.md`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] YAML frontmatter with description and argument-hint
  - [ ] Variables section for REMOTE and BRANCH with defaults
  - [ ] Pre-flight check for dirty working directory
  - [ ] Workflow steps for fetch and rebase
  - [ ] Conflict resolution guidance section
  - [ ] Session persistence note for remote override

#### Task 1.2: Test fr.md manually

- **Description**: Verify command works in various scenarios
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Works with no arguments
  - [ ] Works with custom remote
  - [ ] Works with custom remote and branch
  - [ ] Prompts correctly on dirty working directory
  - [ ] Handles missing tracking branch gracefully

### Phase 1 Deliverables

- [ ] `commands/git/fr.md` - Functional fetch-rebase command

### Phase 1 Exit Criteria

- [ ] `/git:fr` executes successfully in common scenarios
- [ ] Safety prompts work as designed

---

## Phase 2: Extensions

**Goal**: Add sync and fast-forward commands building on fr.md patterns

### Tasks

#### Task 2.1: Create sync.md command file

- **Description**: Create the full sync (fetch+rebase+push) command
- **File**: `commands/git/sync.md`
- **Dependencies**: Task 1.1 (uses same patterns)
- **Acceptance Criteria**:
  - [ ] Includes all fr.md functionality
  - [ ] Adds push step after successful rebase
  - [ ] Confirms before pushing to remote
  - [ ] Handles push failures gracefully

#### Task 2.2: Create ff.md command file

- **Description**: Create the fast-forward-only merge command
- **File**: `commands/git/ff.md`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] YAML frontmatter with description
  - [ ] Attempts fast-forward merge only
  - [ ] Clear failure message if FF not possible
  - [ ] Suggests alternatives (rebase, merge) on failure

#### Task 2.3: Test sync.md and ff.md

- **Description**: Verify both commands work correctly
- **Dependencies**: Tasks 2.1, 2.2
- **Acceptance Criteria**:
  - [ ] sync completes full cycle successfully
  - [ ] sync prompts before push
  - [ ] ff succeeds when fast-forward possible
  - [ ] ff fails gracefully with helpful message

### Phase 2 Deliverables

- [ ] `commands/git/sync.md` - Full sync command
- [ ] `commands/git/ff.md` - Fast-forward merge command

### Phase 2 Exit Criteria

- [ ] Both commands function correctly
- [ ] Error handling provides useful guidance

---

## Phase 3: Maintenance

**Goal**: Add branch cleanup command with safety guards

### Tasks

#### Task 3.1: Create prune.md command file

- **Description**: Create the stale branch cleanup command
- **File**: `commands/git/prune.md`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] YAML frontmatter with description and argument-hint for --force
  - [ ] Fetches with prune to update remote tracking
  - [ ] Lists branches with "gone" upstream
  - [ ] Dry-run by default (list only, no deletion)
  - [ ] Deletes branches only with --force flag
  - [ ] Confirmation prompt before deletion even with --force

#### Task 3.2: Test prune.md

- **Description**: Verify prune command safety and functionality
- **Dependencies**: Task 3.1
- **Acceptance Criteria**:
  - [ ] Dry-run correctly shows branches without deleting
  - [ ] --force triggers deletion with confirmation
  - [ ] Handles "no stale branches" case gracefully
  - [ ] Protected branches (main, master, develop) excluded

### Phase 3 Deliverables

- [ ] `commands/git/prune.md` - Branch cleanup command

### Phase 3 Exit Criteria

- [ ] Prune command works safely
- [ ] No accidental deletions possible

---

## Phase 4: Documentation

**Goal**: Update documentation and finalize

### Tasks

#### Task 4.1: Update CLAUDE.md

- **Description**: Add new commands to the Git Workflow table
- **File**: `CLAUDE.md`
- **Dependencies**: All commands complete
- **Acceptance Criteria**:
  - [ ] `/git:fr` added with description
  - [ ] `/git:sync` added with description
  - [ ] `/git:ff` added with description
  - [ ] `/git:prune` added with description

#### Task 4.2: Final testing sweep

- **Description**: End-to-end testing of all four commands
- **Dependencies**: Tasks 1-3 complete
- **Acceptance Criteria**:
  - [ ] All commands work from fresh session
  - [ ] Session persistence works for remote override
  - [ ] All error cases handled gracefully
  - [ ] Documentation matches implementation

### Phase 4 Deliverables

- [ ] Updated CLAUDE.md
- [ ] All commands tested and verified

### Phase 4 Exit Criteria

- [ ] Documentation complete
- [ ] All tests pass

---

## Dependency Graph

```
Phase 1:
  Task 1.1 (fr.md) ──► Task 1.2 (test fr)
       │
       └────────────────────────┐
                                │
Phase 2:                        ▼
  Task 2.1 (sync.md) ─────► Task 2.3 (test)
  Task 2.2 (ff.md) ────────┘

Phase 3:
  Task 3.1 (prune.md) ──► Task 3.2 (test prune)

Phase 4:
  All above ──► Task 4.1 (CLAUDE.md) ──► Task 4.2 (final test)
```

## Risk Mitigation Tasks

| Risk | Mitigation Task | Phase |
|------|-----------------|-------|
| Conflicts confuse users | Detailed guidance in fr.md | 1 |
| Accidental branch deletion | Dry-run default + confirmation | 3 |
| Missing tracking branch | Smart detection + prompt | 1 |

## Testing Checklist

### Unit Testing (per command)

- [ ] `/git:fr` - fetch and rebase operations
- [ ] `/git:sync` - full sync cycle
- [ ] `/git:ff` - fast-forward merge
- [ ] `/git:prune` - branch listing and deletion

### Integration Testing

- [ ] Session persistence for remote override
- [ ] Dirty working directory handling across commands
- [ ] Error recovery guidance

### Edge Case Testing

- [ ] No upstream tracking branch
- [ ] Already up-to-date
- [ ] Rebase in progress
- [ ] No stale branches to prune
- [ ] Fast-forward not possible

## Documentation Tasks

- [ ] Update CLAUDE.md Git Workflow table
- [ ] Commands self-document via frontmatter description

## Launch Checklist

- [ ] All four command files created
- [ ] CLAUDE.md updated
- [ ] Manual testing complete
- [ ] Edge cases verified

## Post-Launch

- [ ] Monitor for user issues
- [ ] Gather feedback on conflict guidance
- [ ] Consider additional flags (`--no-push`, `--interactive`)
