# Claude Spec Plugin

A comprehensive Claude Code plugin for project specification and implementation lifecycle management.

## Features

- **`/cs:*` Commands** - Full project planning lifecycle
  - `/cs:p` - Strategic project planning with Socratic requirements elicitation
  - `/cs:i` - Implementation progress tracking with document sync
  - `/cs:s` - Portfolio and project status monitoring
  - `/cs:c` - Project close-out and archival
  - `/cs:log` - Prompt capture toggle
  - `/cs:migrate` - Migration from legacy `/arch:*` commands

- **`/cs:wt:*` Worktree Commands** - Git worktree automation
  - `/cs:wt:create` - Create worktrees with Claude agents
  - `/cs:wt:status` - View worktree status
  - `/cs:wt:cleanup` - Clean up worktrees

- **Prompt Capture** - Session logging for traceability and retrospectives

- **Parallel Agent Orchestration** - Built-in directives for parallel specialist agent usage

## Installation

### Local Installation

1. Create local marketplace configuration:
```bash
mkdir -p ~/.claude/marketplaces
cat > ~/.claude/marketplaces/local.json << 'EOF'
{
  "name": "Local Plugin Marketplace",
  "plugins": [
    {
      "name": "claude-spec",
      "path": "/path/to/claude-spec"
    }
  ]
}
EOF
```

2. Install the plugin:
```bash
claude plugins install --marketplace ~/.claude/marketplaces/local.json claude-spec
```

3. Verify installation:
```bash
claude plugins list
```

## Usage

### Start a New Project

```
/cs:p my new feature idea
```

This initiates Socratic requirements elicitation, parallel research, and generates:
- `docs/spec/active/YYYY-MM-DD-project-slug/`
  - README.md
  - REQUIREMENTS.md
  - ARCHITECTURE.md
  - IMPLEMENTATION_PLAN.md
  - DECISIONS.md
  - RESEARCH_NOTES.md
  - CHANGELOG.md

### Track Implementation Progress

```
/cs:i project-slug
```

Creates and maintains PROGRESS.md, syncs checkboxes across documents.

### Check Project Status

```
/cs:s              # Current project status
/cs:s --list       # List all active projects
/cs:s --expired    # Find expired plans
```

### Close Out Project

```
/cs:c project-slug
```

Generates RETROSPECTIVE.md, archives to `docs/spec/completed/`.

### Worktree Management

```
# Natural language triggers
"spin up worktrees for feature/auth, feature/payments"
"worktree status"
"cleanup the auth worktree"

# Or explicit commands
/cs:wt:create feature/auth feature/payments
/cs:wt:status
/cs:wt:cleanup feature/auth
```

### Prompt Capture

```
/cs:log on      # Enable prompt capture
/cs:log off     # Disable prompt capture
/cs:log status  # Check status
/cs:log show    # View captured prompts
```

### Migration from /arch:*

```
/cs:migrate
```

Moves `docs/architecture/` to `docs/spec/` and updates CLAUDE.md references.

## Configuration

### Worktree Configuration

Edit `worktree/config.json`:

```json
{
  "terminal": "iterm2",
  "shell": "bash",
  "claudeCommand": "cc",
  "portPool": { "start": 8100, "end": 8199 },
  "portsPerWorktree": 2,
  "worktreeBase": "~/Projects/worktrees"
}
```

## Project Structure

```
docs/spec/
├── active/           # In-progress projects
│   └── YYYY-MM-DD-slug/
│       ├── README.md
│       ├── REQUIREMENTS.md
│       ├── ARCHITECTURE.md
│       ├── IMPLEMENTATION_PLAN.md
│       ├── PROGRESS.md
│       ├── DECISIONS.md
│       ├── RESEARCH_NOTES.md
│       ├── CHANGELOG.md
│       └── .prompt-log-enabled
└── completed/        # Archived projects
    └── YYYY-MM-DD-slug/
        └── (same + RETROSPECTIVE.md)
```

## Requirements

- Claude Code CLI
- Git (for worktree operations)
- Python 3 (for hooks)
- jq (for registry operations)
- Terminal app (iTerm2, Ghostty, tmux, etc.)

## Attribution

The worktree management functionality is based on the original `worktree-manager` skill.

## License

MIT
