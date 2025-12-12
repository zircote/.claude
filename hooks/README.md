# Prompt Capture Hook System

The Prompt Capture Hook automatically logs all prompts during `/arch:*` architecture sessions, providing traceability, audit trails, and data-driven retrospective insights.

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  User types prompt during /arch:* session                           │
│                              ↓                                      │
│  Hookify plugin triggers UserPromptSubmit event                     │
│                              ↓                                      │
│  prompt_capture_hook.py checks:                                     │
│    • Is .prompt-log-enabled marker present?                         │
│    • Is this an /arch:* context?                                    │
│                              ↓                                      │
│  Filter pipeline processes content:                                 │
│    1. Secrets filter (25+ patterns from gitleaks)                   │
│    2. Profanity filter (50+ words, word-boundary matching)          │
│                              ↓                                      │
│  Append filtered entry to PROMPT_LOG.json (NDJSON format)           │
│                              ↓                                      │
│  On /arch:c close-out:                                              │
│    • Analyze log → Generate Interaction Analysis                    │
│    • Include insights in RETROSPECTIVE.md                           │
│    • Auto-disable logging (remove marker)                           │
│    • Move log file with project to completed/                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Installation

### Quick Start (Fresh Clone)

After cloning the `.claude` repository to `~/.claude/`:

```bash
# Run the installation script
~/.claude/hooks/install.sh
```

### Manual Installation

If you need to manually set up or re-enable after updating the hookify plugin:

```bash
# 1. Ensure hook files exist (automatic if repo is at ~/.claude/)
ls ~/.claude/hooks/prompt_capture_hook.py

# 2. Apply the hookify patch to register the hook
cp -r ~/.claude/patches/hookify-0.1.0/* ~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/

# 3. Verify the patch was applied
grep "prompt_capture_hook" ~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/hooks/hooks.json
```

### After Hookify Plugin Updates

When the hookify plugin is updated, the patch needs to be reapplied:

```bash
cp -r ~/.claude/patches/hookify-0.1.0/* ~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/
```

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `/arch:log on` | Enable prompt logging for the active architecture project |
| `/arch:log off` | Disable prompt logging |
| `/arch:log status` | Check current logging status and log file size |
| `/arch:log show` | Display last 10 log entries in readable format |

### Typical Workflow

```bash
# 1. Start a new architecture project
/arch:p my-new-feature

# 2. Enable logging (optional - do this anytime during the project)
/arch:log on

# 3. Work on the project - all prompts are automatically captured
/arch:i
# ... implementation work ...

# 4. Check logging status
/arch:log status
# Output: 📝 Logging: ENABLED
#         📂 Project: 2025-12-12-my-new-feature
#         📊 Log entries: 47 (12KB)

# 5. Close out project - log is analyzed automatically
/arch:c
# Output includes: Interaction Analysis with metrics and insights
```

## File Structure

```
~/.claude/
├── hooks/
│   ├── prompt_capture_hook.py      # Main hook entry point
│   ├── log_cli.py                  # CLI for manual logging
│   ├── install.sh                  # Installation script
│   ├── filters/
│   │   ├── profanity.py            # Profanity detection (word-boundary)
│   │   ├── profanity_words.txt     # 50+ profanity words
│   │   ├── secrets.py              # 25+ secret patterns
│   │   ├── pipeline.py             # Filter orchestration
│   │   ├── log_entry.py            # NDJSON schema definitions
│   │   ├── log_writer.py           # Atomic append with locking
│   │   └── response_summarizer.py  # Heuristic summarization
│   ├── analyzers/
│   │   ├── log_analyzer.py         # Metrics and insights
│   │   └── analyze_cli.py          # CLI wrapper
│   └── tests/
│       ├── test_filters.py         # Filter tests
│       ├── test_log_entry.py       # Log entry/writer tests
│       └── test_analyzer.py        # Analyzer tests
├── commands/arch/
│   └── log.md                      # /arch:log command definition
└── patches/hookify-0.1.0/
    └── hooks/hooks.json            # Patched to include our hook
```

## Log Format (NDJSON)

Each log entry is a single JSON line (Newline-Delimited JSON):

```json
{
  "timestamp": "2025-12-12T20:19:04.104248+00:00",
  "session_id": "abc123",
  "type": "user_input",
  "command": "/arch:p",
  "content": "Create a new authentication system with [FILTERED] and [SECRET:aws_access_key]",
  "filter_applied": {
    "profanity_count": 1,
    "secret_count": 1,
    "secret_types": ["aws_access_key"]
  },
  "metadata": {
    "content_length": 78,
    "cwd": "/path/to/project"
  }
}
```

**Entry Types**:
- `user_input` - Direct user prompts (captured automatically)
- `expanded_prompt` - Slash command expansions (via CLI utility)
- `response_summary` - Claude response summaries (via CLI utility)

## Content Filtering

### Secrets Filter (25+ Patterns)

Based on [gitleaks](https://github.com/gitleaks/gitleaks) patterns:

| Category | Examples |
|----------|----------|
| **Cloud** | AWS access keys, AWS secret keys, GCP API keys |
| **Git** | GitHub PAT, GitLab PAT, GitHub OAuth tokens |
| **AI Services** | OpenAI keys, Anthropic keys |
| **Payment** | Stripe keys (secret & publishable) |
| **Communication** | Slack tokens, Slack webhooks, SendGrid, Mailgun |
| **Databases** | PostgreSQL URIs, MySQL URIs, MongoDB URIs, Redis URIs |
| **Auth** | JWT tokens, Bearer tokens, Basic auth |
| **Crypto** | Private keys (RSA, DSA, EC, OpenSSH, PGP) |
| **Generic** | Password assignments, secret assignments |

Detected secrets are replaced with `[SECRET:type]` placeholders.

### Profanity Filter (50+ Words)

- Word-boundary matching (won't match "assess" or "classic")
- Case-insensitive detection
- Replaced with `[FILTERED]` placeholder

## Automatic Analysis

When `/arch:c` closes a project, the log is automatically analyzed:

### Metrics Generated

| Metric | Description |
|--------|-------------|
| Total Prompts | All captured entries |
| User Inputs | Direct user prompts |
| Sessions | Unique session count |
| Questions Asked | Prompts containing "?" |
| Avg Prompt Length | Character count analysis |
| Commands Used | Frequency of /arch:* commands |
| Content Filtered | Profanity and secrets filtered |

### Insights Generated

- **High clarification sessions**: Sessions with >10 questions (unclear initial requirements)
- **Question-heavy interaction**: >50% of prompts are questions
- **Multiple sessions**: Project required many sessions (consider smaller scope)
- **Short prompts**: <50 chars average (more detail may help)
- **Detailed prompts**: >500 chars average (good context provided)

### Example Interaction Analysis Output

```markdown
## Interaction Analysis

*Auto-generated from prompt capture logs*

### Metrics

| Metric | Value |
|--------|-------|
| Total Prompts | 47 |
| User Inputs | 42 |
| Sessions | 3 |
| Avg Prompts/Session | 15.7 |
| Questions Asked | 12 |
| Total Duration | 180 minutes |
| Avg Prompt Length | 156 chars |

### Commands Used

- `/arch:p`: 1 times
- `/arch:i`: 8 times
- `/arch:s`: 3 times

### Insights

- Multiple sessions: Project required 3 sessions. Consider breaking down future projects into smaller chunks.
- Detailed prompts: Average prompt was over 500 characters. This level of detail likely improved Claude's understanding.

### Recommendations for Future Projects

- Interaction patterns were efficient. Continue current prompting practices.
```

## Troubleshooting

### Hook Not Capturing Prompts

1. **Check if logging is enabled**:
   ```bash
   /arch:log status
   ```

2. **Verify hook is registered**:
   ```bash
   grep "prompt_capture_hook" ~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/hooks/hooks.json
   ```

3. **Reapply patch if needed**:
   ```bash
   cp -r ~/.claude/patches/hookify-0.1.0/* ~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/
   ```

4. **Check for errors** (hook writes to stderr):
   ```bash
   # Errors appear in Claude Code's debug output
   ```

### Log File Not Created

- Ensure `.prompt-log-enabled` marker exists in the project directory
- Verify you're in an `/arch:*` context (hook only activates for arch commands)
- Check directory permissions

### Tests Failing

Run the test suite to verify installation:

```bash
cd ~/.claude/hooks && python3 -m unittest discover -s tests -v
```

All 44 tests should pass.

## Architecture Reference

For detailed technical documentation, see:
- `docs/architecture/completed/2025-12-12-prompt-capture-log/ARCHITECTURE.md`
- `docs/architecture/completed/2025-12-12-prompt-capture-log/REQUIREMENTS.md`
- `docs/architecture/completed/2025-12-12-prompt-capture-log/DECISIONS.md`
