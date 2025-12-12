---
document_type: requirements
project_id: ARCH-2025-12-12-002
version: 1.0.0
last_updated: 2025-12-12T21:45:00Z
status: completed
---

# Prompt Capture Log - Product Requirements Document

## Executive Summary

This project implements an automated system to capture, filter, and log all prompts exchanged during architecture planning and development work (`/arch:*` commands). The captured data provides traceability of decision-making, feeds into retrospective analysis, and helps users improve their prompting capabilities over time.

The system uses Claude Code's hook mechanism to intercept prompts at submission time, applies content filtering (profanity and secrets), and writes structured JSON logs to the active architecture project directory. At project close-out, the logs are automatically analyzed to generate insights for the retrospective.

## Problem Statement

### The Problem

When completing architecture planning sessions, there is no record of the actual prompts and interactions that led to the final artifacts. This creates several issues:

1. **No traceability** - Cannot review what was asked to understand how conclusions were reached
2. **No learning loop** - Cannot identify patterns in prompting that led to better or worse outcomes
3. **No retrospective data** - Retrospectives lack quantitative insights about the planning process itself
4. **Repeated mistakes** - Poor prompting patterns are not identified and corrected

### Impact

- Users cannot improve their prompting skills based on past sessions
- Retrospectives miss valuable data about the interaction quality
- No way to reproduce or understand the reasoning behind architectural decisions
- Team knowledge transfer is limited to final artifacts, not the discovery process

### Current State

- `/arch:*` commands create comprehensive planning artifacts (REQUIREMENTS.md, ARCHITECTURE.md, etc.)
- No capture of the prompts that generated these artifacts
- Retrospectives (`RETROSPECTIVE.md`) are generated at `/arch:c` but lack interaction analysis
- UserPromptSubmit hooks exist but are not used for logging

## Goals and Success Criteria

### Primary Goal

Automatically capture all prompts during architecture work sessions, filter sensitive content, and use the data to improve future planning quality through retrospective analysis.

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Prompt capture rate | 100% of /arch:* session prompts | Log entry count vs session interaction count |
| False positive filter rate | <5% legitimate content filtered | Manual review of filtered entries |
| Secret detection rate | 100% of common patterns | Test suite with known secret formats |
| Retrospective insight generation | Automatic for all closed projects | Presence of Interaction Analysis section |

### Non-Goals (Explicit Exclusions)

- Capturing prompts outside of `/arch:*` sessions (unless manually toggled on)
- Real-time analysis or intervention during sessions
- Sharing or syncing logs across users/machines
- Training ML models on captured data
- Capturing Claude's full responses (only summaries)

## User Analysis

### Primary Users

- **Who**: Developers and architects using the `/arch:*` command suite
- **Needs**: Traceability, self-improvement feedback, retrospective data
- **Context**: Architecture planning sessions, typically lasting 30-120 minutes

### User Stories

1. As an architect, I want my prompts logged automatically during `/arch:p` sessions so that I can review my questioning approach later
2. As a developer, I want to see analysis of my prompting patterns in the retrospective so that I can improve my planning skills
3. As a team lead, I want prompt logs included with completed projects so that I can understand how decisions were reached
4. As a user, I want to toggle logging on/off so that I can control when my prompts are captured
5. As a user, I want sensitive content filtered before logging so that secrets and profanity are not committed to git

## Functional Requirements

### Must Have (P0)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-001 | Capture user input on UserPromptSubmit during /arch:* sessions | Core functionality | Every user prompt in /arch:* session appears in PROMPT_LOG.json |
| FR-002 | Capture expanded slash command prompts | Traceability of full context | /arch:p template content logged alongside user input |
| FR-003 | Capture Claude response summaries | Complete interaction record | Summary of each Claude response logged |
| FR-004 | Filter profanity from logged content | Commit safety | Known profanity replaced with [FILTERED] |
| FR-005 | Filter secrets/tokens from logged content | Security | API keys, passwords, tokens detected and replaced |
| FR-006 | Write logs to PROMPT_LOG.json in active project directory | Project association | Log file created in docs/architecture/active/[project]/ |
| FR-007 | Implement /arch:log on\|off toggle command | User control | Command enables/disables logging, persists across sessions |
| FR-008 | Auto-disable logging after /arch:c completes | Clean lifecycle | Logging stops when retrospective is generated |
| FR-009 | Analyze logs and generate insights for RETROSPECTIVE.md | Value delivery | Interaction Analysis section added to retrospective |
| FR-010 | Move PROMPT_LOG.json with project to completed/ | Archive integrity | Log file moves with other artifacts at close-out |

### Should Have (P1)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-101 | Track session boundaries in log | Analysis clarity | Entries grouped by session_id with start/end markers |
| FR-102 | Include timestamp for each entry | Temporal analysis | ISO 8601 timestamp on every log entry |
| FR-103 | Detect and warn on high clarification count | Quality signal | Analysis flags sessions with >10 clarifying questions |
| FR-104 | Support manual log review command | Debugging | /arch:log show displays recent entries |

### Nice to Have (P2)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-201 | Configurable profanity word list | Customization | User can add/remove words via config |
| FR-202 | Configurable secret patterns | Customization | User can add custom regex patterns |
| FR-203 | Export log to markdown format | Readability | Command to generate human-readable log |

## Non-Functional Requirements

### Performance

- Hook execution must add <100ms latency to prompt submission
- Log writes must be asynchronous to avoid blocking user input
- JSON parsing must handle logs up to 10MB without degradation

### Security

- Secrets must be detected before writing to disk (never written in cleartext)
- Profanity filter must run before any disk I/O
- Log files should have standard file permissions (644)

### Reliability

- Hook failures must not block user interaction (fail-open)
- Partial writes must not corrupt existing log data (atomic append)
- Missing project directory must not crash hook (graceful skip)

### Maintainability

- Hook code must be well-documented with clear extension points
- Filter patterns must be externalized for easy updates
- Test coverage >80% for filter logic

## Technical Constraints

### Technology Stack

- **Language**: Python (matching existing hookify plugin)
- **Hook mechanism**: Claude Code UserPromptSubmit hook
- **Log format**: JSON (NDJSON for append efficiency)
- **Profanity filtering**: Custom word list (portable, no npm dependency)
- **Secret detection**: Regex patterns from gitleaks project

### Integration Requirements

- Must integrate with existing hookify plugin infrastructure
- Must respect existing `/arch:*` command conventions
- Must not modify Claude Code core (hook-only implementation)

### Compatibility Requirements

- Must work on macOS (primary development environment)
- Should work on Linux (CI/deployment environments)
- Python 3.8+ required

## Dependencies

### Internal Dependencies

- hookify plugin (`~/.claude/plugins/cache/claude-code-plugins/hookify/`)
- `/arch:*` command suite (`~/.claude/commands/arch/`)
- Architecture project directory structure (`docs/architecture/`)

### External Dependencies

- Python 3.8+ (standard library only for core functionality)
- Optional: `@2toad/profanity` patterns (adapted for Python)

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Hook latency affects UX | Medium | Medium | Async writes, performance testing |
| False positive secret detection | Medium | Low | Configurable patterns, whitelist support |
| Log file grows too large | Low | Medium | Session-based rotation, size limits |
| Sensitive data leaks past filter | Low | High | Multiple filter passes, conservative patterns |
| Hook breaks on Claude Code update | Medium | High | Version pinning, graceful degradation |

## Open Questions

- [x] Should Claude's responses be captured? → **Yes, as summaries**
- [x] What triggers capture start? → **Any /arch:* command when logging enabled**
- [x] Where are logs stored? → **Project directory, moves with lifecycle**
- [ ] How are response summaries generated? → TBD in architecture phase
- [ ] What analysis metrics are most valuable? → TBD based on initial usage

## Appendix

### Glossary

| Term | Definition |
|------|------------|
| UserPromptSubmit | Claude Code hook event fired when user submits a prompt |
| PROMPT_LOG.json | JSON file containing captured prompts and metadata |
| Expanded prompt | The full template content after slash command expansion |
| Response summary | Condensed version of Claude's response for logging |

### References

- [hookify plugin documentation](~/.claude/plugins/cache/claude-code-plugins/hookify/)
- [gitleaks secret patterns](https://github.com/gitleaks/gitleaks)
- [Claude Code hooks documentation](https://docs.anthropic.com/claude-code/hooks)
