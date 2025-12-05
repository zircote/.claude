# Opus 4.5 Migration Guide

## Overview

This document describes the migration of Claude Code agents, commands, skills, and other components to leverage Opus 4.5 (claude-opus-4-5-20251101) capabilities.

## Migration Status

| Component | Status | Notes |
|-----------|--------|-------|
| **settings.json** | ✅ Complete | `"model": "opus"` maps to Opus 4.5 |
| **Agents** | ✅ Complete | All 119 agents use `model: inherit` |
| **Skills** | ✅ Complete | No model-specific changes needed |
| **Commands** | ✅ Complete | No model-specific changes needed |
| **Plugins** | ✅ Complete | No model-specific changes needed |

## Key Files Created

### 1. Opus 4.5 Agent Include
**Path**: `~/.claude/includes/opus-4-5-agent.md`

Shared instructions for agents to leverage Opus 4.5 capabilities:
- Extended context handling
- Parallel tool execution patterns
- Deliberate thinking protocol
- Minimal engineering principle
- Cleanup discipline

### 2. Opus 4.5 Agent Template
**Path**: `~/.claude/agents/templates/opus-4-5-template.md`

Template for creating new Opus 4.5-optimized agents with:
- Structured frontmatter
- Capability sections
- Execution protocols
- Communication patterns

## Agents Enhanced

### Meta-Orchestration Agents
Located in `~/.claude/agents/09-meta-orchestration/`:
- `multi-agent-coordinator.md` - Full workflow state, cross-agent correlation
- `context-manager.md` - Multi-store visibility, schema context
- `workflow-orchestrator.md` - Full workflow graphs, state machine histories

### Quality-Security Agents
Located in `~/.claude/agents/04-quality-security/`:
- `code-reviewer.md` - Full PR context, parallel analysis tools
- `security-auditor.md` - Complete compliance matrix, multi-cloud visibility
- `test-automator.md` - Full test suite awareness, cross-platform coverage

### Core Development Agents
Located in `~/.claude/agents/01-core-development/`:
- `frontend-developer.md` - Complete component tree, design system awareness
- `backend-developer.md` - Full service architecture, deep schema understanding
- `fullstack-developer.md` - Complete stack visibility, end-to-end type safety
- `api-designer.md` - Complete API surface, cross-service awareness
- `microservices-architect.md` - Full system topology, distributed trace analysis

## Opus 4.5 Capabilities Added

### 1. Extended Context Utilization
Each enhanced agent now includes guidance on leveraging extended context for:
- Maintaining complete system states without fragmentation
- Deep analysis across multiple files and services
- Long-running tasks that persist through context compaction

### 2. Parallel Execution Strategy
Explicit patterns for each agent defining:
- **PARALLEL operations**: Independent tool calls to execute simultaneously
- **SEQUENTIAL operations**: Dependencies requiring ordered execution

### 3. Deliberate Protocol
Investigation-before-action requirements:
- Read files before commenting on them
- Understand existing patterns before adding new ones
- Verify information before reporting findings

## How to Migrate Additional Agents

### Step 1: Add Opus 4.5 Section
Insert after the frontmatter `---`:

```markdown
## Opus 4.5 Capabilities

### Extended Context Utilization
Leverage Opus 4.5's extended context for:
- [Agent-specific context needs]
- [Multi-file/system visibility needs]
- [Long-running task requirements]

### Parallel Execution Strategy
```
PARALLEL operations for this agent:
- [Independent operations list]

SEQUENTIAL when:
- [Dependency conditions]
```

### Deliberate [Domain] Protocol
Before [primary action]:
1. **[Investigation step 1]**
2. **[Investigation step 2]**
3. **[Investigation step 3]**

---
```

### Step 2: Customize for Agent Domain
- Identify agent's primary tools and data sources
- Define which operations can run in parallel
- Specify investigation requirements before action

### Step 3: Reference Include (Optional)
For comprehensive instructions, reference the include:
```markdown
@include opus-4-5-agent.md
```

## Configuration Verification

### Check Current Model
```bash
cat ~/.claude/settings.json | jq '.model'
# Should output: "opus"
```

### Verify Agent Inheritance
```bash
grep -h "^model:" ~/.claude/agents/**/*.md | sort | uniq -c
# All should show: model: inherit
```

## Best Practices

### 1. Use `model: inherit`
Never hardcode model names in agents. Use `model: inherit` to automatically use the model from settings.json.

### 2. Maximize Parallel Tool Calls
When multiple independent pieces of information are needed, request them simultaneously:
```
# Good: Parallel
Read file1, Read file2, Read file3 → Single message with 3 tool calls

# Bad: Sequential
Read file1 → wait → Read file2 → wait → Read file3
```

### 3. Investigate Before Acting
Always read referenced files before making claims about their contents. Never speculate about code you haven't inspected.

### 4. Complete Tasks Fully
Don't stop tasks early due to token budget concerns. Context compaction allows indefinite operation. Persist state to memory before context refresh if approaching limits.

## Troubleshooting

### Agent Not Using Opus 4.5
1. Check `settings.json` has `"model": "opus"`
2. Verify agent uses `model: inherit` (not hardcoded)
3. Restart Claude Code session

### Parallel Calls Not Working
Ensure tool calls are truly independent with no parameter dependencies. If one call's output informs another's parameters, they must be sequential.

## Related Files

- `~/.claude/includes/opus-4-5.md` - System-level Opus 4.5 instructions
- `~/.claude/includes/opus-4-5-agent.md` - Agent-level Opus 4.5 include
- `~/.claude/agents/templates/opus-4-5-template.md` - New agent template
- `~/.claude/CLAUDE.md` - Global instructions referencing Opus 4.5
