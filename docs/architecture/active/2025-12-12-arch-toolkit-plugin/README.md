---
project_id: ARCH-2025-12-12-002
project_name: "Claude Spec Plugin"
slug: claude-spec-plugin
status: draft
created: 2025-12-12T00:00:00Z
approved: null
started: null
completed: null
expires: 2026-03-12T00:00:00Z
superseded_by: null
tags: [plugin, architecture, workflows, parallel-agents, prompt-capture, worktree-manager]
stakeholders: []
---

# Claude Spec Plugin

## Overview

Extract and consolidate the architecture planning workflow into a standalone, distributable Claude Code plugin. This plugin bundles:

1. **`/cs:*` Commands** (Claude Spec) - Strategic project planning, implementation tracking, status monitoring, and close-out
   - `/cs:p` - Project planning with Socratic requirements elicitation
   - `/cs:i` - Implementation progress tracking
   - `/cs:s` - Status and portfolio monitoring
   - `/cs:c` - Project close-out and archival
   - `/cs:log` - Prompt capture toggle
2. **Prompt Capture** - Logs user prompts during architecture sessions for traceability
3. **Worktree Manager** - Git worktree automation for isolated development environments
   - Attribution: Based on original `~/.claude/skills/worktree-manager/` skill

This is a plugin-first redesign that incorporates the parallel agent directives (from superseded ARCH-2025-12-12-001) as a native feature.

## Goals

- **Distributable**: Installable via Claude Code plugin marketplace
- **Self-contained**: All dependencies bundled within the plugin
- **Parallel-native**: Built-in parallel specialist agent orchestration
- **Dynamic integration**: Reads agent catalog from host's CLAUDE.md
- **Backward compatible**: Supports existing `docs/architecture/active/` projects
- **Extensible**: Foundation for future plugin extractions

## Status

**Current Phase**: Phase 1 - Scaffold (Implementation Started)

## Quick Links

- [Requirements](./REQUIREMENTS.md)
- [Architecture](./ARCHITECTURE.md)
- [Implementation Plan](./IMPLEMENTATION_PLAN.md)
- [Research Notes](./RESEARCH_NOTES.md)
- [Decisions](./DECISIONS.md)
- [Changelog](./CHANGELOG.md)

## Supersedes

- [ARCH-2025-12-12-001: Parallel Agent Directives](../2025-12-12-arch-parallel-agent-directives/README.md) - Requirements and research incorporated into this project
