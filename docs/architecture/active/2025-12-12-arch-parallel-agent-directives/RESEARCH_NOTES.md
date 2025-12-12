---
document_type: research
project_id: ARCH-2025-12-12-001
last_updated: 2025-12-12
---

# Parallel Agent Directives - Research Notes

## Research Summary

Research was conducted using three parallel specialist agents to understand the existing agent catalog, Task tool usage patterns, and artifact templates. Key findings:

1. **Agent Catalog**: 121 specialist agents exist across 10 numbered categories in `~/.claude/agents/`
2. **Task Tool Patterns**: Parallel execution is supported but rarely leveraged with named specialists
3. **Templates**: Existing templates have unused `Assignee` field that can become `Agent`

## Codebase Analysis

### Relevant Files Examined

| File | Purpose | Relevance |
|------|---------|-----------|
| `commands/arch/p.md` | Planning command | Primary modification target |
| `commands/arch/i.md` | Implementation command | Needs parallel directive + sync fix |
| `commands/arch/s.md` | Status command | Optional enhancement |
| `commands/arch/c.md` | Close-out command | Minor updates |
| `~/.claude/agents/` | Agent catalog | Source for specialist names |
| `CLAUDE.md` | Global instructions | Already documents agent categories |

### Existing Patterns Identified

1. **Generic Subagent Pattern** (current):
   ```
   Subagent 1 - Existing Codebase Analysis:
   "Explore the entire codebase..."
   ```
   Problem: No `subagent_type` specified, uses generic Explore agent

2. **Parallel Execution Rules** (documented but not enforced):
   ```
   - When to parallelize: Launch multiple specialists simultaneously
   - Dependency awareness: Only serialize when output informs input
   ```
   Problem: Rules exist in CLAUDE.md but not referenced in commands

3. **Unused Assignee Field**:
   ```
   - **Assignee**: [Role/TBD]
   ```
   Problem: Always set to TBD, never populated with agent names

### Integration Points

- **Task Tool API**: `subagent_type` parameter takes exact agent filename (without .md)
- **Agent Catalog**: Files in `~/.claude/agents/[category]/[name].md`
- **CLAUDE.md Reference**: Existing "Parallel Specialist Subagents" section

## Technical Research

### Best Practices Found

| Topic | Source | Key Insight |
|-------|--------|-------------|
| Parallel execution | Claude Code system prompt | "If multiple tools and no dependencies, make all calls in parallel" |
| Agent naming | Agent catalog inspection | Use exact filename without .md extension |
| Directive language | Opus 4.5 behavior docs | Normal phrasing works; avoid "CRITICAL: MUST" (over-triggering) |

### Recommended Approaches

1. **Directive Block Pattern**: Create reusable `<parallel_execution_directive>` XML block
2. **Named Agent Specification**: `subagent_type="research-analyst"` not generic labels
3. **Parallel Group Notation**: Tasks in same group run together
4. **Quality Gates**: Sequential only when outputs inform inputs

### Anti-Patterns to Avoid

1. **Generic Explore Agent**: Don't use `subagent_type="Explore"` when specialist exists
2. **Sequential Default**: Don't assume sequential; parallel should be default for independent tasks
3. **Over-triggering Language**: Avoid "CRITICAL", "ABSOLUTELY MUST" - normal language works with Opus 4.5

## Agent Catalog Analysis

### Category Distribution

| Category | Count | Key Agents |
|----------|-------|------------|
| 01-core-development | 11 | frontend-developer, backend-developer, api-designer |
| 02-language-specialists | 23 | python-pro, typescript-pro, rust-engineer |
| 03-infrastructure | 12 | devops-engineer, kubernetes-specialist, terraform-engineer |
| 04-quality-security | 12 | code-reviewer, security-auditor, test-automator |
| 05-data-ai | 12 | data-scientist, ml-engineer, llm-architect |
| 06-developer-experience | 10 | documentation-engineer, cli-developer, mcp-developer |
| 07-specialized-domains | 11 | fintech-engineer, blockchain-developer, game-developer |
| 08-business-product | 11 | product-manager, technical-writer, ux-researcher |
| 09-meta-orchestration | 8 | multi-agent-coordinator, workflow-orchestrator |
| 10-research-analysis | 6 | research-analyst, competitive-analyst |

### Agent Selection Heuristics

| Task Domain | Recommended Agent | Fallback |
|-------------|-------------------|----------|
| API design | api-designer | backend-developer |
| Database | postgres-pro | database-administrator |
| Frontend | frontend-developer | react-specialist (if React) |
| Security | security-auditor | penetration-tester |
| Performance | performance-engineer | database-optimizer |
| Research | research-analyst | competitive-analyst |
| Documentation | documentation-engineer | technical-writer |
| Infrastructure | devops-engineer | terraform-engineer |

## Bug Analysis

### Bug 1: Worktree Prompt Logging

**Symptom**: Prompts not captured when starting new worktree
**Root Cause**: Logging infrastructure created AFTER Claude Code launches
**Fix**: Create `.prompt-log-enabled` and `PROMPT_LOG.json` BEFORE launch-agent.sh

### Bug 2: Document Synchronization

**Symptom**: Checkboxes stay unchecked, status stays "draft"
**Root Cause**: `/arch:i` Phase 5 sync logic not being executed
**Fix**: Add explicit `<sync_enforcement>` directive with mandatory sync points

## Open Questions from Research

- [x] Which agents best suit which task types? → Documented in Agent Selection Heuristics
- [x] How to balance parallel vs sequential? → Dependency-based: parallel when independent
- [ ] Should we create auto-assignment based on task keywords? → Future enhancement

## Sources

- Agent catalog exploration: `~/.claude/agents/` directory
- Task tool patterns: `~/.claude/commands/` directory
- IMPLEMENTATION_PLAN template: `commands/arch/p.md` lines 766-890
- Completed project examples: `docs/architecture/completed/*/IMPLEMENTATION_PLAN.md`
