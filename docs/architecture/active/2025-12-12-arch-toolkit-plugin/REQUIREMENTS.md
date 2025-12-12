---
document_type: requirements
project_id: ARCH-2025-12-12-002
version: 1.0.0
last_updated: 2025-12-12
status: draft
---

# Claude Spec Plugin - Product Requirements Document

## Executive Summary

Extract the architecture planning workflow (`/arch:*`), prompt capture system, and worktree manager into a standalone, distributable Claude Code plugin named `claude-spec`. The plugin provides a complete project specification and implementation lifecycle with:

- Renamed commands (`/cs:*` instead of `/arch:*`)
- Built-in parallel specialist agent orchestration
- Integrated prompt capture for session traceability
- Full worktree management for isolated development
- Dynamic integration with host's CLAUDE.md agent catalog
- Backward compatibility with existing architecture projects

## Problem Statement

### Current State

The architecture planning tools are scattered across multiple locations:
- Commands in `~/.claude/commands/arch/`
- Prompt capture hook patched into hookify plugin
- Worktree manager as a separate skill
- Configuration and state files in various locations

This creates:
1. **Maintenance burden**: Updates require touching multiple locations
2. **Distribution challenges**: Can't easily share with other users
3. **Integration fragility**: Hookify patches break on updates
4. **Unclear boundaries**: Which files belong to architecture workflows?

### Impact

- Cannot distribute architecture workflow to teammates
- Hookify patches lost on plugin updates
- No clear versioning for the architecture toolkit
- Dependencies on host configuration not documented

## Goals and Success Criteria

### Primary Goal

Create a self-contained Claude Code plugin that bundles all architecture planning functionality into a distributable, versioned package.

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Installation success | 100% | Plugin installs via marketplace |
| Command availability | 5 commands | `/cs:p`, `/cs:i`, `/cs:s`, `/cs:c`, `/cs:log` all work |
| Backward compatibility | 100% | Existing `docs/architecture/active/` projects load |
| Prompt capture | Working | Hooks fire on UserPromptSubmit |
| Worktree manager | Full parity | All existing worktree operations work |

### Non-Goals

- Creating new agent definitions (uses host's `~/.claude/agents/`)
- Modifying Claude Code runtime
- Supporting non-Claude-Code environments
- Migrating completed architecture projects

## User Analysis

### Primary Users

- **Claude instances** executing `/cs:*` commands for planning and implementation
- **Developers** using worktree manager for parallel development

### Secondary Users

- **Plugin developers** using this as a reference implementation
- **Teams** wanting to adopt the architecture workflow

## Functional Requirements

### Must Have (P0)

#### Plugin Infrastructure

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-001 | Valid plugin.json manifest | Plugin must be installable | Manifest validates against Claude Code plugin schema |
| FR-002 | Hooks registration via hooks.json | Prompt capture needs hook | UserPromptSubmit hook registered and fires |
| FR-003 | Slash commands via commands/ | Commands must be discoverable | All 5 commands appear in `/help` |
| FR-004 | Local marketplace support | Enable local installation | Can install via `claude plugins install` |

#### Spec Commands (renamed /arch:* → /cs:*)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-010 | `/cs:p` planning command | Project planning with requirements elicitation | Creates project in `docs/spec/active/` |
| FR-011 | `/cs:i` implementation command | Progress tracking and task execution | Updates PROGRESS.md, syncs checkboxes |
| FR-012 | `/cs:s` status command | Portfolio and project status | Lists projects, shows status |
| FR-013 | `/cs:c` close-out command | Archive completed projects | Moves to `docs/spec/completed/`, generates retrospective |
| FR-014 | `/cs:log` prompt toggle | Enable/disable prompt capture | Toggles `.prompt-log-enabled` marker |
| FR-015 | `/cs:migrate` migration command | Move projects from old location | Moves `docs/architecture/` to `docs/spec/` |

#### Worktree Commands (/cs:wt:*)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-016 | `/cs:wt:create` command | Create worktrees with agents | Creates worktree, installs deps, launches agent |
| FR-017 | `/cs:wt:status` command | View worktree status | Shows all worktrees with ports, status |
| FR-018 | `/cs:wt:cleanup` command | Clean up worktrees | Removes worktree, releases ports, updates registry |
| FR-019 | Skill trigger phrases | Natural language activation | "spin up worktrees", "worktree status" etc. work |

#### Parallel Agent Directives (from ARCH-2025-12-12-001)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-020 | Parallel execution directive in commands | Enforce parallel specialist usage | Commands contain `<parallel_execution_directive>` block |
| FR-021 | Task template with Agent field | Track agent assignments | IMPLEMENTATION_PLAN.md template has `- **Agent**:` |
| FR-022 | Phase Summary with Lead Agent | Phase-level visibility | Table includes Lead Agent, Parallel Agents columns |
| FR-023 | Named research agents | Replace "Subagent 1" labels | Research uses `code-reviewer`, `research-analyst`, etc. |
| FR-024 | Document sync enforcement | Fix checkbox/status update bug | `<sync_enforcement>` block in `/cs:i` |

#### Worktree Manager Migration

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-030 | All scripts migrated | Full worktree functionality | `allocate-ports.sh`, `cleanup.sh`, etc. work |
| FR-031 | SKILL.md as embedded documentation | Skill triggers still work | Trigger phrases documented in README |
| FR-032 | Config.json bundled | Configurable behavior | Terminal, shell, ports configurable |
| FR-033 | Registry operations work | Global worktree tracking | `~/.claude/worktree-registry.json` operations work |
| FR-034 | Attribution in documentation | Credit original work | README notes worktree-manager origin |

#### Prompt Capture

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-040 | Standalone hook (not hookify patch) | Avoid patch fragility | Hook in plugin's hooks.json |
| FR-041 | Filter pipeline included | Privacy protection | Filters bundled in plugin |
| FR-042 | PROMPT_LOG.json writing | Capture prompts | Logs written to project directory |

#### Dynamic Integration

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-050 | Read agent catalog from host | Use existing agents | Commands reference `~/.claude/agents/` |
| FR-051 | CLAUDE.md compatibility | No duplicate agent defs | Plugin doesn't bundle agents |

#### Migration Support

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-060 | `/cs:migrate` command | Move old projects | Moves `docs/architecture/` → `docs/spec/` |
| FR-061 | Migration preserves history | No data loss | All files, git history preserved |
| FR-062 | Updates CLAUDE.md references | Clean transition | Updates /arch: → /cs: in docs |

### Should Have (P1)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-101 | Agent utilization stats in `/cs:s` | Track agent usage | Status shows agent assignment counts |
| FR-102 | RETROSPECTIVE.md agent notes | Learn from agent effectiveness | Template prompts for agent feedback |
| FR-103 | Worktree init for `/cs:p` projects | Enable prompt capture | Creates logging infrastructure before launch |

### Nice to Have (P2)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-201 | Plugin marketplace publication | Public distribution | Listed on Claude Code marketplace |
| FR-202 | Auto-upgrade from /arch to /cs | Smooth migration | Detects old commands, suggests upgrade |
| FR-203 | Plugin settings UI | User-friendly config | Settings editable via claude command |

## Non-Functional Requirements

### Performance

- Plugin load time < 100ms
- Hook execution < 5 seconds
- No impact on non-spec Claude operations

### Maintainability

- Single source of truth for all spec workflow code
- Clear directory structure mirroring functionality
- Version-controlled with semantic versioning

### Security

- No secrets in plugin code
- Prompt filters protect sensitive data
- No network calls except when explicitly requested

## Technical Constraints

- Must use Claude Code plugin API (hooks.json, commands/)
- No runtime code modifications
- Must work with existing `~/.claude/agents/` structure
- Must support macOS (primary), Linux (secondary)

## Naming Decisions

| Element | Decision | Notes |
|---------|----------|-------|
| Plugin name | `claude-spec` | Matches command prefix |
| Command prefix | `/cs:*` | Short for claude-spec |
| Worktree commands | `/cs:wt:create`, `/cs:wt:status`, `/cs:wt:cleanup` | Full descriptive names |
| Worktree triggers | Keep skill triggers | "spin up worktrees" etc. still work |
| Project directory | `docs/spec/active/` | New location (was `docs/architecture/active/`) |
| Migration | `/cs:migrate` command | One-time script to move old projects |
| Legacy aliases | None | Clean break, no `/arch:*` aliases |
| Prompt log file | `.prompt-log.json` | Hidden file in project dir |
| Capture marker | `.prompt-log-enabled` | Keep current name |

## Plugin Structure

```
claude-spec/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/
│   └── cs/
│       ├── p.md                 # Planning command
│       ├── i.md                 # Implementation command
│       ├── s.md                 # Status command
│       ├── c.md                 # Close-out command
│       ├── log.md               # Prompt log toggle
│       ├── migrate.md           # Migration from /arch:*
│       └── wt/
│           ├── create.md        # Create worktrees
│           ├── status.md        # Worktree status
│           └── cleanup.md       # Cleanup worktrees
├── hooks/
│   ├── hooks.json               # Hook registration
│   └── prompt_capture.py        # Prompt capture hook
├── filters/
│   ├── __init__.py
│   ├── pipeline.py
│   ├── log_entry.py
│   └── log_writer.py
├── worktree/
│   ├── scripts/
│   │   ├── allocate-ports.sh
│   │   ├── cleanup.sh
│   │   ├── launch-agent.sh
│   │   ├── register.sh
│   │   ├── release-ports.sh
│   │   └── status.sh
│   ├── templates/
│   │   └── worktree.json
│   ├── config.json
│   └── SKILL.md                 # Embedded skill documentation
├── templates/
│   ├── REQUIREMENTS.md
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── PROGRESS.md
│   ├── DECISIONS.md
│   ├── RESEARCH_NOTES.md
│   ├── CHANGELOG.md
│   └── RETROSPECTIVE.md
├── README.md
├── CHANGELOG.md
└── LICENSE
```

## Dependencies

### Internal Dependencies

- Host's `~/.claude/agents/` directory
- Host's CLAUDE.md (for agent catalog reference)
- Host's `~/.claude/worktree-registry.json`

### External Dependencies

- Claude Code plugin runtime
- Git (for worktree operations)
- Python 3 (for hooks)
- jq (for registry operations)
- Terminal app (iTerm2/Ghostty/tmux per config)

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Plugin API changes | Medium | High | Pin to known-working Claude Code version |
| Agent catalog format changes | Low | Medium | Abstract agent lookup logic |
| Worktree registry conflicts | Medium | Medium | Add locking mechanism |
| Hook execution failures | Medium | Low | Graceful degradation (log but don't block) |

## Migration Path

### For Existing Users

1. Install claude-spec plugin
2. Run `/cs:migrate` to move `docs/architecture/` → `docs/spec/`
3. Migration script updates CLAUDE.md references from `/arch:*` to `/cs:*`
4. Old `/arch:*` commands no longer work (clean break)
5. All existing project data preserved in new location

### For New Users

1. Install claude-spec plugin
2. Use `/cs:*` commands directly
3. Projects created in `docs/spec/active/`

## Open Questions

- [ ] Should we support Windows (WSL)?
- [ ] Plugin auto-update strategy?
- [ ] Telemetry/usage analytics (opt-in)?

## Appendix

### Command Mapping

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `/arch:p` | `/cs:p` | Planning |
| `/arch:i` | `/cs:i` | Implementation |
| `/arch:s` | `/cs:s` | Status |
| `/arch:c` | `/cs:c` | Close-out |
| `/arch:log` | `/cs:log` | Prompt capture toggle |

### Incorporated from ARCH-2025-12-12-001

- FR-000: Worktree prompt logging initialization → FR-103
- FR-000a: Document sync enforcement → FR-024
- FR-000b: Standalone prompt capture plugin → FR-040, FR-041, FR-042
- FR-001 through FR-006: Parallel agent directives → FR-020 through FR-024

### Worktree Manager Attribution

The worktree management functionality is based on the original `~/.claude/skills/worktree-manager/` skill. Full credit and attribution will be maintained in plugin documentation.
