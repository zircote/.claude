---
document_type: architecture
project_id: ARCH-2025-12-12-002
version: 1.0.0
last_updated: 2025-12-12T22:00:00Z
status: completed
---

# Prompt Capture Log - Technical Architecture

## System Overview

The Prompt Capture Log system intercepts user prompts during `/arch:*` command sessions, applies content filtering, and writes structured logs to the active architecture project directory. The system integrates with the existing hookify plugin infrastructure and adds analysis capabilities to the `/arch:c` close-out command.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Claude Code Session                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         UserPromptSubmit Event                               │
│  {user_prompt, session_id, cwd, transcript_path, hook_event_name}           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      prompt_capture_hook.py                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │   Toggle    │──▶│   Filter    │──▶│   Filter    │──▶│   Write     │     │
│  │   Check     │   │  Profanity  │   │   Secrets   │   │    Log      │     │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘     │
│         │                                                     │             │
│         ▼                                                     ▼             │
│  .prompt-log-enabled                              PROMPT_LOG.json           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          /arch:c Close-out                                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                       │
│  │    Read     │──▶│   Analyze   │──▶│   Write     │                       │
│  │    Logs     │   │   Metrics   │   │   Retro     │                       │
│  └─────────────┘   └─────────────┘   └─────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Implementation language | Python | Matches existing hookify plugin, no additional runtime |
| Log format | NDJSON (newline-delimited JSON) | Atomic append, streaming read, corruption-resistant |
| Toggle persistence | File marker (`.prompt-log-enabled`) | Simple, visible, no database needed |
| Filter approach | Pre-write pipeline | Secrets never touch disk in cleartext |
| Response capture | Summary extraction | Full responses too verbose, summaries sufficient |

## Component Design

### Component 1: Prompt Capture Hook

- **Purpose**: Intercept UserPromptSubmit events and log prompt data
- **Responsibilities**:
  - Check if logging is enabled for current project
  - Detect if session is within `/arch:*` command context
  - Extract user prompt and expanded command content
  - Apply content filters
  - Write to project-specific log file
- **Interfaces**: stdin (JSON), stdout (JSON response), filesystem (log writes)
- **Dependencies**: hookify infrastructure, filter modules
- **Technology**: Python 3.8+

**File**: `~/.claude/hooks/prompt_capture_hook.py`

```python
# Core hook entry point
def main():
    input_data = json.load(sys.stdin)

    # Check toggle and context
    if not is_logging_enabled(input_data['cwd']):
        return pass_through()

    if not is_arch_context(input_data):
        return pass_through()

    # Filter and log
    filtered_prompt = filter_pipeline(input_data['user_prompt'])
    log_entry = build_entry(input_data, filtered_prompt)
    append_to_log(input_data['cwd'], log_entry)

    return pass_through()
```

### Component 2: Content Filter Pipeline

- **Purpose**: Remove sensitive content before logging
- **Responsibilities**:
  - Profanity detection and replacement
  - Secret pattern detection and masking
  - Preserve content structure while filtering
- **Interfaces**: `filter(text: str) -> FilterResult`
- **Dependencies**: Pattern files, word lists
- **Technology**: Python regex, word list matching

**File**: `~/.claude/hooks/filters/`

```
filters/
├── __init__.py
├── profanity.py      # Profanity word list and detection
├── secrets.py        # Secret pattern regex collection
└── pipeline.py       # Orchestrates filter chain
```

**Filter Result Structure**:
```python
@dataclass
class FilterResult:
    original_length: int
    filtered_text: str
    profanity_count: int
    secret_count: int
    secret_types: List[str]
```

### Component 3: Toggle Manager

- **Purpose**: Manage logging enable/disable state per project
- **Responsibilities**:
  - Create/remove toggle marker file
  - Check toggle state
  - Handle toggle command (`/arch:log`)
- **Interfaces**: CLI command, file operations
- **Dependencies**: Project directory structure
- **Technology**: Bash script (for command) + Python (for hook check)

**Toggle State**:
- **Enabled**: `.prompt-log-enabled` file exists in project directory
- **Disabled**: File does not exist
- **Default**: Disabled until explicitly enabled

**File**: `~/.claude/commands/arch/log.md`

### Component 4: Log Writer

- **Purpose**: Safely append entries to PROMPT_LOG.json
- **Responsibilities**:
  - Atomic append operations
  - Create log file if not exists
  - Handle concurrent writes gracefully
- **Interfaces**: `append_entry(project_path: str, entry: LogEntry)`
- **Dependencies**: Filesystem
- **Technology**: Python file I/O with locking

**Atomic Append Pattern**:
```python
def append_entry(project_path: str, entry: LogEntry):
    log_path = os.path.join(project_path, 'PROMPT_LOG.json')

    with open(log_path, 'a') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(json.dumps(entry.to_dict()) + '\n')
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

### Component 5: Log Analyzer

- **Purpose**: Generate insights from captured logs for retrospective
- **Responsibilities**:
  - Parse PROMPT_LOG.json
  - Calculate metrics (prompt count, session duration, clarification ratio)
  - Generate markdown summary for RETROSPECTIVE.md
- **Interfaces**: Called by `/arch:c` command
- **Dependencies**: Log file, RETROSPECTIVE.md template
- **Technology**: Python analysis script

**Metrics Calculated**:
```python
@dataclass
class LogAnalysis:
    total_prompts: int
    user_prompts: int
    expanded_prompts: int
    response_summaries: int
    session_count: int
    avg_prompts_per_session: float
    clarification_questions: int  # Questions containing "?"
    filtered_content_count: int
    total_duration_minutes: float
    prompt_length_stats: Dict[str, float]  # min, max, avg
```

**File**: `~/.claude/hooks/analyzers/log_analyzer.py`

### Component 6: Response Summarizer

- **Purpose**: Generate concise summaries of Claude responses for logging
- **Responsibilities**:
  - Extract key points from Claude responses
  - Limit summary length
  - Preserve essential information
- **Interfaces**: `summarize(response: str, max_length: int) -> str`
- **Dependencies**: None (heuristic-based)
- **Technology**: Python text processing

**Summarization Strategy**:
1. Extract first paragraph (typically contains main point)
2. Extract any bullet points or numbered lists
3. Truncate to max_length with ellipsis if needed
4. Preserve code block indicators without full content

## Data Design

### Log Entry Schema

```json
{
  "timestamp": "2025-12-12T22:00:00Z",
  "session_id": "abc123def456",
  "type": "user_input | expanded_prompt | response_summary",
  "command": "/arch:p | /arch:i | /arch:s | /arch:c | null",
  "content": "The actual prompt or summary text",
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

### Log File Structure (NDJSON)

```
{"timestamp":"2025-12-12T22:00:00Z","type":"user_input","command":"/arch:p",...}
{"timestamp":"2025-12-12T22:00:01Z","type":"expanded_prompt","command":"/arch:p",...}
{"timestamp":"2025-12-12T22:05:00Z","type":"user_input","command":null,...}
{"timestamp":"2025-12-12T22:05:30Z","type":"response_summary","command":null,...}
```

### Toggle Marker File

**Path**: `docs/architecture/active/[project]/.prompt-log-enabled`

**Content**: Empty file (presence = enabled)

**Alternative (with metadata)**:
```json
{
  "enabled_at": "2025-12-12T22:00:00Z",
  "enabled_by": "user",
  "sessions_logged": 0
}
```

### Data Flow

```
User types prompt
        │
        ▼
┌───────────────────┐
│  Claude Code CLI  │
└───────────────────┘
        │
        ▼ UserPromptSubmit event
┌───────────────────┐
│  Hook Dispatcher  │
└───────────────────┘
        │
        ▼
┌───────────────────┐    ┌─────────────────┐
│ prompt_capture    │───▶│ .prompt-log-    │
│ _hook.py          │    │  enabled check  │
└───────────────────┘    └─────────────────┘
        │                        │
        │ if enabled             │
        ▼                        │
┌───────────────────┐            │
│  Filter Pipeline  │◀───────────┘
│  (profanity,      │
│   secrets)        │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   Log Writer      │
│   (NDJSON append) │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  PROMPT_LOG.json  │
└───────────────────┘
```

## API Design

### Hook Input (stdin)

```json
{
  "hook_event_name": "UserPromptSubmit",
  "user_prompt": "string - the user's input",
  "session_id": "string - unique session identifier",
  "cwd": "string - current working directory",
  "transcript_path": "string - path to session transcript"
}
```

### Hook Output (stdout)

```json
{
  "decision": "approve",
  "systemMessage": "Prompt logged successfully",
  "additionalContext": ""
}
```

### /arch:log Command Interface

```bash
# Enable logging for current project
/arch:log on

# Disable logging
/arch:log off

# Show current status and recent entries
/arch:log show

# Show status only
/arch:log status
```

## Integration Points

### Internal Integrations

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| hookify plugin | Hook registration | Register prompt_capture_hook in hooks.json |
| /arch:p command | Context detection | Detect when planning session is active |
| /arch:c command | Analysis trigger | Call log analyzer, generate retrospective section |
| Project directory | File I/O | Read/write log files and toggle markers |

### Hook Registration (hooks.json extension)

```json
{
  "UserPromptSubmit": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python3 ~/.claude/hooks/prompt_capture_hook.py",
          "timeout": 5000
        }
      ]
    }
  ]
}
```

### /arch:c Integration

The close-out command will be modified to:
1. Check for PROMPT_LOG.json in project directory
2. If exists, run log analyzer
3. Append "## Interaction Analysis" section to RETROSPECTIVE.md
4. Disable logging (remove .prompt-log-enabled)
5. Move PROMPT_LOG.json with other artifacts to completed/

## Security Design

### Secrets Never Written to Disk

```python
def log_prompt(prompt: str, project_path: str):
    # Filter BEFORE any file operation
    filtered = filter_pipeline(prompt)

    # Only write filtered content
    append_to_log(project_path, filtered)
```

### Filter Patterns (Secrets)

Priority patterns based on gitleaks:

```python
SECRET_PATTERNS = {
    # High-priority (common in dev)
    'aws_access_key': r'\b(AKIA|ASIA|ABIA|ACCA)[A-Z2-7]{16}\b',
    'github_token': r'gh[pousr]_[A-Za-z0-9_]{36,}',
    'openai_key': r'sk-[a-zA-Z0-9]{20,}T3BlbkFJ[a-zA-Z0-9]{20,}',
    'anthropic_key': r'sk-ant-api\d{2}-[a-zA-Z0-9_\-]{80,}',

    # Generic patterns
    'bearer_token': r'Bearer\s+[a-zA-Z0-9\-_.~+\/]+=*',
    'password_assign': r'(?:password|passwd|pwd)\s*[:=]\s*[\'"][^\'"]{8,}[\'"]',
    'connection_string': r'(?:mongodb|postgres|mysql|redis):\/\/[^\s\'"]+',

    # Private keys (detect header only)
    'private_key': r'-----BEGIN\s+(?:RSA|DSA|EC|OPENSSH|PGP)?\s*PRIVATE KEY-----',
}
```

### Profanity Word List

Externalized to `~/.claude/hooks/filters/profanity_words.txt`:
- One word per line
- Case-insensitive matching
- Supports wildcards (e.g., `f*ck` matches variations)
- User can extend via `profanity_words_custom.txt`

## Performance Considerations

### Expected Load

- Prompts per session: 10-50
- Sessions per day: 1-5
- Average prompt length: 100-500 characters
- Log file growth: ~50KB per session

### Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Hook latency | <100ms | User should not notice delay |
| Log write time | <10ms | Async, buffered writes |
| Filter processing | <50ms | Regex pre-compilation |
| Analysis time | <5s | Acceptable at close-out |

### Optimization Strategies

1. **Regex pre-compilation**: Compile all patterns at module load
2. **Async file writes**: Use file locking but don't block return
3. **Lazy loading**: Only load filter modules when logging enabled
4. **NDJSON format**: Append-only, no full-file rewrites

## Testing Strategy

### Unit Testing

- Filter functions: Test each pattern against known examples
- Log writer: Test atomic append, concurrent access
- Toggle manager: Test enable/disable state transitions
- Analyzer: Test metric calculations against sample logs

### Integration Testing

- Hook registration: Verify hook fires on UserPromptSubmit
- End-to-end logging: Submit prompt, verify log entry
- /arch:c integration: Verify analysis appears in retrospective

### Test Data

```python
# Secret detection tests
TEST_SECRETS = [
    ('AKIA<EXAMPLE_AWS_KEY_HERE>', 'aws_access_key'),
    ('ghp_<EXAMPLE_GITHUB_TOKEN_HERE>', 'github_token'),
    ('<EXAMPLE_OPENAI_KEY_FORMAT>', 'openai_key'),
]

# Profanity tests
TEST_PROFANITY = [
    ('This is fine', False),
    ('What the [filtered]', True),
]
```

## Deployment Considerations

### Installation

1. Copy hook files to `~/.claude/hooks/`
2. Update `~/.claude/settings.json` or hookify hooks.json
3. Create filter word lists
4. Restart Claude Code session

### Configuration Files

```
~/.claude/
├── hooks/
│   ├── prompt_capture_hook.py
│   ├── filters/
│   │   ├── __init__.py
│   │   ├── profanity.py
│   │   ├── secrets.py
│   │   ├── pipeline.py
│   │   └── profanity_words.txt
│   └── analyzers/
│       └── log_analyzer.py
├── commands/
│   └── arch/
│       └── log.md           # Toggle command
└── settings.json            # Hook registration (if not using hookify)
```

### Rollback Plan

1. Remove hook registration from hooks.json
2. Hook will stop firing
3. Existing logs remain intact
4. No cleanup required

## Future Considerations

1. **Multi-user support**: Log user identifier for team environments
2. **Log rotation**: Archive old logs to prevent unbounded growth
3. **Real-time analysis**: Show prompting quality indicators during session
4. **Export formats**: Generate markdown, HTML reports from logs
5. **Pattern learning**: Identify common effective prompt patterns across projects
