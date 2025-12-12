---
document_type: requirements
project_id: ARCH-2025-12-12-001
version: 1.0.0
last_updated: 2025-12-12T19:50:00Z
status: in-review
---

# Architecture Lifecycle Automation - Product Requirements Document

## Executive Summary

The `/arch` command suite successfully creates comprehensive planning artifacts (requirements, architecture, implementation plans) but operates in a **write-once, read-only** pattern. Once documents are created, they remain static—checkboxes don't update as tasks complete, status transitions don't occur automatically, and frontmatter metadata becomes stale.

This project introduces `/arch:i` (implement), a new command that activates **implementation mode** with intelligent state tracking. It auto-detects the project from the current branch, loads context efficiently via a hybrid checkpoint system, and automatically updates all state-bearing documents as work progresses. The result is a living planning system that accurately reflects implementation reality.

## Problem Statement

### The Problem

When implementing architecture plans created by `/arch:p`, developers must manually:
1. Check off task checkboxes in `IMPLEMENTATION_PLAN.md` as they complete work
2. Update status fields in `README.md` frontmatter (draft → in-progress → completed)
3. Update timestamps (`started`, `completed`, `last_updated`)
4. Add CHANGELOG entries for significant transitions
5. Track acceptance criteria completion in `REQUIREMENTS.md`

This manual overhead creates friction, leads to stale documentation, and breaks the promise of a managed architecture lifecycle.

### Impact

- **Cognitive load**: Developers must context-switch from implementation to documentation
- **Stale artifacts**: Documents drift from reality, reducing their value
- **Lost progress**: Multi-session implementations lose state; work must be mentally reconstructed
- **Inconsistent state**: Different documents show conflicting status (e.g., tasks done but status still "draft")

### Current State

The existing `/arch` suite provides:
- `/arch:p` — Creates planning artifacts (7 documents) with static content
- `/arch:s` — Displays portfolio status (read-only, no mutations)
- `/arch:c` — Closes completed projects (updates only at the end)

**Gap**: No command manages state *during* implementation.

## Goals and Success Criteria

### Primary Goal

Enable Claude to automatically maintain accurate, synchronized state across all architecture planning documents as implementation progresses.

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Manual checkbox updates required | 0 | User never manually edits checkboxes |
| Status transition accuracy | 100% | Status always reflects actual phase |
| Cross-session state recovery | < 30 seconds | Time to resume after `/arch:i` |
| Document sync errors | 0 | No conflicting state across documents |
| Divergence capture rate | 100% | All plan deviations logged |

### Non-Goals (Explicit Exclusions)

- **External integrations**: No GitHub Issues, Jira, or external PM tool sync (future consideration)
- **Multi-user coordination**: Single-developer workflow; no concurrent edit handling
- **Undo/rollback**: No reverting completed tasks to pending (manual edit if needed)
- **Automated testing**: Does not run tests to verify task completion (relies on Claude's judgment)

## User Analysis

### Primary Users

- **Who**: Developers using Claude Code with the `/arch` command suite
- **Needs**: Accurate documentation that reflects implementation reality without manual maintenance
- **Context**: Working in isolated worktrees on architecture projects, often across multiple sessions

### User Stories

1. As a developer, I want Claude to automatically check off tasks as I complete them, so my implementation plan stays accurate without manual updates.

2. As a developer, I want the project status to transition automatically (draft → in-progress → completed), so README.md always reflects reality.

3. As a developer, I want to resume implementation in a new Claude session and have full context of what's done and what's pending, so I don't lose progress.

4. As a developer, I want divergences from the plan (added tasks, skipped tasks) to be tracked and flagged, so I can review and approve changes.

5. As a developer, I want CHANGELOG.md to automatically record significant transitions, so I have an audit trail of implementation progress.

## Functional Requirements

### Must Have (P0)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-001 | `/arch:i` command that activates implementation mode | Core enabler for all automation | Command exists, loads project context, creates PROGRESS.md if missing |
| FR-002 | Auto-detect project from current branch name | Reduces friction; follows convention | Branch `fix/foo` matches project with slug containing "foo" |
| FR-003 | Create and maintain `PROGRESS.md` checkpoint file | Enables session persistence | File created on first `/arch:i`, updated on each state change |
| FR-004 | Auto-update task checkboxes in `IMPLEMENTATION_PLAN.md` | Primary pain point | When task completed, `- [ ]` becomes `- [x]` with timestamp comment |
| FR-005 | Auto-update `README.md` frontmatter status | Keep project metadata current | `status`, `started`, `completed`, `last_updated` fields synced |
| FR-006 | Hierarchical status rollup (task → phase → project) | Accurate aggregate status | Phase marked complete when all tasks done; project complete when all phases done |
| FR-007 | Persist state across Claude sessions | Multi-session implementations | `/arch:i` in new session reads PROGRESS.md and resumes |

### Should Have (P1)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-101 | Auto-append CHANGELOG.md entries on transitions | Audit trail | Status changes, phase completions logged with timestamps |
| FR-102 | Track acceptance criteria completion in `REQUIREMENTS.md` | Full lifecycle tracking | When implementing task that satisfies criteria, checkbox updated |
| FR-103 | Divergence logging with user notification | Handle reality vs plan | Added/skipped/modified tasks logged in PROGRESS.md Divergence Log |
| FR-104 | Allow dynamic task addition during implementation | Plans evolve | New tasks can be added; marked as "unplanned" in divergence log |
| FR-105 | Allow task skipping with reason | Not all tasks needed | Skipped tasks logged; don't block phase completion |
| FR-106 | Update `DECISIONS.md` ADR status when decisions validated | Complete lifecycle | ADR status: Proposed → Accepted when implementation confirms decision |

### Nice to Have (P2)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-201 | Implementation brief generation | Efficient context loading | Condensed summary of current state for session start |
| FR-202 | Progress visualization in `/arch:s` | Better status display | Show percentage complete, current phase, blockers |
| FR-203 | Estimated vs actual effort tracking | Improve future estimates | Track time spent; compare to IMPLEMENTATION_PLAN.md estimates |
| FR-204 | Session notes capture | Context preservation | Capture what was discussed/decided each session |

## Non-Functional Requirements

### Performance

- `/arch:i` startup: < 5 seconds to load context and be ready for implementation
- State update latency: < 1 second per document update
- PROGRESS.md should not exceed 50KB (avoid bloat)

### Reliability

- No data loss: All state changes persisted before confirmation to user
- Graceful degradation: If PROGRESS.md corrupted, can rebuild from document checkboxes
- Idempotent updates: Running same update twice produces same result

### Maintainability

- `/arch:i` command follows existing `/arch` command patterns (YAML frontmatter, allowed-tools)
- PROGRESS.md format is human-readable and manually editable if needed
- Clear separation: PROGRESS.md is source of truth; other documents are derived

### Compatibility

- Works with existing `/arch:p` generated documents (no migration needed)
- Works alongside `/arch:s` (status) and `/arch:c` (close)
- Compatible with worktree-manager skill workflow

## Technical Constraints

- Must be implemented as a Claude Code slash command (`.md` file in `commands/arch/`)
- Must use Opus 4.5 model for intelligent detection capabilities
- Must not require external dependencies (no npm packages, APIs)
- File operations limited to project's `docs/architecture/` directory

## Dependencies

### Internal Dependencies

- Existing `/arch:p` document templates (structure must be parseable)
- Existing `/arch:s` and `/arch:c` commands (should remain functional)
- Git for branch name detection

### External Dependencies

- None (self-contained within Claude Code)

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PROGRESS.md format changes break parsing | Medium | High | Version the format; include migration logic |
| Branch name doesn't match any project | Medium | Medium | Interactive project selection fallback |
| Large projects exceed context limits | Low | High | Progressive loading; summarization |
| User manually edits checkboxes causing desync | Medium | Medium | Reconciliation on `/arch:i` startup |
| Multiple active projects on same branch | Low | Medium | Prompt user to select which project |

## Open Questions

- [x] How to detect project from branch? → Match branch slug to project slug
- [x] Where to store implementation state? → PROGRESS.md checkpoint file
- [x] How granular should tracking be? → Hierarchical: task → phase → project
- [x] How to handle divergence? → Log + flag for user; allow dynamic updates

## Appendix

### Glossary

| Term | Definition |
|------|------------|
| Implementation mode | State where Claude actively tracks and updates planning artifacts |
| Checkpoint file | PROGRESS.md - persists implementation state across sessions |
| Divergence | Difference between original plan and implementation reality |
| Hierarchical rollup | Aggregating status from tasks → phases → project |

### References

- [RESEARCH_NOTES.md](./RESEARCH_NOTES.md) - Codebase analysis findings
- `commands/arch/p.md` - Existing planner command (lines 1-1226)
- `commands/arch/s.md` - Existing status command (lines 1-272)
- `commands/arch/c.md` - Existing close-out command (lines 1-230)
