# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Project initialized as ARCH-2025-12-12-002
- Supersedes ARCH-2025-12-12-001 (Parallel Agent Directives)
- REQUIREMENTS.md with 30+ requirements across plugin infrastructure, commands, worktree management
- DECISIONS.md with 7 ADRs covering key architectural choices

### Naming Decisions Finalized
- Plugin name: `claude-spec`
- Command prefix: `/cs:*`
- Worktree commands: `/cs:wt:create`, `/cs:wt:status`, `/cs:wt:cleanup`
- Project directory: `docs/spec/active/` (was `docs/architecture/active/`)
- Prompt log: `.prompt-log.json` (hidden)
- Migration: `/cs:migrate` command (no legacy aliases)

### Key ADRs
- ADR-001: Custom prompt capture (not Claude Code native logs)
- ADR-002: `/cs:*` command prefix
- ADR-003: No legacy `/arch:*` aliases
- ADR-004: `docs/spec/` directory rename
- ADR-005: Both skill triggers AND explicit worktree commands
- ADR-006: Hidden `.prompt-log.json` file
- ADR-007: Dynamic agent catalog from host's CLAUDE.md

### Incorporated from ARCH-2025-12-12-001
- Parallel agent directives (built into commands)
- Document sync enforcement
- Worktree initialization fix
- Standalone prompt capture plugin architecture
