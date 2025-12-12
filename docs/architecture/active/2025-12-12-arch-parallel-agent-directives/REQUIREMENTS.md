---
document_type: requirements
project_id: ARCH-2025-12-12-001
version: 1.0.0
last_updated: 2025-12-12
status: draft
---

# Parallel Agent Directives for /arch Workflows - Product Requirements Document

## Executive Summary

The `/arch:*` workflow commands currently execute work sequentially when parallel specialist agent execution would significantly reduce execution time and improve output quality. Despite having access to 121 specialist agents across 10 categories, the workflow prompts do not systematically identify, assign, or enforce the use of these agents.

This project enhances the `/arch:*` suite to:
1. Identify appropriate specialist agents during planning
2. Embed explicit agent assignments in planning artifacts
3. Enforce parallel execution through directive language in command prompts
4. Maintain quality through dependency-aware execution

## Problem Statement

### The Problem

The current `/arch:*` workflows treat Claude as a single executor performing tasks sequentially, rather than as an orchestrator dispatching work to specialized agents in parallel. This results in:

1. **Unnecessary execution time**: Sequential task completion when independent tasks could run concurrently
2. **Suboptimal expertise**: Generic Claude responses instead of domain-expert agent responses
3. **Inconsistent agent usage**: Hit-or-miss use of specialists depending on Claude's discretion
4. **Wasted capability**: 121 specialist agents available but rarely leveraged

### Impact

- **Time**: Architecture planning that could complete in one session takes multiple
- **Quality**: Generalist responses instead of specialist expertise
- **Consistency**: No predictable agent orchestration pattern
- **User frustration**: Observing sequential work when parallel is obviously appropriate

### Current State

The `/arch:p` command has a Phase 2 "Research and Context Gathering" that mentions "4 parallel subagents" but:
- Uses generic labels ("Subagent 1", "Subagent 2") not named specialists
- Does not specify `subagent_type` parameters for Task tool calls
- Does not track which agents performed which work
- IMPLEMENTATION_PLAN.md has an `Assignee` field but it's always "TBD"

## Goals and Success Criteria

### Primary Goal

Transform `/arch:*` workflows from sequential single-executor to parallel multi-agent orchestrator, with explicit agent assignments embedded in all planning artifacts.

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Agent assignment coverage | 100% of tasks have assigned agents | Audit IMPLEMENTATION_PLAN.md |
| Parallel execution rate | 80%+ of independent tasks run in parallel | Observe Task tool call patterns |
| Specialist utilization | Named agents used vs generic "Explore" | Review subagent_type values |
| Planning time reduction | 40% faster completion | Compare session durations |

### Non-Goals (Explicit Exclusions)

- **New agents**: This project does not create new agents; it leverages existing 121 agents
- **UI changes**: No changes to Claude Code interface
- **Runtime enforcement**: No code changes to enforce at runtime; enforcement is via prompt directives
- **CLAUDE.md restructuring**: Minimal updates to document the enhancement

## User Analysis

### Primary Users

- **Who**: Claude instances executing `/arch:*` commands
- **Needs**: Clear directives on which agents to use and when to parallelize
- **Context**: Architecture planning and implementation tracking sessions

### Secondary Users

- **Who**: Developers reviewing planning artifacts
- **Needs**: Visibility into which agents performed which tasks
- **Context**: Code review, retrospectives, debugging

### User Stories

1. As Claude executing `/arch:p`, I want explicit agent assignments in the IMPLEMENTATION_PLAN.md template so that I know exactly which specialist to invoke for each task.

2. As Claude executing `/arch:i`, I want enforcement language in my prompt that mandates parallel Task tool calls for independent tasks so that I consistently use parallel execution.

3. As a developer reviewing a planning artifact, I want to see which agents were assigned to each phase/task so that I understand the expertise that contributed to each component.

4. As Claude executing research phases, I want named specialist agents (research-analyst, code-reviewer) instead of generic "Subagent 1" labels so that the right expertise is applied.

## Functional Requirements

### Must Have (P0)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-000 | Worktree creation initializes prompt logging infrastructure BEFORE launching Claude Code | Prompt capture hooks fail if marker/log files don't exist when Claude starts | Worktree script creates `.prompt-log-enabled` and `PROMPT_LOG.json` in project directory before calling launch-agent.sh |
| FR-000a | Document synchronization updates checkboxes and status fields during transitions | Checkboxes in IMPLEMENTATION_PLAN.md and status fields in README.md frontmatter are not being updated when tasks complete or phases transition | `/arch:i` explicitly updates: (1) acceptance criteria checkboxes when tasks done, (2) status field in README.md/REQUIREMENTS.md/ARCHITECTURE.md frontmatter, (3) phase deliverable checkboxes |
| FR-000b | Prompt capture as standalone plugin | Multiple hook groups in UserPromptSubmit array causes only first hook to execute; patching hookify is fragile | Create standalone `prompt-capture` plugin with own hook registration; remove hookify patches |
| FR-001 | IMPLEMENTATION_PLAN.md template includes `Agent` field for each task | Enable task-level agent assignment | Every task template block includes `- **Agent**: [agent-name]` |
| FR-002 | Phase Summary table includes `Lead Agent` column | Enable phase-level visibility | Table header includes `\| Lead Agent \|` |
| FR-003 | `/arch:p` prompt includes explicit parallel execution directive | Enforce parallel Task tool calls | Prompt contains "MUST launch parallel Task tool calls" language |
| FR-004 | `/arch:i` prompt includes parallel execution directive | Enforce parallel implementation | Prompt mandates parallel agent invocation for independent tasks |
| FR-005 | Research phase uses named specialist agents | Replace generic "Subagent 1" labels | Research section specifies `subagent_type="research-analyst"` etc. |
| FR-006 | Agent recommendations section in IMPLEMENTATION_PLAN.md | Guidance on which agents suit which task types | New section mapping task categories to recommended agents |

### Should Have (P1)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-101 | PROGRESS.md includes `Agent` column in Task Status table | Track which agent completed each task | Task Status table has Agent column |
| FR-102 | ARCHITECTURE.md template includes agent attribution | Track which agents designed each component | Component sections note designing agent |
| FR-103 | Dependency-aware parallelization guidance | Prevent incorrect parallelization | Prompt includes "sequential when outputs inform inputs" |
| FR-104 | Agent category quick-reference in planning artifacts | Help identify appropriate agents | Reference table of 10 categories with example agents |

### Nice to Have (P2)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-201 | `/arch:s` shows agent utilization statistics | Portfolio-level agent usage visibility | Status output shows agent assignment counts |
| FR-202 | RETROSPECTIVE.md captures agent performance notes | Learn from agent effectiveness | Template prompts for agent performance feedback |

## Non-Functional Requirements

### Performance

- Parallel execution should reduce end-to-end planning time by 40%+
- No additional latency from agent assignment lookup

### Maintainability

- Agent assignments use exact names from `~/.claude/agents/` directory
- Adding new agents requires no changes to `/arch:*` commands

### Consistency

- All four `/arch:*` commands follow same parallel execution patterns
- Agent naming conventions match existing agent file naming

## Technical Constraints

- **No code changes**: All enforcement via prompt engineering in markdown command files
- **Existing agent catalog**: Must use agents from `~/.claude/agents/` (121 available)
- **Task tool API**: Must use existing `subagent_type` parameter
- **Backward compatibility**: Existing planning artifacts remain valid

## Dependencies

### Internal Dependencies

- `~/.claude/agents/` directory structure (10 categories, 121 agents)
- Task tool with `subagent_type` parameter
- Existing `/arch:*` command files (p.md, i.md, s.md, c.md)

### External Dependencies

- None

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Over-parallelization causing quality issues | Medium | High | Include dependency-awareness language in directives |
| Wrong agent assigned to task | Low | Medium | Include agent category reference; agents can escalate |
| Prompt length increases significantly | Medium | Low | Use concise directive language; reference CLAUDE.md |
| Claude ignores directives | Low | High | Use strong enforcement language ("MUST", "ALWAYS") |

## Open Questions

- [x] ~~Should agent assignments be mandatory or recommended?~~ → Strong enforcement with quality gates
- [x] ~~Phase-level vs task-level granularity?~~ → Both
- [ ] Should we create a dedicated "agent-recommender" agent for suggesting assignments?

## Appendix

### Glossary

| Term | Definition |
|------|------------|
| Specialist Agent | A Claude subagent with domain-specific prompt engineering from `~/.claude/agents/` |
| subagent_type | Task tool parameter specifying which agent definition to use |
| Parallel execution | Launching multiple Task tool calls in a single response |
| Lead Agent | Primary specialist responsible for a phase |

### Agent Categories Reference

| Category | Directory | Example Agents | Use For |
|----------|-----------|----------------|---------|
| Core Development | `01-core-development/` | frontend-developer, backend-developer, api-designer | Application architecture, UI/UX |
| Language Specialists | `02-language-specialists/` | python-pro, typescript-pro, rust-engineer | Language-specific implementation |
| Infrastructure | `03-infrastructure/` | devops-engineer, kubernetes-specialist, terraform-engineer | Deployment, cloud, CI/CD |
| Quality & Security | `04-quality-security/` | code-reviewer, security-auditor, test-automator | Code review, testing, security |
| Data & AI | `05-data-ai/` | data-scientist, ml-engineer, llm-architect | ML, data pipelines, AI |
| Developer Experience | `06-developer-experience/` | documentation-engineer, cli-developer, mcp-developer | DX tooling, docs |
| Specialized Domains | `07-specialized-domains/` | fintech-engineer, blockchain-developer, game-developer | Domain expertise |
| Business & Product | `08-business-product/` | product-manager, technical-writer, ux-researcher | Product, process |
| Meta-Orchestration | `09-meta-orchestration/` | multi-agent-coordinator, workflow-orchestrator | Complex workflows |
| Research & Analysis | `10-research-analysis/` | research-analyst, competitive-analyst | Research, market intel |

### References

- [CLAUDE.md - Parallel Specialist Subagents section](../../CLAUDE.md)
- [Agent directory structure](~/.claude/agents/)
- [Task tool documentation](system prompt)
