---
document_type: decisions
project_id: ARCH-2025-12-12-001
---

# Parallel Agent Directives - Architecture Decision Records

## ADR-001: Prompt Engineering vs Code Changes

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

We need to enforce parallel specialist agent usage across `/arch:*` commands. This could be implemented via:
1. Code changes to Claude Code runtime
2. Prompt engineering in command markdown files
3. Custom hooks or middleware

### Decision

Implement via **prompt engineering only** - modifications to the markdown command files.

### Consequences

**Positive:**
- No code changes required
- Changes take effect immediately
- Easy to iterate and refine
- Leverages existing Task tool API

**Negative:**
- Enforcement is "soft" - Claude could theoretically ignore directives
- Must use persuasive language rather than hard constraints

**Neutral:**
- Aligns with existing `/arch:*` architecture

### Alternatives Considered

1. **Runtime enforcement**: Rejected - would require Claude Code source modifications
2. **Custom hooks**: Rejected - hooks run after tool calls, can't enforce before

---

## ADR-002: Agent Assignment Granularity

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

Agent assignments could be specified at:
- Phase level only (coarse)
- Task level only (granular)
- Both levels (flexible)

### Decision

Implement **both phase-level and task-level** agent assignments.

### Consequences

**Positive:**
- Phase level provides overview (Lead Agent, Parallel Agents)
- Task level provides precision for execution
- Flexibility for different project sizes

**Negative:**
- More fields to populate in templates
- Potential inconsistency between levels

**Neutral:**
- Mirrors existing project management patterns (team lead + individual contributors)

### Alternatives Considered

1. **Phase only**: Rejected - insufficient for execution guidance
2. **Task only**: Rejected - loses high-level visibility

---

## ADR-003: Parallel Group Notation

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

Need a way to indicate which tasks can run in parallel vs must be sequential.

### Decision

Use **Parallel Group** field with notation:
- `PG-N` for tasks that run together
- `Sequential` for tasks with dependencies
- `independent` for tasks that can run anytime

### Consequences

**Positive:**
- Clear visual grouping
- Explicit dependency management
- Easy to understand in tables

**Negative:**
- Another field to maintain
- Group assignments require thought

**Neutral:**
- Similar to thread pool / batch processing patterns

### Alternatives Considered

1. **Dependency graph only**: Rejected - harder to parse visually
2. **No explicit notation**: Rejected - leaves parallelization to discretion

---

## ADR-004: Document Synchronization Enforcement

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

Document synchronization (updating checkboxes, status fields) is specified in `/arch:i` but not being executed. Need to fix this.

### Decision

Add explicit **`<sync_enforcement>`** directive block to `/arch:i` with mandatory sync points.

### Consequences

**Positive:**
- Clear trigger points for synchronization
- Explicit field updates specified
- Cannot be missed if following the directive

**Negative:**
- More directive text in prompt
- Synchronization adds steps to task completion

**Neutral:**
- Aligns with existing Phase 5 design - just makes it mandatory

### Alternatives Considered

1. **Automated sync hooks**: Rejected - can't modify hook behavior
2. **Post-session batch sync**: Rejected - creates drift between documents

---

## ADR-005: Worktree Initialization Sequence

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

Prompt logging infrastructure must exist when Claude Code starts in a new worktree. Currently it's created after launch, causing hooks to fail.

### Decision

Modify worktree creation sequence to **create logging infrastructure BEFORE launching Claude Code**.

### Consequences

**Positive:**
- Hooks find marker file immediately
- Logging works from first prompt
- No missed prompts

**Negative:**
- More bash commands in worktree creation
- Project directory created before user confirms project name

**Neutral:**
- Aligns with "initialize before run" pattern

### Alternatives Considered

1. **Hooks check/create files**: Rejected - hooks run in response to events, not proactively
2. **Retry logic in hooks**: Rejected - complexity for a simple sequencing fix

---

## ADR-006: Prompt Capture Implementation Strategy

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

The prompt capture hook was registered in hookify's `hooks.json` but never executed during Claude Code sessions. Investigation revealed:
1. The hook was in a separate group entry within the `UserPromptSubmit` array
2. Consolidating hooks into a single array still didn't trigger execution
3. Patching hookify creates maintenance burden and unclear behavior

### Decision

Create a **standalone prompt-capture plugin** instead of patching hookify.

### Consequences

**Positive:**
- Clean separation of concerns - prompt capture is its own plugin
- No patch management when hookify updates
- Can be enabled/disabled independently via `/plugin` commands
- Hook registration follows standard plugin patterns
- Easier to debug and maintain

**Negative:**
- Requires creating a new plugin (additional work)
- Two plugins handling UserPromptSubmit event (hookify + prompt-capture)

**Neutral:**
- Same underlying hook mechanism, different registration approach

### Alternatives Considered

1. **Multiple group entries in hookify**: Original state - only first group executed
2. **Consolidated single array in hookify**: Attempted - still didn't work
3. **Hook consolidation in hookify**: Rejected - patch management fragile

### Implementation Notes

New plugin structure:
```
~/.claude/plugins/prompt-capture/
├── plugin.json           # Plugin manifest with UserPromptSubmit hook
├── prompt_capture.py     # Move from ~/.claude/hooks/prompt_capture_hook.py
└── README.md             # Usage documentation
```

Revert hookify patches after plugin is working.
