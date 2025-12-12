---
document_type: decisions
project_id: ARCH-2025-12-12-002
---

# Claude Spec Plugin - Architecture Decision Records

## ADR-001: Custom Prompt Capture vs Claude Code Native Logs

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

Claude Code may maintain internal session transcripts. The question was whether we could leverage those instead of maintaining a custom prompt capture system.

### Investigation Findings

1. **No guaranteed local transcript access**: Claude Code retains data server-side, not locally
2. **`transcript_path` hook parameter exists but is undocumented** - internal implementation detail, subject to change
3. **Retention policies**: Max 30 days (commercial), not suitable for project archives
4. **No content filtering**: Claude Code doesn't filter secrets before storage

### Decision

Maintain **custom prompt capture system** within the plugin.

### Consequences

**Positive:**
- Full control over log format and location
- Content filtering (secrets, profanity) before storage
- Project-local logs that persist with codebase
- Not dependent on undocumented Claude Code internals

**Negative:**
- More code to maintain
- Duplicate logging (ours + Claude's internal)

**Neutral:**
- Aligns with original design from ARCH-2025-12-12-001

---

## ADR-002: Command Prefix Rename (/arch:* → /cs:*)

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User

### Context

The plugin needs a command prefix. Options were `/arch:*`, `/spec:*`, `/cs:*`, or `/cspec:*`.

### Decision

Use **`/cs:*`** prefix (short for claude-spec).

### Consequences

**Positive:**
- Short, easy to type
- Matches plugin name `claude-spec`
- Distinct from any other Claude Code commands

**Negative:**
- Requires migration from `/arch:*`
- Less descriptive than full words

---

## ADR-003: No Legacy Aliases

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User

### Context

During migration, we could provide `/arch:*` aliases that redirect to `/cs:*` commands.

### Decision

**No aliases** - clean break from old commands.

### Consequences

**Positive:**
- Simpler codebase
- No ambiguity about which commands are current
- Forces complete migration

**Negative:**
- Existing workflows break immediately
- Muscle memory adjustment required

**Mitigation:**
- `/cs:migrate` command updates CLAUDE.md references

---

## ADR-004: Project Directory Rename

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User

### Context

Projects were stored in `docs/architecture/active/`. With the rename, options were:
- Keep old location (backward compatible)
- Rename to `docs/spec/active/` (consistent branding)
- Use hidden `.claude-spec/` directory

### Decision

Rename to **`docs/spec/active/`** with one-time migration via `/cs:migrate`.

### Consequences

**Positive:**
- Consistent with `claude-spec` branding
- Cleaner naming
- `docs/spec/completed/` for archives

**Negative:**
- Requires explicit migration step
- Git history shows file moves (not deletes)

---

## ADR-005: Worktree Commands Structure

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User

### Context

Worktree manager functionality could be exposed as:
- Skill triggers only ("spin up worktrees")
- Explicit commands (`/cs:wt:*`)
- Both

### Decision

**Both** - skill triggers AND explicit commands.

Commands:
- `/cs:wt:create` - Create worktrees with agents
- `/cs:wt:status` - View worktree status
- `/cs:wt:cleanup` - Clean up worktrees

### Consequences

**Positive:**
- Flexibility for different user preferences
- Discoverability via `/help`
- Natural language still works

**Negative:**
- More commands to maintain
- Potential duplicate code paths

---

## ADR-006: Hidden Prompt Log File

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User

### Context

Prompt log file naming options:
- `PROMPT_LOG.json` (visible, all caps)
- `prompts.json` (visible, lowercase)
- `.prompt-log.json` (hidden)

### Decision

Use **`.prompt-log.json`** (hidden file).

### Consequences

**Positive:**
- Less clutter in project directory listings
- Clearly auxiliary/generated file
- Won't appear in most file explorers by default

**Negative:**
- Could be missed during manual inspection
- Need to use `ls -a` to see it

---

## ADR-007: Dynamic Agent Catalog Integration

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User

### Context

Plugin needs to reference specialist agents. Options:
- Bundle agent definitions in plugin
- Assume host has agents, document as prerequisite
- Dynamically read from host's `~/.claude/agents/`

### Decision

**Dynamically read from host's `~/.claude/agents/`** and CLAUDE.md.

### Consequences

**Positive:**
- No duplication of agent definitions
- Plugin stays smaller
- Host can customize agents
- Automatic access to any new agents

**Negative:**
- Plugin depends on host configuration
- Behavior varies based on host setup

**Mitigation:**
- Document required host configuration in README
- Graceful degradation if agents not found
