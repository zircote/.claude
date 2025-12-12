---
document_type: architecture
project_id: ARCH-2025-12-12-001
version: 1.0.0
last_updated: 2025-12-12T20:00:00Z
status: in-review
---

# Architecture Lifecycle Automation - Technical Architecture

## System Overview

This enhancement introduces `/arch:i` (implement), a new command in the `/arch` suite that activates implementation mode with intelligent state tracking. The architecture follows a **checkpoint-centric** design where `PROGRESS.md` serves as the single source of truth for implementation state, with all other documents deriving their state from it.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            /arch COMMAND SUITE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │ /arch:p  │    │ /arch:i  │    │ /arch:s  │    │ /arch:c  │             │
│  │  (Plan)  │───►│(Implement)│───►│ (Status) │───►│ (Close)  │             │
│  │  Opus    │    │   Opus   │    │  Sonnet  │    │  Sonnet  │             │
│  └──────────┘    └────┬─────┘    └──────────┘    └──────────┘             │
│                       │                                                     │
│                       ▼                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    PROGRESS.md (Source of Truth)                     │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │  │
│  │  │ Task Status │  │ Phase State │  │ Divergence  │                  │  │
│  │  │    Map      │  │   Tracker   │  │    Log      │                  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                       │                                                     │
│                       ▼ (Sync)                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    State-Bearing Documents                           │  │
│  │  ┌───────────┐ ┌────────────────┐ ┌──────────────┐ ┌────────────┐  │  │
│  │  │ README.md │ │IMPLEMENTATION_ │ │REQUIREMENTS  │ │ CHANGELOG  │  │  │
│  │  │frontmatter│ │   PLAN.md      │ │    .md       │ │    .md     │  │  │
│  │  │  status   │ │  checkboxes    │ │ checkboxes   │ │  entries   │  │  │
│  │  └───────────┘ └────────────────┘ └──────────────┘ └────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **PROGRESS.md as Single Source of Truth**: All state lives in one file; other documents are synchronized from it. Prevents split-brain scenarios.

2. **Hierarchical State Model**: Task → Phase → Project rollup ensures consistent aggregate status.

3. **Checkpoint-based Session Recovery**: PROGRESS.md persists across Claude sessions, enabling seamless resume.

4. **Divergence as First-Class Concept**: Plan changes are tracked explicitly rather than silently overwriting.

## Component Design

### Component 1: `/arch:i` Command (`commands/arch/i.md`)

- **Purpose**: Entry point for implementation mode; orchestrates all state management
- **Responsibilities**:
  - Auto-detect project from current branch
  - Initialize or load PROGRESS.md
  - Provide implementation context to Claude
  - Coordinate document updates
- **Interfaces**:
  - Input: Optional project ID/path argument
  - Output: Implementation mode activated with context summary
- **Dependencies**: Git (branch detection), file system, existing planning documents
- **Technology**: Claude Code slash command (Markdown with YAML frontmatter)

### Component 2: PROGRESS.md Checkpoint File

- **Purpose**: Persist implementation state across sessions
- **Responsibilities**:
  - Track individual task status with timestamps
  - Maintain phase completion state
  - Log divergences (added/skipped/modified tasks)
  - Store session notes for context
- **Interfaces**:
  - Read: On `/arch:i` startup
  - Write: On every state change
- **Dependencies**: None (standalone file)
- **Technology**: Markdown with YAML frontmatter + structured tables

### Component 3: State Synchronization Engine

- **Purpose**: Keep all documents consistent with PROGRESS.md
- **Responsibilities**:
  - Update IMPLEMENTATION_PLAN.md checkboxes
  - Update README.md frontmatter
  - Update REQUIREMENTS.md acceptance criteria
  - Append CHANGELOG.md entries
- **Interfaces**: Called after any state change in PROGRESS.md
- **Dependencies**: PROGRESS.md, target documents
- **Technology**: Claude's Edit tool with targeted updates

### Component 4: Project Detection Logic

- **Purpose**: Match current branch to architecture project
- **Responsibilities**:
  - Parse current branch name
  - Search `docs/architecture/active/` for matching project
  - Handle ambiguous matches (prompt user)
  - Handle no matches (error with guidance)
- **Interfaces**: Returns project path or prompts for selection
- **Dependencies**: Git, file system
- **Technology**: Bash commands + directory scanning

### Component 5: Hierarchical Status Calculator

- **Purpose**: Derive aggregate status from granular task state
- **Responsibilities**:
  - Calculate phase completion percentage
  - Determine when phase transitions to "complete"
  - Determine when project transitions to "completed"
  - Handle edge cases (skipped tasks, added tasks)
- **Interfaces**: Takes task status map, returns phase/project status
- **Dependencies**: PROGRESS.md task status
- **Technology**: Logic within `/arch:i` command

## Data Design

### PROGRESS.md Schema

```yaml
---
document_type: progress
project_id: ARCH-2025-12-12-001
format_version: 1.0.0
implementation_started: 2025-12-12T19:00:00Z
last_session: 2025-12-12T20:00:00Z
current_phase: 2
project_status: in-progress
---
```

**Task Status Table**:
```markdown
## Task Status

| Task ID | Description | Status | Started | Completed | Notes |
|---------|-------------|--------|---------|-----------|-------|
| 1.1 | [Description] | done | [ISO8601] | [ISO8601] | [Optional] |
| 1.2 | [Description] | done | [ISO8601] | [ISO8601] | |
| 2.1 | [Description] | in-progress | [ISO8601] | - | |
| 2.2 | [Description] | pending | - | - | |
```

**Status Values**: `pending`, `in-progress`, `done`, `skipped`

**Phase Status Table**:
```markdown
## Phase Status

| Phase | Name | Status | Progress | Completed |
|-------|------|--------|----------|-----------|
| 1 | Foundation | done | 100% | 2025-12-12T19:30:00Z |
| 2 | Core Implementation | in-progress | 50% | - |
| 3 | Integration | pending | 0% | - |
| 4 | Polish | pending | 0% | - |
```

**Divergence Log**:
```markdown
## Divergence Log

| Date | Type | Task ID | Description | Resolution |
|------|------|---------|-------------|------------|
| 2025-12-12 | added | 2.4 | Edge case handling | approved |
| 2025-12-12 | skipped | 1.3 | Not needed for MVP | flagged |
| 2025-12-12 | modified | 2.1 | Scope expanded | approved |
```

**Divergence Types**: `added`, `skipped`, `modified`, `reordered`
**Resolution Values**: `approved`, `flagged`, `pending-review`

### Data Flow

```
┌─────────────────┐
│  User Action    │ "Task 2.1 is complete"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  /arch:i Logic  │ Interprets completion
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Update         │ 1. Task 2.1 → done in PROGRESS.md
│  PROGRESS.md    │ 2. Phase 2 progress recalculated
└────────┬────────┘ 3. Timestamps updated
         │
         ▼
┌─────────────────┐
│  Sync Engine    │ Triggered by PROGRESS.md change
└────────┬────────┘
         │
         ├──► IMPLEMENTATION_PLAN.md: Task 2.1 checkbox checked
         ├──► README.md: last_updated timestamp
         ├──► CHANGELOG.md: Entry appended (if phase complete)
         └──► REQUIREMENTS.md: Related criteria checked (if applicable)
```

### Storage Strategy

- **Primary Store**: PROGRESS.md (human-readable Markdown with YAML)
- **Derived State**: Other document checkboxes/frontmatter
- **No External Database**: All state in version-controlled files

## API Design

### `/arch:i` Command Interface

**Invocation**:
```
/arch:i                          # Auto-detect project from branch
/arch:i ARCH-2025-12-12-001      # Explicit project ID
/arch:i arch-lifecycle-automation # Explicit project slug
```

**Startup Behavior**:
1. Detect/validate project
2. Load or create PROGRESS.md
3. Display implementation brief
4. Enter implementation mode (ready for task work)

**Implementation Mode Behaviors**:
- When Claude completes a task: Auto-update PROGRESS.md + sync documents
- When user says "skip task X": Log divergence + update status
- When user says "add task Y": Create divergence entry + add to tracking
- When phase completes: Transition phase status + CHANGELOG entry
- When project completes: Transition to completed + prompt for `/arch:c`

## Integration Points

### Internal Integrations

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| `/arch:p` | Document format | Parse IMPLEMENTATION_PLAN.md structure |
| `/arch:s` | Status display | Could show PROGRESS.md data in future |
| `/arch:c` | Handoff | When project complete, smooth transition to close-out |
| worktree-manager | Context | Branch-based project detection |

### External Integrations

None required. Future consideration: GitHub PR status sync.

## Security Design

### Data Protection

- All files stored in local repository (no cloud sync by this feature)
- No secrets or credentials involved
- User-controlled: all state changes visible in git diff

### Access Control

- Inherits repository permissions
- No additional authentication required

## Performance Considerations

### Expected Load

- Single user, single project at a time
- ~10-50 tasks per project typical
- ~4 phases per project typical
- ~5-20 document updates per session

### Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| `/arch:i` startup | < 5 seconds | User experience; quick context load |
| Task completion update | < 2 seconds | Responsive feedback |
| Document sync | < 3 seconds | All documents updated promptly |
| PROGRESS.md size | < 50 KB | Avoid context bloat |

### Optimization Strategies

1. **Lazy document reading**: Only read documents when sync needed
2. **Targeted edits**: Use Edit tool for surgical updates, not full rewrites
3. **Batch updates**: Group related changes when possible
4. **Progressive loading**: Load current phase detail, summary of others

## Reliability & Operations

### Availability Target

Not applicable (local CLI tool, not a service)

### Failure Modes

| Failure | Impact | Recovery |
|---------|--------|----------|
| PROGRESS.md corrupted | Lost state | Rebuild from document checkboxes |
| Document edit fails | Single doc desync | Re-run sync manually |
| Branch detection fails | Can't find project | Manual project selection |
| Claude session crash | Progress since last save lost | PROGRESS.md has last-saved state |

### Backup & Recovery

- Git provides versioning for all files
- PROGRESS.md can be rebuilt by scanning document checkboxes
- Session notes may be lost on crash (acceptable)

## Testing Strategy

### Unit Testing

- Task status transition logic
- Phase completion calculation
- Divergence type classification
- Branch-to-project matching

### Integration Testing

- PROGRESS.md → IMPLEMENTATION_PLAN.md sync
- Full lifecycle: start → task completion → phase transition → project completion
- Multi-session resume (create state, new session, verify resume)

### Edge Cases to Test

- No matching project for branch
- Multiple matching projects
- All tasks skipped in a phase
- Task added mid-phase
- Manual checkbox edit causing desync
- Very large project (100+ tasks)

## Deployment Considerations

### Installation

1. Add `commands/arch/i.md` to user's `.claude/commands/arch/` directory
2. No additional configuration required
3. Works immediately with existing `/arch:p` projects

### Configuration Management

- Inherits from existing `/arch` command patterns
- No new configuration files needed
- PROGRESS.md format versioned in frontmatter

### Rollout Strategy

1. Create `/arch:i` command
2. Test with sample project
3. Document in CLAUDE.md
4. User adoption

### Rollback Plan

- Remove `commands/arch/i.md` file
- PROGRESS.md files remain but are inert
- Other `/arch` commands unaffected

## Future Considerations

1. **`/arch:s` integration**: Show PROGRESS.md data in status view
2. **GitHub PR sync**: Update PR description with implementation progress
3. **Time tracking**: Capture actual effort vs estimated
4. **Multi-project dashboards**: Aggregate progress across projects
5. **Undo capability**: Revert task completion (currently: manual edit)
