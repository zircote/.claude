---
document_type: architecture
project_id: ARCH-2025-12-12-002
version: 1.0.0
last_updated: 2025-12-12
status: draft
---

# Claude Spec Plugin - Technical Architecture

## System Overview

The `claude-spec` plugin consolidates architecture planning workflows into a standalone, distributable Claude Code plugin. It bundles:

1. **Spec Commands** (`/cs:*`) - Project planning lifecycle
2. **Worktree Commands** (`/cs:wt:*`) - Git worktree management
3. **Prompt Capture** - Session logging via hooks
4. **Templates** - Standardized project artifacts

### Architecture Principles

| Principle | Application |
|-----------|-------------|
| Self-contained | All functionality within plugin directory |
| Dynamic integration | Reads agent catalog from host's CLAUDE.md |
| Graceful degradation | Works without optional host features |
| Clean separation | Commands, hooks, scripts in distinct directories |

---

## Plugin Structure

```
claude-spec/
├── .claude-plugin/
│   └── plugin.json                 # Plugin manifest
│
├── commands/
│   └── cs/
│       ├── p.md                    # /cs:p - Planning
│       ├── i.md                    # /cs:i - Implementation
│       ├── s.md                    # /cs:s - Status
│       ├── c.md                    # /cs:c - Close-out
│       ├── log.md                  # /cs:log - Prompt toggle
│       ├── migrate.md              # /cs:migrate - Migration
│       └── wt/
│           ├── create.md           # /cs:wt:create
│           ├── status.md           # /cs:wt:status
│           └── cleanup.md          # /cs:wt:cleanup
│
├── hooks/
│   ├── hooks.json                  # Hook registration
│   └── prompt_capture.py           # UserPromptSubmit handler
│
├── filters/
│   ├── __init__.py
│   ├── pipeline.py                 # Filter orchestration
│   ├── log_entry.py                # Log entry creation
│   └── log_writer.py               # JSON file writing
│
├── worktree/
│   ├── scripts/
│   │   ├── allocate-ports.sh       # Port allocation
│   │   ├── cleanup.sh              # Worktree removal
│   │   ├── launch-agent.sh         # Terminal + Claude launch
│   │   ├── register.sh             # Registry update
│   │   ├── release-ports.sh        # Port release
│   │   └── status.sh               # Status display
│   ├── config.json                 # Default configuration
│   └── SKILL.md                    # Skill documentation
│
├── templates/
│   ├── README.md                   # Project README template
│   ├── REQUIREMENTS.md             # PRD template
│   ├── ARCHITECTURE.md             # Architecture template
│   ├── IMPLEMENTATION_PLAN.md      # Plan template (with Agent fields)
│   ├── PROGRESS.md                 # Progress tracking template
│   ├── DECISIONS.md                # ADR template
│   ├── RESEARCH_NOTES.md           # Research template
│   ├── CHANGELOG.md                # Changelog template
│   └── RETROSPECTIVE.md            # Retrospective template
│
├── README.md                       # Plugin documentation
├── CHANGELOG.md                    # Plugin changelog
└── LICENSE                         # MIT license
```

---

## Component Design

### Component 1: Plugin Manifest

**File**: `.claude-plugin/plugin.json`

```json
{
  "name": "claude-spec",
  "version": "1.0.0",
  "description": "Project specification and implementation lifecycle management with worktree automation",
  "author": {
    "name": "Claude Spec Contributors"
  },
  "license": "MIT",
  "keywords": ["architecture", "planning", "worktree", "specification"],
  "hooks": "./hooks/hooks.json",
  "commands": "./commands"
}
```

**Key fields:**
- `hooks`: Points to hook registration file
- `commands`: Directory containing slash commands

---

### Component 2: Spec Commands (/cs:*)

Each command is a markdown file in `commands/cs/`.

#### /cs:p - Planning Command

**Purpose**: Create new project with Socratic requirements elicitation

**Flow**:
```
User input → Requirements questions → Parallel research agents →
Document generation → Project directory in docs/spec/active/
```

**Key sections**:
- `<parallel_execution_directive>` - Enforce parallel agent usage
- Research phase with named agents (research-analyst, code-reviewer, etc.)
- Template generation with Agent fields

**Output**:
```
docs/spec/active/YYYY-MM-DD-project-slug/
├── README.md
├── REQUIREMENTS.md
├── ARCHITECTURE.md
├── IMPLEMENTATION_PLAN.md
├── DECISIONS.md
├── RESEARCH_NOTES.md
├── CHANGELOG.md
└── .prompt-log-enabled  (if logging enabled)
```

#### /cs:i - Implementation Command

**Purpose**: Track progress, execute tasks, sync documents

**Key sections**:
- `<parallel_execution_directive>` - Parallel task execution
- `<sync_enforcement>` - Mandatory checkbox/status updates
- PROGRESS.md creation and maintenance

**Sync points**:
1. Task completion → Update checkboxes in IMPLEMENTATION_PLAN.md
2. First task start → README.md status: draft → in-progress
3. Phase completion → Mark phase deliverables complete
4. Project completion → README.md status: in-progress → completed

#### /cs:s - Status Command

**Purpose**: View project and portfolio status

**Features**:
- Single project status
- Portfolio listing (`--list`)
- Expired plan detection (`--expired`)

#### /cs:c - Close-out Command

**Purpose**: Archive completed projects

**Flow**:
```
Validate completion → Generate RETROSPECTIVE.md →
Analyze .prompt-log.json → Move to docs/spec/completed/ →
Update CLAUDE.md references
```

#### /cs:log - Prompt Toggle

**Purpose**: Enable/disable prompt capture for current project

**Actions**:
- `on`: Create `.prompt-log-enabled` marker
- `off`: Remove marker
- `status`: Show current state
- `show`: Display log contents

#### /cs:migrate - Migration Command

**Purpose**: One-time migration from /arch:* to /cs:*

**Actions**:
1. Move `docs/architecture/` → `docs/spec/`
2. Update CLAUDE.md references from `/arch:` to `/cs:`
3. Report migration summary

---

### Component 3: Worktree Commands (/cs:wt:*)

Commands in `commands/cs/wt/` delegate to scripts in `worktree/scripts/`.

#### /cs:wt:create

**Purpose**: Create worktrees with Claude agents

**Flow**:
```
Parse branches → Allocate ports → Create git worktrees →
Copy resources → Install dependencies → Validate →
Register in ~/.claude/worktree-registry.json → Launch agents
```

**Supports**:
- Multiple worktrees in parallel
- Initial prompts with template variables
- Interactive or headless mode

#### /cs:wt:status

**Purpose**: Display worktree status

**Output**: Table with project, branch, ports, status, task

#### /cs:wt:cleanup

**Purpose**: Remove worktrees cleanly

**Flow**:
```
Kill port processes → Remove git worktree →
Update registry → Release ports → Optionally delete branch
```

---

### Component 4: Prompt Capture Hook

**Files**: `hooks/hooks.json`, `hooks/prompt_capture.py`

#### hooks.json

```json
{
  "description": "Prompt capture for claude-spec projects",
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/prompt_capture.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

#### prompt_capture.py

**Input** (via stdin):
```json
{
  "session_id": "string",
  "cwd": "string",
  "prompt": "string",
  "permission_mode": "string",
  "hook_event_name": "UserPromptSubmit"
}
```

**Logic**:
1. Check if `docs/spec/active/*/. prompt-log-enabled` exists
2. If not enabled, pass through immediately
3. Run prompt through filter pipeline
4. Write to `.prompt-log.json` in project directory
5. Return `{"decision": "approve"}`

**Output** (to stdout):
```json
{
  "decision": "approve",
  "systemMessage": "Prompt captured to project log"
}
```

---

### Component 5: Filter Pipeline

**Files**: `filters/pipeline.py`, `filters/log_entry.py`, `filters/log_writer.py`

#### Filter Chain

```
Raw prompt → Secret detection → Profanity filter →
Length truncation → Log entry creation → JSON write
```

#### log_entry.py

```python
@dataclass
class LogEntry:
    timestamp: str
    session_id: str
    entry_type: str  # "user_input"
    content: str
    command: Optional[str]  # "/cs:p", etc.
    cwd: str
    filter_info: dict
```

#### log_writer.py

**File format** (`.prompt-log.json`):
```json
{
  "sessions": ["session-id-1", "session-id-2"],
  "prompts": [
    {
      "timestamp": "2025-12-12T10:00:00Z",
      "session_id": "session-id-1",
      "entry_type": "user_input",
      "content": "filtered prompt content",
      "command": "/cs:p",
      "filter_info": {"secrets_removed": 0, "truncated": false}
    }
  ]
}
```

---

### Component 6: Worktree Scripts

Scripts in `worktree/scripts/` handle git worktree operations.

#### Configuration

**File**: `worktree/config.json`

```json
{
  "terminal": "iterm2",
  "shell": "bash",
  "claudeCommand": "cc",
  "portPool": {
    "start": 8100,
    "end": 8199
  },
  "portsPerWorktree": 2,
  "worktreeBase": "~/Projects/worktrees",
  "registryPath": "~/.claude/worktree-registry.json",
  "defaultCopyDirs": [".agents", ".env.example", ".env"],
  "healthCheckTimeout": 30,
  "healthCheckRetries": 6
}
```

#### Script Reference

| Script | Purpose | Key Operations |
|--------|---------|----------------|
| `allocate-ports.sh` | Reserve ports | Find free ports, update registry |
| `register.sh` | Add to registry | Create worktree entry with metadata |
| `launch-agent.sh` | Start Claude | Open terminal, cd, run claude command |
| `status.sh` | Display status | Read registry, format output |
| `cleanup.sh` | Remove worktree | Kill ports, git worktree remove, update registry |
| `release-ports.sh` | Free ports | Remove from allocated pool |

---

### Component 7: Templates

Templates in `templates/` provide standardized project artifacts.

#### Key Template Features

**IMPLEMENTATION_PLAN.md**:
- Phase Summary with Lead Agent, Parallel Agents columns
- Task template with `- **Agent**:` and `- **Parallel Group**:` fields
- Agent Recommendations section
- Parallel Execution Groups table

**PROGRESS.md**:
- Task Status table with Agent column
- Phase Status with percentages
- Divergence log

**RETROSPECTIVE.md**:
- Prompt analysis section (reads from `.prompt-log.json`)
- Agent effectiveness notes
- Lessons learned

---

## Data Flow

### Planning Flow (/cs:p)

```
┌─────────────────────────────────────────────────────────────┐
│                     /cs:p Planning Flow                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User: "/cs:p my project idea"                              │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────┐                                        │
│  │ Requirements    │  Socratic Q&A until 95% confidence     │
│  │ Elicitation     │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────┐           │
│  │         PARALLEL RESEARCH PHASE              │           │
│  │  ┌────────────┐ ┌────────────┐ ┌──────────┐ │           │
│  │  │research-   │ │code-       │ │security- │ │           │
│  │  │analyst     │ │reviewer    │ │auditor   │ │           │
│  │  └────────────┘ └────────────┘ └──────────┘ │           │
│  └─────────────────────┬───────────────────────┘           │
│                        │                                    │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────┐           │
│  │       PARALLEL DOCUMENTATION PHASE           │           │
│  │  ┌────────────┐ ┌────────────┐ ┌──────────┐ │           │
│  │  │prompt-     │ │architect-  │ │document- │ │           │
│  │  │engineer    │ │reviewer    │ │engineer  │ │           │
│  │  │(IMPL_PLAN) │ │(ARCH)      │ │(REQ)     │ │           │
│  │  └────────────┘ └────────────┘ └──────────┘ │           │
│  └─────────────────────┬───────────────────────┘           │
│                        │                                    │
│                        ▼                                    │
│            docs/spec/active/YYYY-MM-DD-slug/                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Flow (/cs:i)

```
┌─────────────────────────────────────────────────────────────┐
│                   /cs:i Implementation Flow                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Load IMPLEMENTATION_PLAN.md                                │
│      │                                                      │
│      ▼                                                      │
│  Create/Update PROGRESS.md                                  │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────────────────────────────┐           │
│  │    For each Parallel Group (PG-N):          │           │
│  │                                              │           │
│  │    ┌──────────┐ ┌──────────┐ ┌──────────┐  │           │
│  │    │ Task N.1 │ │ Task N.2 │ │ Task N.3 │  │           │
│  │    │ Agent: X │ │ Agent: Y │ │ Agent: Z │  │           │
│  │    └────┬─────┘ └────┬─────┘ └────┬─────┘  │           │
│  │         │            │            │         │           │
│  │         └────────────┴────────────┘         │           │
│  │                      │                      │           │
│  │                      ▼                      │           │
│  │         <sync_enforcement>                  │           │
│  │         Update checkboxes in IMPL_PLAN      │           │
│  │         Update PROGRESS.md                  │           │
│  │         Update README.md status             │           │
│  │                                              │           │
│  └─────────────────────────────────────────────┘           │
│                        │                                    │
│                        ▼                                    │
│               Next Parallel Group...                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Prompt Capture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  Prompt Capture Flow                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User submits prompt                                        │
│      │                                                      │
│      ▼                                                      │
│  Claude Code triggers UserPromptSubmit hook                 │
│      │                                                      │
│      ▼                                                      │
│  prompt_capture.py receives JSON via stdin                  │
│      │                                                      │
│      ▼                                                      │
│  Check: docs/spec/active/*/.prompt-log-enabled exists?      │
│      │                                                      │
│      ├── No ──► Return {"decision": "approve"} ──► Done     │
│      │                                                      │
│      ▼ Yes                                                  │
│  Run filter pipeline                                        │
│      │                                                      │
│      ▼                                                      │
│  Create LogEntry                                            │
│      │                                                      │
│      ▼                                                      │
│  Append to .prompt-log.json                                 │
│      │                                                      │
│      ▼                                                      │
│  Return {"decision": "approve"}                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### With Host CLAUDE.md

The plugin reads the host's CLAUDE.md to discover:
- Agent catalog (`~/.claude/agents/`)
- Parallel execution rules
- Custom configurations

**Lookup logic**:
```
1. Check ~/.claude/CLAUDE.md
2. Parse "Parallel Specialist Subagents" section
3. Extract agent categories and names
4. Use in research phases and task assignments
```

### With Worktree Registry

**File**: `~/.claude/worktree-registry.json`

Shared with host system. Plugin reads/writes worktree entries.

**Concurrency**: Scripts use temp file + mv pattern for atomic updates.

### With Git

- `git worktree add/remove` for worktree management
- `git branch` for branch operations
- `git rev-parse` for repo detection

---

## Error Handling

### Hook Failures

Prompt capture hook always returns `{"decision": "approve"}` even on errors:
- Log errors to stderr
- Never block user prompts
- Graceful degradation

### Script Failures

Worktree scripts:
- Check prerequisites before operations
- Provide clear error messages
- Suggest manual fallback commands

### Missing Dependencies

Commands check for:
- Required host files (CLAUDE.md, agents/)
- External tools (git, jq, terminal app)
- Provide helpful error messages if missing

---

## Security Considerations

### Prompt Filtering

Before logging prompts:
1. Detect and redact secrets (API keys, passwords)
2. Filter profanity (optional)
3. Truncate extremely long prompts

### No Network Calls

Plugin makes no outbound network requests except when explicitly triggered by user commands.

### File Permissions

- Log files created with user-only permissions (600)
- Scripts marked executable during install

---

## Testing Strategy

### Manual Testing

1. **Plugin install**: Verify plugin loads correctly
2. **Command availability**: All `/cs:*` commands in `/help`
3. **Hook registration**: Prompt capture triggers
4. **Template generation**: Projects created with correct structure
5. **Worktree operations**: Create, status, cleanup work

### Test Scenarios

| Scenario | Expected Result |
|----------|-----------------|
| `/cs:p test project` | Creates `docs/spec/active/YYYY-MM-DD-test-project/` |
| `/cs:log on` | Creates `.prompt-log-enabled` marker |
| Type prompt | Entry appears in `.prompt-log.json` |
| `/cs:wt:create feature/x` | Worktree created, agent launched |
| `/cs:migrate` | `docs/architecture/` → `docs/spec/` |

---

## Future Considerations

1. **Plugin marketplace publication**: Package for public distribution
2. **VS Code extension**: UI for status and worktree management
3. **CI/CD integration**: Auto-close projects on PR merge
4. **Multi-repo support**: Coordinate specs across repositories
