---
document_type: requirements
project_id: SPEC-2025-12-13-001
version: 1.0.0
last_updated: 2025-12-13T00:00:00Z
status: draft
---

# Agent File Best Practices & Optimization - Product Requirements Document

## Executive Summary

Optimize all 116 agent files in `~/.claude/agents/` to leverage Opus 4.5's full capabilities, including extended context utilization, parallel execution strategies, subagent orchestration, and MCP tool awareness. This clean-slate optimization will transform agents from varying maturity levels (18 Mature, 61 Moderate, 22 Minimal) into exceptional AI development compatriots following Anthropic's latest best practices.

## Problem Statement

### The Problem
Current agent files do not take full advantage of Opus 4.5's latest improvements. Most agents (83%) lack:
- Opus 4.5-specific capability sections
- Parallel execution strategies
- Deliberate investigation-before-action protocols
- MCP tool awareness
- Proper word sensitivity (avoiding "think" when extended thinking disabled)
- Integration patterns with other agents

### Impact
- Suboptimal agent performance and accuracy
- Missed opportunities for parallel execution
- Inconsistent agent invocation and delegation
- Underutilization of extended context capabilities
- Poor coordination between specialist agents

### Current State
- 18 agents (15.5%) at Tier 1 (Mature) with full Opus 4.5 support
- 61 agents (52.6%) at Tier 2 (Moderate) with basic patterns
- 22 agents (19%) at Tier 3 (Minimal) with stock templates
- 2 duplicate agent files requiring consolidation
- Inconsistent frontmatter and structure across categories

## Goals and Success Criteria

### Primary Goal
Transform all 116 agent files into Tier 1 (Mature) status with comprehensive Opus 4.5 optimization, following Anthropic's official best practices and the `/cs:p` gold standard structure.

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Tier 1 agents | 100% (116 agents) | Structural audit against template |
| Opus 4.5 sections present | 100% | Grep for "## Opus 4.5 Capabilities" |
| Parallel execution defined | 100% | Grep for "PARALLEL operations" |
| MCP tool awareness | 100% applicable | Per-agent relevance check |
| Word sensitivity compliance | 100% | No "think" in non-thinking contexts |
| Integration patterns | 100% | Cross-agent references documented |
| Duplicates resolved | 0 | File inventory check |

### Non-Goals (Explicit Exclusions)
- Creating new agents (only optimizing existing ones)
- Changing agent tool access (preserve existing tool lists unless MCP additions)
- Modifying agent directory structure (keep 10 categories)
- Changing agent naming conventions

## User Analysis

### Primary Users
- **Who**: Claude Code users leveraging the Task tool with specialist subagents
- **Needs**: Reliable, high-performance agents that maximize Opus 4.5 capabilities
- **Context**: Multi-agent orchestration for complex software engineering tasks

### User Stories
1. As a developer, I want agents to leverage Opus 4.5's extended context so that complex codebases are fully understood
2. As a developer, I want agents to execute tasks in parallel where possible so that work completes faster
3. As a developer, I want agents to investigate before acting so that changes are accurate and targeted
4. As a developer, I want agents to coordinate with each other so that complex tasks are handled seamlessly
5. As a developer, I want agents to utilize MCP tools so that external services are properly integrated

## Functional Requirements

### Must Have (P0)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-001 | Add Opus 4.5 Capabilities section to all agents | Core optimization goal | Section present with Extended Context, Parallel Execution, Deliberate Protocol |
| FR-002 | Update frontmatter to use `model: inherit` | Ensures model flexibility | All agents use `inherit`, none hardcode model names |
| FR-003 | Replace "think" with Opus 4.5-safe alternatives | Word sensitivity compliance | No occurrences of "think" in instruction contexts |
| FR-004 | Remove aggressive tool triggering language | Prevents over-triggering | No "CRITICAL: MUST", "ABSOLUTELY SHOULD" patterns |
| FR-005 | Add parallel execution strategy section | Enables efficient multi-operation | PARALLEL/SEQUENTIAL blocks defined per agent |
| FR-006 | Add deliberate investigation protocol | Ensures accuracy | "Before [action]" protocol with numbered steps |
| FR-007 | Consolidate duplicate agents | Clean inventory | embedded-systems and wordpress-master resolved |
| FR-008 | Update all version references | Current best practices | References to current tooling, frameworks |

### Should Have (P1)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-101 | Add MCP tool awareness where applicable | Extended capabilities | MCP Tool Suite section for relevant agents |
| FR-102 | Add integration patterns section | Multi-agent coordination | "Coordinates with" section listing related agents |
| FR-103 | Add communication protocol | Structured interaction | JSON query/response templates where applicable |
| FR-104 | Add quality standards checklist | Consistent outcomes | Domain-specific checklist per agent |
| FR-105 | Enhance descriptions for auto-delegation | Better invocation | "Use PROACTIVELY" in descriptions |

### Nice to Have (P2)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-201 | Add execution phase breakdown | Clear workflow | 4-phase protocol (Context, Analysis, Implementation, Verification) |
| FR-202 | Add progress tracking JSON templates | State management | Standard JSON format for status updates |
| FR-203 | Add domain-specific examples | Clearer guidance | Example inputs/outputs per agent domain |

## Non-Functional Requirements

### Performance
- Agent invocation overhead: No increase from current baseline
- File size: Keep under 500 lines per agent for readability

### Maintainability
- Consistent structure across all agents
- Clear section demarcation with markdown headers
- Comments explaining non-obvious patterns

### Compatibility
- Backward compatible with existing Task tool invocations
- Works with both Opus 4.5 and fallback to other models
- Preserves existing tool access patterns

## Technical Constraints
- Must maintain markdown format (.md files)
- Must preserve YAML frontmatter structure
- Must work with Claude Code's agent discovery mechanism
- File locations must remain in `~/.claude/agents/` hierarchy

## Dependencies

### Internal Dependencies
- Existing agent file inventory (116 files)
- Template file at `agents/templates/opus-4-5-template.md`
- Include files at `~/.claude/includes/opus-4-5*.md`

### External Dependencies
- Anthropic documentation for best practices
- Claude Code subagent specification

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing agent invocations | Low | High | Preserve tool lists and core competencies |
| Inconsistent application of patterns | Medium | Medium | Use template-driven generation |
| Missing domain-specific nuances | Medium | Medium | Review each agent individually, not batch |
| Over-engineering simple agents | Medium | Low | Apply minimal necessary complexity principle |

## Open Questions
- [x] Which agent is the gold standard? → `/cs:p` planning command
- [x] Should MCP tools be added to all agents? → Only where applicable
- [x] Clean slate or preserve backward compatibility? → Clean slate with preserved tool lists

## Appendix

### Glossary

| Term | Definition |
|------|------------|
| Opus 4.5 | Current frontier Claude model (claude-opus-4-5-20251101) |
| Extended Context | Opus 4.5's ability to maintain large context windows |
| MCP | Model Context Protocol for external tool integration |
| Subagent | Specialist agent invoked via Task tool |
| Tier 1/Mature | Agent with full Opus 4.5 optimization |
| Tier 2/Moderate | Agent with basic patterns, partial optimization |
| Tier 3/Minimal | Agent with stock template, needs significant work |

### References
- Research Notes: [RESEARCH_NOTES.md](./RESEARCH_NOTES.md)
- Anthropic Best Practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/
- Claude Code Subagents: https://code.claude.com/docs/en/sub-agents.md
