---
document_type: research
project_id: ARCH-2025-12-12-001
last_updated: 2025-12-12T19:45:00Z
---

# Architecture Lifecycle Automation - Research Notes

## Research Summary

Comprehensive analysis of the existing `/arch` command suite reveals a **write-once, read-only** pattern where planning artifacts are created but never actively managed during implementation. The suite lacks state management, progress tracking, and automatic document updates as work progresses.

## Codebase Analysis

### Relevant Files Examined

| File | Lines | Purpose | Key Findings |
|------|-------|---------|--------------|
| `commands/arch/p.md` | 1-1226 | Strategic project planner | Creates 7 document types; no update logic |
| `commands/arch/s.md` | 1-272 | Status/portfolio viewer | Read-only display; no state mutation |
| `commands/arch/c.md` | 1-230 | Project close-out | Only updates at project end |
| `skills/worktree-manager/SKILL.md` | 1-870 | Worktree management | Has registry pattern worth emulating |
| `skills/worktree-manager/scripts/launch-agent.sh` | 1-261 | Agent launcher | Template variable substitution pattern |

### Existing Patterns Identified

1. **YAML Frontmatter for Metadata** (`p.md:64-81`)
   - All documents use YAML frontmatter with `status`, `last_updated`, `version`
   - Currently static after creation—never programmatically updated
   - Example fields: `project_id`, `status`, `created`, `approved`, `started`, `completed`, `expires`

2. **Checkbox-based Progress Tracking** (`p.md:800-820`)
   - `IMPLEMENTATION_PLAN.md` uses `- [ ]` checkboxes for tasks
   - `REQUIREMENTS.md` uses checkboxes for acceptance criteria
   - Quality gates and launch checklists use checkboxes
   - **Problem**: No mechanism to auto-check these during implementation

3. **Lifecycle States** (`p.md:54-62`)
   ```
   draft → in-review → approved → in-progress → completed → superseded
   ```
   - States defined but transitions are manual
   - No triggers or automation for state changes

4. **Model Tiering Strategy** (`p.md:4`, `s.md:4`, `c.md:4`)
   - `/arch:p` uses Opus 4.5 (complex reasoning)
   - `/arch:s` and `/arch:c` use Sonnet (simpler operations)
   - **Implication**: `/arch:i` should use Opus for intelligent detection

5. **Registry Pattern in worktree-manager** (`SKILL.md:129-180`)
   - Global JSON registry at `~/.claude/worktree-registry.json`
   - Tracks state with timestamps (`createdAt`, `validatedAt`, `agentLaunchedAt`)
   - **Opportunity**: Similar pattern for `PROGRESS.md` checkpoint

### Integration Points

| System | Integration Method | Notes |
|--------|-------------------|-------|
| Git | Branch name detection | `/arch:i` auto-detects project from branch |
| File system | Document paths | `docs/architecture/active/[date]-[slug]/` |
| YAML frontmatter | Metadata storage | Status, timestamps, version |
| Markdown checkboxes | Progress indicators | `- [ ]` / `- [x]` syntax |
| CHANGELOG.md | Audit trail | Append entries on transitions |

## Technical Research

### Best Practices Found

| Topic | Source | Key Insight |
|-------|--------|-------------|
| State machines | General SWE | Explicit state transitions with guards |
| Checkpoint/resume patterns | ML training | Periodic saves enable session recovery |
| Progressive disclosure | UX | Load only what's needed, expand on demand |
| Hierarchical tracking | Project management | Roll up task→phase→project status |

### Recommended Approaches

1. **PROGRESS.md as State Machine**
   - Single source of truth for implementation state
   - Contains: current phase, task status map, divergence notes, session log
   - Updated atomically on each significant action

2. **Frontmatter as Derived State**
   - PROGRESS.md is authoritative
   - README.md frontmatter is derived/synced from PROGRESS.md
   - Prevents split-brain state issues

3. **Hierarchical Rollup**
   ```
   Task completed → Phase progress updated → Project status derived
   All tasks in phase done → Phase marked complete
   All phases done → Project status → completed
   ```

4. **Divergence as First-Class Concept**
   - Track planned vs actual explicitly
   - Allow dynamic task addition/removal
   - Flag for user review but don't block

### Anti-Patterns to Avoid

1. **Scattered State**: Don't track progress in multiple places that can desync
2. **Implicit Completion**: Always require explicit confirmation before marking done
3. **Lost Context**: Don't rely solely on in-memory state; persist to file
4. **Brittle Parsing**: Use structured formats (YAML/JSON) not regex on markdown

## Existing Document Templates Analysis

### Documents That Need State Updates

| Document | State Fields | Update Triggers |
|----------|-------------|-----------------|
| `README.md` | `status`, `started`, `completed`, dates | Phase transitions, project milestones |
| `REQUIREMENTS.md` | Acceptance criteria checkboxes | When criteria verified during implementation |
| `IMPLEMENTATION_PLAN.md` | Task checkboxes, phase deliverables | Each task completion |
| `CHANGELOG.md` | Version entries | Any significant state change |
| `DECISIONS.md` | ADR status (Proposed→Accepted) | When decisions are validated |

### Proposed New Document

**`PROGRESS.md`** - Implementation checkpoint file

```markdown
---
document_type: progress
project_id: ARCH-2025-12-12-001
last_session: 2025-12-12T20:00:00Z
implementation_started: 2025-12-12T19:00:00Z
---

# Implementation Progress

## Current State
- **Phase**: 2 of 4
- **Status**: in-progress
- **Last Action**: Completed Task 2.1

## Task Status
| Task ID | Description | Status | Completed At |
|---------|-------------|--------|--------------|
| 1.1 | Setup foundation | done | 2025-12-12T19:15:00Z |
| 1.2 | Configure base | done | 2025-12-12T19:30:00Z |
| 2.1 | Implement core | done | 2025-12-12T20:00:00Z |
| 2.2 | Add validation | in-progress | - |
| 2.3 | Write tests | pending | - |

## Divergence Log
| Date | Type | Description | Resolution |
|------|------|-------------|------------|
| 2025-12-12 | added | New task 2.4 for edge case | Approved |
| 2025-12-12 | skipped | Task 1.3 not needed | Flagged for review |

## Session Notes
### Session 2025-12-12T19:00:00Z
- Started implementation
- Completed Phase 1
- Began Phase 2
```

## Competitive Analysis

### Similar Solutions

| Solution | Approach | Strengths | Weaknesses |
|----------|----------|-----------|------------|
| GitHub Projects | Kanban + automation | Visual, integrated with PRs | External to codebase |
| Linear | Issue tracking | Great UX, automation rules | External service |
| Markdown task lists | Native in repo | Simple, version controlled | No automation |
| Org-mode (Emacs) | Hierarchical outliner | Powerful state tracking | Editor-specific |

### Lessons Learned

1. **State should live in the repo**: External tools lose context; in-repo tracking enables Claude to see and update
2. **Automation reduces friction**: Manual checkbox updating is tedious and error-prone
3. **Hierarchical views matter**: Both detailed task view and high-level status needed
4. **Session continuity is critical**: Implementation spans multiple sessions; must not lose progress

## Open Questions Resolved

- [x] How to detect project from branch? → Parse branch name, match against `docs/architecture/active/*/README.md` slugs
- [x] Where to store implementation state? → New `PROGRESS.md` checkpoint file
- [x] How granular should tracking be? → Hierarchical: task → phase → project
- [x] How to handle plan divergence? → Track in Divergence Log, flag for user, allow dynamic updates

## Sources

- Codebase exploration via `/explore commands/arch/` (2025-12-12)
- Direct file reads of `p.md`, `s.md`, `c.md`, `SKILL.md`, `launch-agent.sh`
- User requirements elicitation session (this planning session)
