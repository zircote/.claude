# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# Global Claude Instructions — Concise

**ALWAYS** ask questions when producing a plan until you have reached 95% or GREATER confidence. ALWAYS DO THIS.

These rules guide Claude across projects. Preserve protocols; keep wording minimal.

## Environment & Standards Includes

When working in these environments, read and follow the corresponding file:

| Environment | Include File |
|-------------|--------------|
| Python | `~/.claude/includes/python.md` |
| React/TypeScript | `~/.claude/includes/react.md` |
| Go | `~/.claude/includes/golang.md` |
| Git/Version Control | `~/.claude/includes/git.md` |
| Testing (any language) | `~/.claude/includes/testing.md` |
| Documentation | `~/.claude/includes/documentation.md` |
| MCP Tools/Skills/Agents | `~/.claude/includes/mcp-reference.md` |
| GitHub Actions | `~/.claude/includes/github-actions.md` |
| Version Discovery | `~/.claude/includes/version-discovery.md` |
| Opus 4.5 (General) | `~/.claude/includes/opus-4-5.md` |
| Opus 4.5 (Agentic) | `~/.claude/includes/opus-4-5-agent.md` |
| HMHCO Organization | `~/.claude/includes/hmhco.md` |

**Usage**: Read the relevant include file(s) at the start of environment-specific tasks to ensure compliance with standards.

## Custom Commands

### Git Workflow (`/git`)

| Command | Description |
|---------|-------------|
| `/git:cm` | Stage all files and create a commit (conventional commits, splits new vs modified) |
| `/git:cp` | Stage, commit, and push all changes |
| `/git:pr [to-branch]` | Create a pull request using `gh` CLI |

### Architecture Planning (`/arch`)

| Command | Description |
|---------|-------------|
| `/arch:p <project-idea>` | Strategic project planner with Socratic requirements elicitation, PRD, and implementation plan |
| `/arch:i [project-id\|project-slug]` | Implementation progress tracker with PROGRESS.md checkpoint file, task tracking, and document sync |
| `/arch:s [project-id\|--list\|--expired]` | Project status, portfolio listing, find expired plans |
| `/arch:c <project-path\|project-id>` | Close out completed project, archive artifacts, generate retrospective |
| `/arch:log <on\|off\|status\|show>` | Toggle prompt capture logging for architecture work |

Workflow: `/arch:p` to plan → `/arch:i` to implement → `/arch:s` to monitor → `/arch:c` to complete

**PROGRESS.md Checkpoint System**: The `/arch:i` command creates and maintains a PROGRESS.md file in the project directory that:
- Tracks task status (pending/in-progress/done/skipped) with timestamps
- Calculates phase and project progress automatically
- Logs divergences from the original plan
- Syncs state to IMPLEMENTATION_PLAN.md checkboxes and README.md frontmatter
- Persists state across Claude sessions

**Completed Architecture Projects**:
- `docs/architecture/completed/2025-12-12-prompt-capture-log/` - Prompt Capture Log
  - Completed: 2025-12-12
  - Outcome: success
  - Key docs: REQUIREMENTS.md, ARCHITECTURE.md, RETROSPECTIVE.md
- `docs/architecture/completed/2025-12-12-arch-lifecycle-automation/` - Architecture Lifecycle Automation
  - Completed: 2025-12-12
  - Outcome: success
  - Key docs: REQUIREMENTS.md, ARCHITECTURE.md, RETROSPECTIVE.md

### Opus 4.5 Optimized

| Command | Description |
|---------|-------------|
| `/explore <path\|pattern\|question>` | Exhaustive codebase exploration with parallel subagents and anti-hallucination enforcement |
| `/deep-research <topic\|url>` | Multi-phase research protocol with structured deliverables and quality gates |

---

## Prompt Capture Hook System

The Prompt Capture Hook automatically logs all prompts during `/arch:*` architecture sessions, providing traceability, audit trails, and data-driven retrospective insights.

### Overview

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

### Installation

#### Quick Start (Fresh Clone)

After cloning the `.claude` repository to `~/.claude/`:

```bash
# Run the installation script
~/.claude/hooks/install.sh
```

#### Manual Installation

If you need to manually set up or re-enable after updating the hookify plugin:

```bash
# 1. Ensure hook files exist (automatic if repo is at ~/.claude/)
ls ~/.claude/hooks/prompt_capture_hook.py

# 2. Apply the hookify patch to register the hook
cp -r ~/.claude/patches/hookify-0.1.0/* ~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/

# 3. Verify the patch was applied
grep "prompt_capture_hook" ~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/hooks/hooks.json
```

#### After Hookify Plugin Updates

When the hookify plugin is updated, the patch needs to be reapplied:

```bash
cp -r ~/.claude/patches/hookify-0.1.0/* ~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/
```

### Usage

#### Commands

| Command | Description |
|---------|-------------|
| `/arch:log on` | Enable prompt logging for the active architecture project |
| `/arch:log off` | Disable prompt logging |
| `/arch:log status` | Check current logging status and log file size |
| `/arch:log show` | Display last 10 log entries in readable format |

#### Typical Workflow

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

### File Structure

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

### Log Format (NDJSON)

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

### Content Filtering

#### Secrets Filter (25+ Patterns)

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

#### Profanity Filter (50+ Words)

- Word-boundary matching (won't match "assess" or "classic")
- Case-insensitive detection
- Replaced with `[FILTERED]` placeholder

### Automatic Analysis

When `/arch:c` closes a project, the log is automatically analyzed:

#### Metrics Generated

| Metric | Description |
|--------|-------------|
| Total Prompts | All captured entries |
| User Inputs | Direct user prompts |
| Sessions | Unique session count |
| Questions Asked | Prompts containing "?" |
| Avg Prompt Length | Character count analysis |
| Commands Used | Frequency of /arch:* commands |
| Content Filtered | Profanity and secrets filtered |

#### Insights Generated

- **High clarification sessions**: Sessions with >10 questions (unclear initial requirements)
- **Question-heavy interaction**: >50% of prompts are questions
- **Multiple sessions**: Project required many sessions (consider smaller scope)
- **Short prompts**: <50 chars average (more detail may help)
- **Detailed prompts**: >500 chars average (good context provided)

#### Example Interaction Analysis Output

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

- 📈 **Multiple sessions**: Project required 3 sessions. Consider breaking down future projects into smaller chunks.
- 📝 **Detailed prompts**: Average prompt was over 500 characters. This level of detail likely improved Claude's understanding.

### Recommendations for Future Projects

- Interaction patterns were efficient. Continue current prompting practices.
```

### Troubleshooting

#### Hook Not Capturing Prompts

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

#### Log File Not Created

- Ensure `.prompt-log-enabled` marker exists in the project directory
- Verify you're in an `/arch:*` context (hook only activates for arch commands)
- Check directory permissions

#### Tests Failing

Run the test suite to verify installation:

```bash
cd ~/.claude/hooks && python3 -m unittest discover -s tests -v
```

All 44 tests should pass.

### Architecture Reference

For detailed technical documentation, see:
- `docs/architecture/completed/2025-12-12-prompt-capture-log/ARCHITECTURE.md`
- `docs/architecture/completed/2025-12-12-prompt-capture-log/REQUIREMENTS.md`
- `docs/architecture/completed/2025-12-12-prompt-capture-log/DECISIONS.md`

---

## Git Worktree Management

**Always use the `worktree-manager` skill** for ALL git worktree operations. This is the ONLY approved method.

Trigger phrases: "create worktree", "spin up worktrees", "worktree status", "cleanup worktrees"

**Initial prompt support**: Add `with prompt "template"` to auto-execute tasks in each worktree:
```
spin up worktrees for auth, payments with prompt "run tests for {{service}}"
```
Template variables: `{{service}}`, `{{branch}}`, `{{project}}`, `{{port}}`, `{{ports}}`

**DO NOT** use raw `git worktree` commands directly or create ad-hoc worktree workflows.

## Plugin Maintenance

Plugin patches are stored in `~/.claude/patches/`. After plugin updates, reapply patches:
```bash
cp -r ~/.claude/patches/<plugin>-<version>/* ~/.claude/plugins/cache/claude-code-plugins/<plugin>/<version>/
```

For detailed repository structure, see `~/.claude/llms.txt`.

## Skills Quick Reference

Skills are in `~/.claude/skills/`. Key categories:
- **Documents**: `pdf`, `docx`, `xlsx`, `pptx`
- **Media**: `ai-multimodal`, `media-processing`, `chrome-devtools`
- **Development**: `frontend-development`, `backend-development`, `databases`, `devops`
- **AI/Prompting**: `anthropic-prompt-engineer`, `anthropic-architect`
- **Utilities**: `docs-seeker`, `changelog-generator`, `mcp-builder`

Invoke via Skill tool or trigger phrases defined in each skill's `SKILL.md`.

## Opus 4.5 Quick Reference

Key behaviors when running as Opus 4.5:
- **Word sensitivity**: Avoid "think" when extended thinking disabled; use "consider", "evaluate", "believe"
- **Tool triggering**: More responsive than previous models—use normal phrasing, avoid "CRITICAL: MUST"
- **Subagent orchestration**: Proactively delegates to subagents when beneficial (native capability)
- **State discovery**: Excels at discovering state from filesystem—prefer fresh context over compaction
- **Git for state**: Use git logs and structured files (tests.json, progress.txt) for multi-session tasks
- **Investigate first**: Read files before answering—no speculation about unread code

## Parallel Specialist Subagents
Leverage the Task tool with specialized subagents from `~/.claude/agents/` for efficiency.

### Agent Categories (`~/.claude/agents/`)
| Category | Specialists | Use For |
|----------|-------------|---------|
| `01-core-development` | frontend-developer, backend-developer, fullstack-developer, api-designer, microservices-architect, mobile-developer | Application architecture, API design, UI/UX implementation |
| `02-language-specialists` | python-pro, typescript-pro, golang-pro, rust-engineer, java-architect, react-specialist, nextjs-developer | Language-specific implementation, framework expertise |
| `03-infrastructure` | devops-engineer, sre-engineer, kubernetes-specialist, terraform-engineer, cloud-architect, database-administrator | Infrastructure, deployment, cloud, networking |
| `04-quality-security` | code-reviewer, security-auditor, penetration-tester, test-automator, performance-engineer, debugger | Code quality, security analysis, testing, debugging |
| `05-data-ai` | data-scientist, data-engineer, ml-engineer, llm-architect, postgres-pro, prompt-engineer | Data pipelines, ML/AI, database optimization |
| `06-developer-experience` | documentation-engineer, cli-developer, build-engineer, refactoring-specialist, mcp-developer | DX tooling, documentation, build systems |
| `07-specialized-domains` | fintech-engineer, blockchain-developer, game-developer, iot-engineer, payment-integration | Domain-specific expertise |
| `08-business-product` | product-manager, technical-writer, ux-researcher, scrum-master | Product, documentation, process |
| `09-meta-orchestration` | multi-agent-coordinator, workflow-orchestrator, task-distributor | Complex multi-agent workflows |
| `10-research-analysis` | research-analyst, competitive-analyst, market-researcher, trend-analyst | Research, analysis, market intelligence |

### Parallel Execution Rules
- **When to parallelize**: Launch multiple specialists simultaneously when tasks are independent (no output dependencies)
- **Specialist matching**: Route work to the most domain-appropriate agent from `~/.claude/agents/`
- **Dependency awareness**: Only serialize when one agent's output informs another's parameters
- **Consolidation**: Synthesize parallel agent results into a unified response

### Example Patterns
```
PARALLEL: Full-stack feature with security review
→ Launch frontend-developer + backend-developer + security-auditor simultaneously

PARALLEL: Infrastructure + monitoring setup
→ Launch terraform-engineer + sre-engineer + devops-engineer in parallel

PARALLEL: Code quality sweep
→ Launch code-reviewer + performance-engineer + test-automator together

SEQUENTIAL: Research → Implementation
→ research-analyst completes → use findings to guide python-pro implementation

SEQUENTIAL: Design → Build → Review
→ api-designer → backend-developer → code-reviewer (each depends on prior output)
```

Prefer parallel specialist agents over sequential single-threaded work when the task naturally decomposes into independent expert domains.

## API Response Validation
- Treat unexpected empties as suspicious. Do not proceed.
- Steps: STOP → try minimal query → ask user to confirm → document quirk in ~/.claude/learnings/.
- Indicators: user says data exists but API returns 0/empty/null; complex query fails; added filters break.
- Fallback:
```python
r = api_call(complex_params)
if not r and context_suggests_data:
    s = api_call(minimal_params)
    if s: warn_user("Complex query 0, using simplified"); use s
    else: ask_user("API shows 0 — match your UI?")
```
- Be honest: state "API returned 0"; list causes; try alternatives; ask for UI confirmation.
- When actually missing:
```
"The [tool] shows no [data] for the period.
Possible reasons: (1) most likely, (2) alternative, (3) unlikely.
Next: actionable step(s)."
```
- Document quirks: symptom, workaround, date, failing vs working example.
- Golden rule: when in doubt about data quality → ASK THE USER.
