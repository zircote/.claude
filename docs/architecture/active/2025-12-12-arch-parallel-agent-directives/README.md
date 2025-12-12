---
project_id: ARCH-2025-12-12-001
project_name: "Parallel Agent Directives for /arch Workflows"
slug: arch-parallel-agent-directives
status: superseded
created: 2025-12-12T00:00:00Z
approved: null
started: null
completed: null
expires: 2026-03-12T00:00:00Z
superseded_by: ARCH-2025-12-12-002
tags: [architecture, workflows, parallel-agents, subagents, planning, bug-fix]
stakeholders: []
---

# Parallel Agent Directives for /arch Workflows

> **SUPERSEDED**: This project has been folded into [Architecture Toolkit Plugin](../2025-12-12-arch-toolkit-plugin/README.md) (ARCH-2025-12-12-002). The parallel agent directives will be implemented as a feature of the plugin rather than as standalone command modifications.

## Overview

Enhance the `/arch:*` workflow commands to systematically identify and leverage parallel specialist agents during planning, and embed directives in planning artifacts that ensure Claude always uses these agents in parallel for optimal outcomes.

Also fixes three bugs:
1. Worktree prompt logging not initialized before Claude Code launches
2. Document synchronization not updating checkboxes and status fields
3. Hook configuration preventing prompt capture hook from executing

## Status

**Current Phase**: SUPERSEDED - Merged into Architecture Toolkit Plugin project

## Quick Links

- [Requirements](./REQUIREMENTS.md)
- [Architecture](./ARCHITECTURE.md)
- [Implementation Plan](./IMPLEMENTATION_PLAN.md)
- [Research Notes](./RESEARCH_NOTES.md)
- [Decisions](./DECISIONS.md)
- [Changelog](./CHANGELOG.md)
