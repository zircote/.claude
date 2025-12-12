---
document_type: decisions
project_id: ARCH-2025-12-12-002
---

# Prompt Capture Log - Architecture Decision Records

## ADR-001: Use NDJSON for Log Format

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

The log file needs to store multiple entries over time, potentially across many sessions. We need a format that supports:
- Atomic appends without reading/rewriting the entire file
- Resistance to corruption (one bad entry shouldn't invalidate all data)
- Easy parsing for analysis
- Human readability for debugging

### Decision

Use NDJSON (Newline-Delimited JSON) format where each line is a self-contained JSON object.

### Consequences

**Positive:**
- Atomic append: Just write a line, no file rewrite needed
- Corruption-resistant: Bad line can be skipped, rest remains valid
- Streaming-friendly: Can process line by line without loading full file
- Standard format: Supported by many tools (jq, Pino, Bunyan)

**Negative:**
- No schema validation at file level
- Slightly larger than compact JSON array
- Requires line-by-line parsing

**Neutral:**
- Will need custom parsing logic for analysis

### Alternatives Considered

1. **JSON Array**: Simpler schema, but requires full file rewrite on each append
2. **SQLite**: Robust, but overkill for simple logging; adds dependency
3. **Plain text**: Simplest, but loses structure; harder to parse reliably

---

## ADR-002: Python for Hook Implementation

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

The hook needs to integrate with Claude Code's hook system, which supports command execution. The existing hookify plugin is written in Python.

### Decision

Implement the prompt capture hook in Python to match the existing hookify plugin infrastructure.

### Consequences

**Positive:**
- Consistent with existing codebase
- No additional runtime dependencies
- Can reuse hookify infrastructure patterns
- Cross-platform compatibility

**Negative:**
- Python startup time adds latency (~50ms)
- Type hints help but aren't enforced at runtime

**Neutral:**
- Will need to manage Python path and imports

### Alternatives Considered

1. **Node.js/TypeScript**: Better type safety, but adds runtime dependency
2. **Bash script**: Simpler, but regex and JSON handling would be fragile
3. **Go binary**: Fast, but requires compilation; overkill for this use case

---

## ADR-003: File-Based Toggle Marker

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

Need a way to persist the "logging enabled" state across Claude Code sessions. The toggle must be:
- Project-specific (different projects can have different states)
- Visible and debuggable
- Persistent without a database

### Decision

Use a marker file (`.prompt-log-enabled`) in the project directory. Presence = enabled, absence = disabled.

### Consequences

**Positive:**
- Simple: just check file existence
- Visible: `ls -la` shows the state
- Project-scoped: naturally tied to project directory
- No database or config file parsing needed

**Negative:**
- Empty file feels like a hack
- Could be accidentally deleted
- Won't work outside project directories

**Neutral:**
- Could extend to JSON file with metadata if needed later

### Alternatives Considered

1. **JSON config file**: More structured, but overkill for boolean state
2. **Environment variable**: Not persistent across sessions
3. **Global settings.json**: Wouldn't be project-scoped
4. **Database**: Way overkill; adds complexity

---

## ADR-004: Filter Pipeline Order (Secrets → Profanity)

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

Both profanity and secrets need to be filtered. The order of filtering could affect results.

### Decision

Filter secrets first, then profanity.

### Consequences

**Positive:**
- Secrets are more security-critical; handle them first
- Avoids edge case where secret contains profanity word (secret would be masked as profanity, but partial secret might remain)

**Negative:**
- None significant

**Neutral:**
- Order is documented for future maintainers

### Alternatives Considered

1. **Profanity → Secrets**: Could miss secrets that partially match profanity patterns
2. **Single pass**: More complex, harder to maintain separate concerns

---

## ADR-005: Response Summaries via Heuristics

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

Need to capture Claude's responses for complete interaction logging, but full responses are too verbose (often 1000+ words). Options for summarization:
- Use LLM to summarize (adds latency, cost)
- Use heuristics (fast, free, less accurate)

### Decision

Use heuristic-based summarization: extract first paragraph, key bullet points, truncate to 500 characters.

### Consequences

**Positive:**
- Zero latency (no API calls)
- Zero cost
- Deterministic and predictable
- Good enough for retrospective analysis

**Negative:**
- May miss important details
- Not as accurate as LLM summarization
- Fixed logic may not adapt to different response styles

**Neutral:**
- Can upgrade to LLM summarization later if needed

### Alternatives Considered

1. **LLM summarization**: Better quality, but adds latency and cost for every prompt
2. **Full response logging**: Complete, but logs would be huge
3. **No response capture**: Loses half the interaction context

---

## ADR-006: Hook Integration Point

**Date**: 2025-12-12
**Status**: Accepted
**Deciders**: User, Claude

### Context

Need to choose how to integrate with Claude Code's hook system. Options:
- Standalone hook in `~/.claude/hooks/`
- Extension to hookify plugin
- New dedicated plugin

### Decision

Implement as a standalone hook in `~/.claude/hooks/` with its own registration, separate from but compatible with hookify.

### Consequences

**Positive:**
- Clear separation of concerns
- Can work even if hookify is disabled
- Easier to maintain independently
- Simpler mental model

**Negative:**
- Some code duplication with hookify patterns
- Two UserPromptSubmit hooks will fire

**Neutral:**
- Both approaches would work; this is slightly cleaner

### Alternatives Considered

1. **Extend hookify**: Tighter integration, but couples to hookify development
2. **New plugin**: More structure, but overkill for a single hook
