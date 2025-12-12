---
document_type: decisions
project_id: ARCH-2025-12-12-001
---

# Architecture Lifecycle Automation - Architecture Decision Records

## ADR-001: Use PROGRESS.md as Single Source of Truth

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User + Claude (planning session)

### Context

Implementation state needs to be tracked across multiple documents (README.md, IMPLEMENTATION_PLAN.md, REQUIREMENTS.md, CHANGELOG.md). We need to decide where the authoritative state lives.

Options considered:
1. Distributed state: Each document owns its own state
2. Central state: One file is authoritative, others are derived
3. External state: JSON/database file separate from markdown

### Decision

Use a new `PROGRESS.md` file as the single source of truth for all implementation state. Other documents are synchronized from PROGRESS.md.

### Consequences

**Positive:**
- No split-brain scenarios where documents disagree
- Clear reconciliation path if desync occurs
- Human-readable checkpoint that doubles as audit trail
- Version controlled with the project

**Negative:**
- Another file to maintain
- Sync logic adds complexity
- Must parse PROGRESS.md on every update

**Neutral:**
- Users can manually edit PROGRESS.md if needed (may cause desync, handled by reconciliation)

### Alternatives Considered

1. **Distributed state**: Rejected because coordinating updates across 4+ files is error-prone; state can diverge.
2. **JSON/database file**: Rejected because not human-readable; violates spirit of markdown-based planning.

---

## ADR-002: Hybrid Checkpoint System for Context Loading

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User + Claude (planning session)

### Context

When `/arch:i` starts, it needs to provide Claude with implementation context. We need to decide how much to load and how.

Options considered:
1. Full document load (all planning docs into context)
2. Condensed brief (summary only)
3. Progressive loading (current phase detail + overview)
4. Reference mode (lazy loading on demand)
5. Hybrid checkpoint (brief + persistent PROGRESS.md)

### Decision

Use Hybrid Checkpoint System: Load a condensed implementation brief at startup, maintain state in PROGRESS.md that persists across sessions.

### Consequences

**Positive:**
- Efficient context usage (~5-15K tokens vs ~50-100K)
- State persists across Claude sessions
- Full audit trail in PROGRESS.md
- Natural place to track divergences

**Negative:**
- Another file format to maintain
- Sync complexity between PROGRESS.md and other docs
- Users may edit PROGRESS.md causing inconsistency

**Neutral:**
- PROGRESS.md becomes a key artifact alongside existing planning docs

### Alternatives Considered

1. **Full document load**: Rejected due to context bloat and slow startup.
2. **Condensed brief only**: Rejected because no session persistence.
3. **Progressive loading**: Rejected as overly complex for initial implementation.
4. **Reference mode**: Rejected due to too many tool calls and lost big-picture context.

---

## ADR-003: Auto-Detect Project from Branch Name

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User + Claude (planning session)

### Context

When user runs `/arch:i`, we need to determine which architecture project to work on. Options:

1. Always require explicit project ID argument
2. Auto-detect from current git branch
3. Interactive selection from active projects
4. Combination with fallback chain

### Decision

Auto-detect project from current git branch name, with explicit argument as override and interactive selection as fallback for ambiguous cases.

Detection logic:
1. If explicit argument provided, use it
2. Parse current branch name (e.g., `fix/arch-commands` → `arch-commands`)
3. Search `docs/architecture/active/*/README.md` for matching slug
4. If multiple matches, prompt user to select
5. If no matches, provide helpful error

### Consequences

**Positive:**
- Seamless workflow when branch naming follows convention
- No argument needed in common case
- Still flexible with explicit override

**Negative:**
- Relies on branch naming convention
- May fail for creative branch names

**Neutral:**
- Users learn to name branches meaningfully (good practice anyway)

### Alternatives Considered

1. **Always require argument**: Rejected as friction in the common case.
2. **Interactive selection only**: Rejected as unnecessary when branch name is clear.

---

## ADR-004: Hierarchical Status Rollup

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User + Claude (planning session)

### Context

We need to determine project and phase status from granular task states. How should rollup work?

Options:
1. Per-task only (no aggregation)
2. Per-phase only
3. Per-deliverable
4. Hierarchical (task → phase → project)

### Decision

Use hierarchical rollup: Task completion rolls up to phase progress, phase completion rolls up to project status.

Rollup rules:
- Phase progress = (done + skipped) / total tasks
- Phase status: pending → in-progress (first task starts) → done (all tasks done/skipped)
- Project status: draft → in-progress (first task starts) → completed (all phases done)

### Consequences

**Positive:**
- Accurate aggregate status at every level
- User sees meaningful progress indicators
- Handles skipped tasks gracefully

**Negative:**
- More complex calculation logic
- Need to track all three levels

**Neutral:**
- Skipped tasks count toward progress (intentional: plan said N tasks, we completed/decided-to-skip all N)

### Alternatives Considered

1. **Per-task only**: Rejected as too granular; no high-level view.
2. **Per-phase only**: Rejected as loses task-level detail.
3. **Per-deliverable**: Rejected as overly complex; deliverables not always clearly mapped to tasks.

---

## ADR-005: Divergence Tracking with User Notification

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User + Claude (planning session)

### Context

Implementation often diverges from plans: tasks get added, skipped, or modified. How should we handle this?

Options:
1. Silently update the plan
2. Block divergence (force adherence to plan)
3. Track and flag for user review
4. Track and auto-approve
5. Track, flag, and allow user to approve/reject

### Decision

Track divergences in PROGRESS.md Divergence Log, notify user, and allow them to approve or flag for review. Divergences don't block progress but are explicitly recorded.

Divergence types: `added`, `skipped`, `modified`, `reordered`
Resolution states: `approved`, `flagged`, `pending-review`

### Consequences

**Positive:**
- Plans can evolve with reality
- Full audit trail of what changed
- User stays informed and in control
- Doesn't block implementation flow

**Negative:**
- User may get notification fatigue
- Divergence log can grow large

**Neutral:**
- Requires user judgment on whether divergences are acceptable

### Alternatives Considered

1. **Silent updates**: Rejected because plan loses historical accuracy.
2. **Block divergence**: Rejected as impractical; plans never survive contact with reality.
3. **Track and auto-approve**: Rejected because removes user oversight.

---

## ADR-006: Use Opus 4.5 Model for `/arch:i`

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User + Claude (planning session)

### Context

The existing `/arch` commands use a model tiering strategy:
- `/arch:p` (planning): Opus 4.5 (complex reasoning)
- `/arch:s` (status): Sonnet (simpler operations)
- `/arch:c` (close): Sonnet (simpler operations)

What model should `/arch:i` use?

### Decision

Use Opus 4.5 for `/arch:i` because it requires:
- Intelligent detection of task completion from implementation work
- Context synthesis across multiple planning documents
- Nuanced divergence detection and user communication
- Complex state management and rollup calculations

### Consequences

**Positive:**
- Accurate task completion detection
- Better handling of ambiguous situations
- Consistent with `/arch:p` complexity

**Negative:**
- Higher cost per interaction
- Potentially slower responses

**Neutral:**
- Aligns with existing tiering strategy (complex tasks get Opus)

### Alternatives Considered

1. **Sonnet**: Rejected because task completion detection requires higher reasoning.
2. **Hybrid (Sonnet + escalate to Opus)**: Rejected as overly complex for initial implementation.
