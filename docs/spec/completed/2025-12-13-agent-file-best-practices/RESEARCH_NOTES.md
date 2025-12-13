---
document_type: research
project_id: SPEC-2025-12-13-001
last_updated: 2025-12-13T00:00:00Z
---

# Agent File Best Practices & Optimization - Research Notes

## Research Summary

Comprehensive research conducted via 5 parallel specialist agents covering Anthropic official documentation, Claude Code guide, existing agent inventory analysis, MCP tools discovery, and Opus 4.5 optimization patterns. Key finding: Current agent files are at varying maturity levels (18 Mature, 61 Moderate, 22 Minimal) and most lack Opus 4.5-specific optimizations.

## 1. Anthropic Official Best Practices

### XML Section Structuring

**Official guidance from Anthropic documentation:**

Use semantic XML tags to organize distinct prompt components:

```xml
<background_information>
Context about the user, domain, constraints
</background_information>

<instructions>
1. Clear, numbered steps for the task
2. Specific behavioral guidance
3. Output format expectations
</instructions>

<examples>
<example>
<input>Example input</input>
<output>Expected output</output>
</example>
</examples>

<constraints>
- Boundary conditions
- What NOT to do
- Performance requirements
</constraints>
```

**Benefits:**
- **Clarity**: Prevents mixing instructions with examples
- **Accuracy**: Reduces parsing errors
- **Parseability**: Easier post-processing
- **Flexibility**: Easy to modify sections

### Opus 4.5 Behavioral Differences

| Aspect | Previous Models | Opus 4.5 | Action Required |
|--------|-----------------|----------|-----------------|
| Word sensitivity | N/A | Avoid "think" when extended thinking disabled | Use "consider", "evaluate", "believe" |
| Tool triggering | Needs aggressive prompting | Responds to normal phrasing | Remove "CRITICAL: MUST" patterns |
| Over-engineering | Moderate | Tendency to add extra files | Add explicit constraints |
| Parallel tools | 2-3 | 3-5 efficiently | Build parallel workflows |

### Frontmatter Standards

```yaml
---
name: agent-name              # Required: lowercase, hyphens, max 64 chars
description: "Clear description"   # Required: max 1024 chars, action-oriented
tools: tool1, tool2, tool3    # Optional: comma-separated list
model: inherit                # ALWAYS use 'inherit', never hardcode
permissionMode: default       # Optional: default|acceptEdits|bypassPermissions|plan
---
```

**Description Field Formula:**
```
[Agent role] specialist. [When to use]. Use PROACTIVELY [if intended for auto-delegation].
```

Keywords that trigger auto-delegation:
- "Use PROACTIVELY"
- "Use immediately after"
- "Use to prevent"

## 2. Gold Standard Analysis: /cs:p Planning Command

The `/cs:p` command (1,432 lines) represents the gold standard for agent file structure.

### Key XML Sections Used

1. `<mandatory_first_actions>` - Pre-execution security checks
2. `<role>` - Agent persona definition
3. `<parallel_execution_directive>` - Multi-agent orchestration rules
4. `<artifact_lifecycle>` - Document management system
5. `<worktree_enforcement>` - Git isolation protocols
6. `<initialization_protocol>` - Project setup procedures
7. `<planning_philosophy>` - Core principles
8. `<execution_protocol>` - Six-phase workflow
9. `<quality_gates>` - Validation checklist
10. `<execution_instruction>` - Step-by-step sequence

### Six-Phase Execution Protocol

| Phase | Purpose | Key Components |
|-------|---------|----------------|
| Phase 1 | Socratic Requirements Elicitation | 5 question categories, 7 clarity checkpoints |
| Phase 2 | Research & Context Gathering | 4 parallel subagents, mandatory parallelization |
| Phase 3 | Requirements Documentation | REQUIREMENTS.md with full template |
| Phase 4 | Technical Architecture Design | ARCHITECTURE.md with component design |
| Phase 5 | Implementation Planning | IMPLEMENTATION_PLAN.md with phases |
| Phase 6 | Artifact Finalization | Cross-referencing, status updates |

### Critical Best Practices Embedded

1. **Clarity Before Code** - No implementation until requirements clear
2. **Questions Over Assumptions** - When in doubt, ASK
3. **Research Before Recommendations** - Ground all suggestions in data
4. **Parallel Multi-Agent Research** - Sequential research is a "protocol violation"
5. **Artifact Hygiene** - Every plan has a home, lifecycle, expiration

## 3. Agent Inventory Analysis

### Summary Statistics

- **Total Agents**: 116 (plus templates)
- **Categories**: 10 organized directories
- **Lines per Agent**: 221-339 range
- **Duplicates Found**: 2 (embedded-systems, wordpress-master)

### Maturity Tiers

**TIER 1 - MATURE (18 agents):** Full Opus 4.5 support, comprehensive protocols
- frontend-developer, backend-developer, python-pro, typescript-pro, golang-pro
- javascript-pro, sql-pro, devops-engineer, cloud-architect
- code-reviewer, test-automator, security-auditor, performance-engineer
- data-scientist, documentation-engineer, mcp-developer
- fintech-engineer, api-documenter
- multi-agent-coordinator, workflow-orchestrator, context-manager
- research-analyst

**TIER 2 - MODERATE (61 agents):** Basic Opus 4.5, standard workflow patterns
- Most language specialists (C++, Java, Rust, PHP, C#, Swift, Kotlin)
- Most infrastructure agents
- Data/AI agents (except data-scientist)
- DX agents
- Business/product agents (all 11)

**TIER 3 - MINIMAL (22 agents):** Weak/missing Opus 4.5, stock patterns
- Framework specialists (React, Next.js, Vue, Angular, Django, Spring, Laravel, Rails, Flutter)
- Infrastructure (Kubernetes-specialist, SRE)
- Quality (QA, Pentester, Debugger, Error Detective, Compliance, Chaos)
- Specialized (IoT, Mobile App, Payment Integration)
- Datadog experts (2)

### Structural Patterns Found

**Common Sections (decreasing priority):**
1. Frontmatter
2. Opus 4.5 Capabilities (Tier 1 only)
3. Core Competencies / Expertise
4. Execution Protocol / Workflow
5. Communication Protocol
6. MCP Tool Suite
7. Integration Points / Agent Collaboration
8. Quality Standards / Checklists

**Missing in Tier 2/3:**
- Opus 4.5 Capabilities section
- Parallel execution strategies
- Detailed communication protocols
- MCP tool awareness
- Integration patterns with other agents

### Duplicates Identified

| File | Locations | Action |
|------|-----------|--------|
| embedded-systems.md | Root + 07-specialized-domains | Consolidate to 07-specialized-domains |
| wordpress-master.md | 01-core-development + 08-business-product | Consolidate to most appropriate location |

## 4. MCP Tools Available

### Core MCP Servers (Anthropic Official)

| Server | Purpose | Agent Relevance |
|--------|---------|-----------------|
| `@modelcontextprotocol/server-filesystem` | File system access | All development agents |
| `@modelcontextprotocol/server-postgres` | PostgreSQL operations | Database, backend, data agents |
| `@modelcontextprotocol/server-github` | GitHub repos, issues, PRs | All development, DevOps |
| `@modelcontextprotocol/server-brave-search` | Web search | Research, analysis agents |
| `@modelcontextprotocol/server-puppeteer` | Browser automation | Testing, frontend, QA agents |

### Project-Specific MCP Servers

| Server | Purpose | Integration |
|--------|---------|-------------|
| `mcp-atlassian` | JIRA integration | Project management agents |
| Custom MCP servers | Domain-specific | Per-agent as needed |

### MCP Developer Resources

- **Agent**: `mcp-developer` in 06-developer-experience
- **Skill**: `mcp-builder` for creating new servers
- **Reference**: `~/.claude/includes/mcp-reference.md`

## 5. Opus 4.5 Optimization Patterns

### Word Sensitivity (Critical)

When extended thinking is disabled:
- **AVOID**: "think", "thinking", "thoughts"
- **USE**: "consider", "evaluate", "analyze", "believe", "assess", "determine"

### Tool Triggering Calibration

**Optimal Language:**
```markdown
Use when processing data
Follow this pattern for better results
Apply when encountering [scenario]
```

**Problematic Language (causes over-triggering):**
```markdown
CRITICAL: You MUST use this tool
ABSOLUTELY SHOULD follow this pattern
YOU MUST ALWAYS do this
```

### Subagent Orchestration Pattern

```markdown
<parallel_execution_directive>
PARALLEL operations for this agent:
- [Independent operation 1]
- [Independent operation 2]
- [Independent operation 3]

SEQUENTIAL when:
- [Dependency condition 1]
- [Dependency condition 2]
</parallel_execution_directive>
```

### State Management

**Use structured formats (JSON) for:**
- Test results
- Task status
- Configuration

**Use unstructured text for:**
- Progress notes
- General context
- Reasoning chains

**Use git for:**
- State tracking across sessions
- Checkpoints
- Change logs

### Investigation-Before-Action Protocol

```markdown
Before [taking action]:
1. **Read referenced files** before making claims
2. **Understand existing patterns** before adding new implementations
3. **Verify assumptions** before proceeding
```

### Context Efficiency

- Do not stop tasks early due to token budget concerns
- Complete tasks fully, even if approaching budget limit
- Save progress and state before context refresh
- Unlimited context through automatic summarization

## 6. Recommended Agent File Structure

Based on research, the optimal agent file structure should be:

```markdown
---
name: [agent-name]
description: >
  [Role] specialist for [domain]. Use PROACTIVELY when [trigger conditions].
  Capabilities: [key capabilities]. Integrates with [related agents].
model: inherit
color: [color]
tools: [Tool1, Tool2, Tool3, ...]
---

## Opus 4.5 Capabilities

### Extended Context Utilization
- **[Capability 1]**: [How Opus 4.5 extended context helps]
- **[Capability 2]**: [How full visibility improves outcomes]

### Parallel Execution Strategy
```
PARALLEL operations:
- [Independent task 1]
- [Independent task 2]

SEQUENTIAL when:
- [Dependency 1]
- [Dependency 2]
```

### Deliberate [Domain] Protocol
Before [primary action]:
1. **[Investigation step]** before [action]
2. **[Verification step]** before [commitment]

## Core Competencies

[Domain-specific expertise organized by category]

## MCP Tool Suite

- **[Tool]**: [Purpose and usage pattern]

## Communication Protocol

### Context Assessment
```json
{
  "requesting_agent": "[agent-name]",
  "request_type": "[request-type]",
  "payload": {}
}
```

### Progress Tracking
```json
{
  "agent": "[agent-name]",
  "status": "[status]",
  "progress": {}
}
```

## Execution Protocol

### Phase 1: Context Gathering
[Parallel operations for initial understanding]

### Phase 2: Analysis & Planning
[Sequential analysis based on gathered context]

### Phase 3: Implementation
[Mixed parallel/sequential execution]

### Phase 4: Verification
[Quality checks and completion criteria]

## Integration Points

Coordinates with:
- **[Agent 1]**: [Collaboration pattern]
- **[Agent 2]**: [Data/artifact sharing]

## Quality Standards

[Domain] checklist:
- [ ] [Standard 1]
- [ ] [Standard 2]
```

## Sources

- Anthropic Prompt Engineering: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/
- Claude Code Subagents: https://code.claude.com/docs/en/sub-agents.md
- Anthropic Multi-Agent Research: https://www.anthropic.com/engineering/multi-agent-research-system
- Claude 4.5 Best Practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices
- Internal files: ~/.claude/includes/opus-4-5.md, ~/.claude/includes/opus-4-5-agent.md
