---
document_type: research
project_id: ARCH-2025-12-12-002
last_updated: 2025-12-12T22:30:00Z
---

# Prompt Capture Log - Research Notes

## Research Summary

Research covered three areas: (1) Claude Code hook mechanisms for prompt capture, (2) content filtering approaches for profanity and secrets, and (3) best practices for JSON logging in CLI tools. Key finding: the existing hookify plugin provides a solid foundation, and the UserPromptSubmit hook receives all necessary data including session_id, transcript_path, and user_prompt.

## Codebase Analysis

### Relevant Files Examined

| File | Purpose | Relevance |
|------|---------|-----------|
| `~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/hooks/userpromptsubmit.py` | UserPromptSubmit hook handler | Primary integration point |
| `~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/core/rule_engine.py` | Rule evaluation engine | Pattern for hook processing |
| `~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/core/config_loader.py` | Loads rules from .md files | Model for config handling |
| `~/.claude/commands/arch/p.md` | /arch:p command definition | Template expansion source |
| `~/.claude/commands/arch/c.md` | /arch:c close-out command | Integration point for analysis |

### Existing Patterns Identified

1. **Hook input structure**: JSON via stdin with `user_prompt`, `session_id`, `cwd`, `transcript_path`
2. **Hook output structure**: JSON via stdout with `decision`, `systemMessage`, `additionalContext`
3. **Rule file pattern**: Markdown files with YAML frontmatter in `.claude/` directory
4. **Project structure**: `docs/architecture/active/[date]-[slug]/` with standardized files

### Integration Points

- **UserPromptSubmit hook**: Entry point for capturing prompts
- **transcript_path**: Access to full session transcript for response capture
- **cwd**: Determines active project directory for log placement
- **/arch:c command**: Trigger for log analysis and retrospective generation

## Technical Research

### Best Practices Found

| Topic | Source | Key Insight |
|-------|--------|-------------|
| NDJSON logging | Pino, Bunyan documentation | Atomic appends, corruption resistance |
| Secret detection | gitleaks project | Well-tested regex patterns, 90+ secret types |
| Profanity filtering | @2toad/profanity | Word boundary matching prevents false positives |
| File locking | Python fcntl docs | LOCK_EX for exclusive writes |

### Recommended Approaches

1. **NDJSON format**: Industry standard for log files; each line is independent JSON
2. **Pre-compiled regex**: Compile secret patterns once at module load for performance
3. **Fail-open design**: Hook failures should not block user interaction

### Anti-Patterns to Avoid

1. **Full file rewrite on append**: Use atomic line append instead
2. **Synchronous I/O in hot path**: File operations should be fast or async
3. **Unbounded content**: Truncate very long entries to prevent DoS
4. **Secrets in error messages**: Filter before any logging, including error logs

## Content Filtering Research

### Profanity Filtering Approaches

**Libraries Evaluated**:

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| @2toad/profanity | TypeScript-first, word boundaries, multi-language | npm-only | Best for TS projects |
| obscenity | Catches leet speak variants | Complex setup | Good for adversarial content |
| bad-words | Simple, lightweight | High false positive rate | Too basic |

**Selected Approach**: Custom word list in Python with:
- Word boundary matching (`\b` regex)
- Case-insensitive matching
- User-extensible word list
- No external dependencies

**Word List Sources**:
- Google's "what do you love" banned words
- Common variations and misspellings

### Secret Detection Patterns

**Sources Consulted**:
- gitleaks project (https://github.com/gitleaks/gitleaks)
- secrets-patterns-db (https://github.com/mazen160/secrets-patterns-db)
- Semgrep secrets rules

**High-Priority Patterns**:

```python
SECRET_PATTERNS = {
    # Cloud providers
    'aws_access_key': r'\b(AKIA|ASIA|ABIA|ACCA)[A-Z2-7]{16}\b',
    'aws_secret_key': r'(?i)aws.{0,20}secret.{0,20}['\"][0-9a-zA-Z/+=]{40}['\"]',

    # Version control
    'github_pat': r'ghp_[A-Za-z0-9_]{36,}',
    'github_oauth': r'gho_[A-Za-z0-9_]{36,}',
    'gitlab_token': r'glpat-[A-Za-z0-9\-_]{20,}',

    # AI services
    'openai_key': r'sk-[a-zA-Z0-9]{20,}T3BlbkFJ[a-zA-Z0-9]{20,}',
    'anthropic_key': r'sk-ant-api\d{2}-[a-zA-Z0-9_\-]{80,}',

    # Generic
    'bearer_token': r'Bearer\s+[a-zA-Z0-9\-_.~+\/]+=*',
    'basic_auth': r'Basic\s+[a-zA-Z0-9+/]+=*',
    'jwt': r'ey[a-zA-Z0-9]{17,}\.ey[a-zA-Z0-9\/\\_-]{17,}\.[a-zA-Z0-9\/\\_-]{10,}',

    # Connection strings
    'connection_string': r'(?:mongodb|postgres|mysql|redis):\/\/[^\s\'"]+',

    # Private keys (header detection)
    'private_key': r'-----BEGIN\s+(?:RSA|DSA|EC|OPENSSH|PGP)?\s*PRIVATE KEY-----',
}
```

**False Positive Mitigation**:
- Require minimum length for generic patterns
- Use word boundaries where appropriate
- Allow whitelist for known safe patterns (test fixtures)

## JSON Logging Research

### Libraries Compared

| Library | Speed | Format | Features | Verdict |
|---------|-------|--------|----------|---------|
| Pino | Fastest | NDJSON | Redaction, transports | Best for Node.js |
| Winston | Medium | Flexible | Multi-transport | Overkill for this use |
| Python logging | Slow | Flexible | Built-in | Too basic |
| Custom | Variable | Any | Full control | Best for Python hook |

**Selected Approach**: Custom Python logging with:
- NDJSON format (one JSON object per line)
- File locking for concurrent safety
- ISO 8601 timestamps
- Structured metadata fields

### Log Entry Schema

```json
{
  "timestamp": "2025-12-12T22:00:00Z",
  "session_id": "abc123",
  "type": "user_input|expanded_prompt|response_summary",
  "command": "/arch:p|null",
  "content": "...",
  "filter_applied": {
    "profanity_count": 0,
    "secret_count": 0,
    "secret_types": []
  },
  "metadata": {
    "content_length": 150,
    "cwd": "/path/to/project"
  }
}
```

## Open Questions from Research

- [x] Can hooks access expanded slash command content? → Yes, via command context or transcript
- [x] What's the best format for log files? → NDJSON
- [x] How to handle concurrent writes? → File locking (fcntl)
- [ ] How to reliably detect /arch:* context? → Need to test with actual sessions
- [ ] Performance impact of regex pattern matching? → Need benchmarking

## Sources

### Codebase
- hookify plugin: `~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/`
- arch commands: `~/.claude/commands/arch/`
- hook-development skill: `~/.claude/plugins/cache/claude-code-plugins/plugin-dev/0.1.0/skills/hook-development/`

### External
- gitleaks: https://github.com/gitleaks/gitleaks
- secrets-patterns-db: https://github.com/mazen160/secrets-patterns-db
- @2toad/profanity: https://github.com/2Toad/Profanity
- obscenity: https://github.com/jo3-l/obscenity
- Pino logger: https://github.com/pinojs/pino
- Python fcntl: https://docs.python.org/3/library/fcntl.html
