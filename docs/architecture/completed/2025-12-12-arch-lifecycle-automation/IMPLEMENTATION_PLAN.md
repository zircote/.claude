---
document_type: implementation_plan
project_id: ARCH-2025-12-12-001
version: 1.0.0
last_updated: 2025-12-12T20:10:00Z
status: in-review
estimated_effort: 8-12 hours
---

# Architecture Lifecycle Automation - Implementation Plan

## Overview

This plan implements the `/arch:i` command and supporting infrastructure in 4 phases: Foundation (command skeleton + PROGRESS.md), Core Logic (state management + sync), Integration (cross-document updates), and Polish (edge cases + documentation).

## Phase Summary

| Phase | Focus | Key Deliverables |
|-------|-------|------------------|
| Phase 1 | Foundation | `/arch:i` command file, PROGRESS.md template, project detection |
| Phase 2 | Core Logic | Task tracking, status transitions, hierarchical rollup |
| Phase 3 | Integration | Document sync engine, CHANGELOG automation |
| Phase 4 | Polish | Edge case handling, error recovery, documentation |

---

## Phase 1: Foundation

**Goal**: Create the basic `/arch:i` command structure and PROGRESS.md checkpoint system
**Prerequisites**: Understanding of existing `/arch` command patterns

### Tasks

#### Task 1.1: Create `/arch:i` command skeleton

- **Description**: Create `commands/arch/i.md` with YAML frontmatter, role definition, and basic structure following existing `/arch` command patterns
- **Acceptance Criteria**:
  - [ ] File created at `commands/arch/i.md`
  - [ ] YAML frontmatter includes: argument-hint, description, model (opus), allowed-tools
  - [ ] Role section defines Implementation Manager persona
  - [ ] Basic execution protocol structure in place

#### Task 1.2: Implement project detection logic

- **Description**: Add logic to detect the target architecture project from the current git branch name
- **Acceptance Criteria**:
  - [ ] Parse current branch name via `git branch --show-current`
  - [ ] Search `docs/architecture/active/*/README.md` for matching slug
  - [ ] Handle no-match case with helpful error message
  - [ ] Handle multiple-match case with interactive selection prompt
  - [ ] Support explicit project ID/slug argument override

#### Task 1.3: Define PROGRESS.md template structure

- **Description**: Design and document the PROGRESS.md checkpoint file format
- **Acceptance Criteria**:
  - [ ] YAML frontmatter schema defined (project_id, format_version, timestamps, current_phase, status)
  - [ ] Task Status table format defined (ID, Description, Status, Started, Completed, Notes)
  - [ ] Phase Status table format defined
  - [ ] Divergence Log table format defined
  - [ ] Session Notes section defined

#### Task 1.4: Implement PROGRESS.md initialization

- **Description**: Add logic to create PROGRESS.md on first `/arch:i` run for a project
- **Acceptance Criteria**:
  - [ ] Check if PROGRESS.md exists in project directory
  - [ ] If missing, create from template with tasks populated from IMPLEMENTATION_PLAN.md
  - [ ] Parse IMPLEMENTATION_PLAN.md to extract task IDs and descriptions
  - [ ] Initialize all tasks as `pending`
  - [ ] Set `implementation_started` timestamp

### Phase 1 Deliverables

- [ ] `commands/arch/i.md` file with basic structure
- [ ] Project detection working
- [ ] PROGRESS.md template defined
- [ ] PROGRESS.md auto-creation from IMPLEMENTATION_PLAN.md

### Phase 1 Exit Criteria

- [ ] Running `/arch:i` in a project worktree creates PROGRESS.md
- [ ] PROGRESS.md contains all tasks from IMPLEMENTATION_PLAN.md in pending state

---

## Phase 2: Core Logic

**Goal**: Implement task status management, hierarchical rollup, and session persistence
**Prerequisites**: Phase 1 complete

### Tasks

#### Task 2.1: Implement task status update logic

- **Description**: Add capability to mark tasks as in-progress, done, or skipped
- **Acceptance Criteria**:
  - [ ] When Claude completes work matching a task, update PROGRESS.md
  - [ ] Set `Started` timestamp when task moves from pending → in-progress
  - [ ] Set `Completed` timestamp when task moves to done
  - [ ] Support explicit "skip task X" instruction with reason
  - [ ] Update task status in PROGRESS.md Task Status table

#### Task 2.2: Implement phase status calculation

- **Description**: Calculate phase completion percentage and status from task states
- **Acceptance Criteria**:
  - [ ] Phase progress = (done + skipped) / total tasks in phase
  - [ ] Phase status transitions: pending → in-progress → done
  - [ ] Phase transitions to in-progress when first task starts
  - [ ] Phase transitions to done when all tasks done/skipped
  - [ ] Update Phase Status table in PROGRESS.md

#### Task 2.3: Implement project status derivation

- **Description**: Derive overall project status from phase states
- **Acceptance Criteria**:
  - [ ] Project status = derived from phase states
  - [ ] draft → in-progress when any task starts
  - [ ] in-progress → completed when all phases done
  - [ ] Update `project_status` in PROGRESS.md frontmatter
  - [ ] Update `current_phase` to reflect active phase

#### Task 2.4: Implement divergence tracking

- **Description**: Track and log deviations from the original plan
- **Acceptance Criteria**:
  - [ ] Log when task is skipped (type: skipped)
  - [ ] Log when task is added dynamically (type: added)
  - [ ] Log when task scope changes (type: modified)
  - [ ] Each entry includes: date, type, task ID, description, resolution
  - [ ] Notify user of divergence with option to approve/flag

#### Task 2.5: Implement session persistence

- **Description**: Ensure state persists across Claude sessions
- **Acceptance Criteria**:
  - [ ] On `/arch:i` startup, read existing PROGRESS.md
  - [ ] Display current state summary (phase, completed tasks, pending tasks)
  - [ ] Update `last_session` timestamp on each session start
  - [ ] Support resume workflow (no re-initialization needed)

### Phase 2 Deliverables

- [ ] Task status management working
- [ ] Phase rollup calculation working
- [ ] Project status derivation working
- [ ] Divergence logging working
- [ ] Multi-session resume working

### Phase 2 Exit Criteria

- [ ] Can mark tasks complete and see PROGRESS.md update
- [ ] Phase status auto-updates based on task completion
- [ ] Can close and reopen Claude session with state preserved

---

## Phase 3: Integration

**Goal**: Synchronize PROGRESS.md state to all state-bearing documents
**Prerequisites**: Phase 2 complete

### Tasks

#### Task 3.1: Implement IMPLEMENTATION_PLAN.md checkbox sync

- **Description**: When task marked done in PROGRESS.md, update checkbox in IMPLEMENTATION_PLAN.md
- **Acceptance Criteria**:
  - [ ] Find task in IMPLEMENTATION_PLAN.md by task ID pattern (e.g., "Task 1.1")
  - [ ] Change `- [ ]` to `- [x]` for completed tasks
  - [ ] Add timestamp comment after checkbox (optional)
  - [ ] Handle tasks that don't have checkboxes gracefully

#### Task 3.2: Implement README.md frontmatter sync

- **Description**: Keep README.md metadata synchronized with project state
- **Acceptance Criteria**:
  - [ ] Update `status` field when project status changes
  - [ ] Update `started` field when implementation begins
  - [ ] Update `completed` field when project completes
  - [ ] Update `last_updated` on every significant change

#### Task 3.3: Implement CHANGELOG.md auto-entries

- **Description**: Automatically append entries for significant transitions
- **Acceptance Criteria**:
  - [ ] Entry when implementation starts (status → in-progress)
  - [ ] Entry when phase completes
  - [ ] Entry when project completes
  - [ ] Entry for significant divergences (flagged items)
  - [ ] Entries follow existing CHANGELOG format

#### Task 3.4: Implement REQUIREMENTS.md criteria sync

- **Description**: Update acceptance criteria checkboxes when verified during implementation
- **Acceptance Criteria**:
  - [ ] Parse acceptance criteria checkboxes from REQUIREMENTS.md
  - [ ] When task completion satisfies a criterion, update checkbox
  - [ ] Link task completion to specific criteria (may require heuristics or explicit mapping)

#### Task 3.5: Implement sync orchestration

- **Description**: Coordinate all document updates after PROGRESS.md changes
- **Acceptance Criteria**:
  - [ ] After any PROGRESS.md update, trigger sync to relevant documents
  - [ ] Handle sync failures gracefully (log error, continue)
  - [ ] Provide summary of documents updated
  - [ ] Avoid redundant updates (only update if state actually changed)

### Phase 3 Deliverables

- [ ] IMPLEMENTATION_PLAN.md checkboxes auto-update
- [ ] README.md frontmatter stays current
- [ ] CHANGELOG.md receives automatic entries
- [ ] REQUIREMENTS.md criteria tracking (best effort)
- [ ] Sync engine coordinates all updates

### Phase 3 Exit Criteria

- [ ] Completing a task updates checkboxes in IMPLEMENTATION_PLAN.md
- [ ] Project status change updates README.md frontmatter
- [ ] Phase completion adds CHANGELOG entry

---

## Phase 4: Polish

**Goal**: Handle edge cases, improve error recovery, and document the feature
**Prerequisites**: Phase 3 complete

### Tasks

#### Task 4.1: Handle edge cases

- **Description**: Address known edge cases and unusual scenarios
- **Acceptance Criteria**:
  - [ ] No matching project: Clear error message with guidance
  - [ ] Multiple matching projects: Interactive selection
  - [ ] Empty IMPLEMENTATION_PLAN.md: Graceful handling
  - [ ] Manual checkbox edit: Reconciliation on startup
  - [ ] PROGRESS.md format corruption: Recovery guidance

#### Task 4.2: Add implementation brief generation

- **Description**: Generate concise summary of current state on `/arch:i` startup
- **Acceptance Criteria**:
  - [ ] Display project name and ID
  - [ ] Show current phase and overall progress
  - [ ] List recently completed tasks
  - [ ] List next pending tasks
  - [ ] Note any flagged divergences

#### Task 4.3: Update CLAUDE.md documentation

- **Description**: Document the new `/arch:i` command in project CLAUDE.md
- **Acceptance Criteria**:
  - [ ] Add `/arch:i` to Architecture Planning command table
  - [ ] Describe workflow: `/arch:p` → `/arch:i` → `/arch:s` → `/arch:c`
  - [ ] Document PROGRESS.md checkpoint system
  - [ ] Provide example usage

#### Task 4.4: Add validation and self-test

- **Description**: Implement basic validation to catch common issues
- **Acceptance Criteria**:
  - [ ] Validate PROGRESS.md format on load
  - [ ] Warn if task count doesn't match IMPLEMENTATION_PLAN.md
  - [ ] Warn if project status seems inconsistent with task states
  - [ ] Provide fix suggestions for detected issues

### Phase 4 Deliverables

- [ ] Edge cases handled gracefully
- [ ] Implementation brief displayed on startup
- [ ] CLAUDE.md documentation updated
- [ ] Validation and self-test in place

### Phase 4 Exit Criteria

- [ ] `/arch:i` handles all documented edge cases
- [ ] User has clear understanding of what's happening
- [ ] Feature is self-documenting

---

## Dependency Graph

```
Phase 1:
  Task 1.1 ──┬──► Task 1.2 ──┬──► Task 1.4
             │               │
             └──► Task 1.3 ──┘

Phase 2 (depends on Phase 1):
  Task 2.1 ──┬──► Task 2.2 ──► Task 2.3
             │
             └──► Task 2.4

  Task 2.5 (parallel to above)

Phase 3 (depends on Phase 2):
  Task 3.1 ──┐
  Task 3.2 ──┼──► Task 3.5
  Task 3.3 ──┤
  Task 3.4 ──┘

Phase 4 (depends on Phase 3):
  Task 4.1 ──┐
  Task 4.2 ──┼──► (All can be parallelized)
  Task 4.3 ──┤
  Task 4.4 ──┘
```

## Risk Mitigation Tasks

| Risk | Mitigation Task | Phase |
|------|-----------------|-------|
| PROGRESS.md format changes break parsing | Version format in frontmatter; add migration logic | Phase 1 |
| Branch name doesn't match project | Interactive fallback selection | Phase 1 |
| User manually edits checkboxes causing desync | Reconciliation on startup | Phase 4 |
| Large projects exceed context limits | Progressive loading (future) | Phase 4 |

## Testing Checklist

- [ ] Unit test: Task status transitions
- [ ] Unit test: Phase completion calculation
- [ ] Unit test: Project status derivation
- [ ] Integration test: PROGRESS.md → IMPLEMENTATION_PLAN.md sync
- [ ] Integration test: Full lifecycle (start → complete)
- [ ] Integration test: Multi-session resume
- [ ] Edge case: No matching project
- [ ] Edge case: Manual checkbox edit
- [ ] Edge case: Skipped tasks

## Documentation Tasks

- [ ] Update CLAUDE.md with `/arch:i` command
- [ ] Add inline documentation in `i.md` command file
- [ ] Document PROGRESS.md format for users who want to manually edit

## Launch Checklist

- [ ] All Phase 1-4 tasks complete
- [ ] Testing checklist complete
- [ ] Documentation tasks complete
- [ ] Tested with real project (this planning project!)
- [ ] Ready for PR to main

## Post-Launch

- [ ] Monitor for issues during first uses
- [ ] Gather feedback on workflow
- [ ] Consider `/arch:s` integration (P2)
- [ ] Consider estimated vs actual effort tracking (P2)
