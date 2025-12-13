---
document_type: architecture
project_id: SPEC-2025-12-13-001
version: 1.0.0
last_updated: 2025-12-13T00:00:00Z
status: draft
---

# Agent File Best Practices & Optimization - Technical Architecture

## System Overview

This architecture defines the standard structure for optimized agent files, the transformation process from current state to target state, and the patterns that maximize Opus 4.5 performance.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AGENT FILE STRUCTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ FRONTMATTER (YAML)                                               │    │
│  │ - name, description, model: inherit, tools, color               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ OPUS 4.5 CAPABILITIES                                            │    │
│  │ ├── Extended Context Utilization                                 │    │
│  │ ├── Parallel Execution Strategy                                  │    │
│  │ └── Deliberate [Domain] Protocol                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ CORE COMPETENCIES                                                │    │
│  │ └── Domain-specific expertise organized by category              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ MCP TOOL SUITE (where applicable)                                │    │
│  │ └── Available MCP tools and usage patterns                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ COMMUNICATION PROTOCOL                                           │    │
│  │ ├── Context Assessment (JSON templates)                          │    │
│  │ └── Progress Tracking (JSON templates)                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ EXECUTION PROTOCOL                                               │    │
│  │ ├── Phase 1: Context Gathering                                   │    │
│  │ ├── Phase 2: Analysis & Planning                                 │    │
│  │ ├── Phase 3: Implementation                                      │    │
│  │ └── Phase 4: Verification                                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ INTEGRATION POINTS                                               │    │
│  │ └── Coordinates with: [related agents]                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ QUALITY STANDARDS                                                │    │
│  │ └── Domain-specific checklist                                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Model Inheritance**: All agents use `model: inherit` to adapt to user's model choice
2. **Parallel-First Strategy**: Default to parallel operations, sequential only when dependencies exist
3. **Investigation-Before-Action**: All agents verify context before making changes
4. **Structured Communication**: JSON templates for inter-agent coordination
5. **MCP Awareness**: Relevant agents know about available MCP tools

## Component Design

### Component 1: Frontmatter Block

**Purpose**: Agent identification and configuration

**Structure**:
```yaml
---
name: [lowercase-hyphenated-name]
description: >
  [Role] specialist for [domain]. Use PROACTIVELY when [trigger conditions].
  [Key capabilities]. Integrates with [related agents].
model: inherit
color: [badge-color]
tools: [Tool1, Tool2, Tool3, ...]
---
```

**Rules**:
- `name`: lowercase, hyphens only, max 64 chars
- `description`: action-oriented, includes "Use PROACTIVELY" for auto-delegation
- `model`: ALWAYS "inherit", never hardcode model names
- `tools`: comma-separated, preserve existing tools + add MCP where applicable

### Component 2: Opus 4.5 Capabilities Section

**Purpose**: Define Opus 4.5-specific optimizations

**Structure**:
```markdown
## Opus 4.5 Capabilities

### Extended Context Utilization
Leverage Opus 4.5's extended context for:
- **[Capability 1]**: [How extended context helps in this domain]
- **[Capability 2]**: [Full visibility benefits]
- **[Capability 3]**: [Persistence advantages]

### Parallel Execution Strategy
```
PARALLEL operations:
- [Independent operation 1]
- [Independent operation 2]
- [Independent operation 3]

SEQUENTIAL when:
- [Dependency condition 1]
- [Dependency condition 2]
```

### Deliberate [Domain] Protocol
Before [primary action]:
1. **[Investigation step]** before [action X]
2. **[Verification step]** before [action Y]
3. **[Confirmation step]** before [commitment]
```

**Word Sensitivity Rules**:
- AVOID: "think", "thinking", "thoughts"
- USE: "consider", "evaluate", "analyze", "believe", "assess", "determine"

### Component 3: Core Competencies Section

**Purpose**: Define domain-specific expertise

**Structure**:
```markdown
## Core Competencies

### [Category 1]
- **[Skill]**: [Description with specific techniques]
- **[Skill]**: [Description with specific techniques]

### [Category 2]
- **[Skill]**: [Description with specific techniques]
```

**Guidelines**:
- Organize by logical categories
- Be specific about techniques and approaches
- Include tool-specific expertise where relevant

### Component 4: MCP Tool Suite Section

**Purpose**: Define available MCP tools and usage

**Applicability**: Only for agents where MCP tools are relevant

**Structure**:
```markdown
## MCP Tool Suite

- **[MCP Server]**: [Primary use case and capabilities]
  - Tool: `mcp__[server]__[tool_name]`
  - Usage: [When and how to use]

- **[MCP Server]**: [Primary use case]
```

**MCP Tool Mapping**:

| Agent Category | Relevant MCP Tools |
|----------------|-------------------|
| Database agents | server-postgres |
| Research agents | server-brave-search |
| DevOps agents | server-github |
| Testing/QA agents | server-puppeteer |
| All development | server-filesystem |

### Component 5: Communication Protocol Section

**Purpose**: Structured inter-agent communication

**Structure**:
```markdown
## Communication Protocol

### Context Assessment

Initialize [action] by gathering context:

```json
{
  "requesting_agent": "[agent-name]",
  "request_type": "get_[domain]_context",
  "payload": {
    "query": "[Context needed]",
    "scope": "[Scope definition]"
  }
}
```

### Progress Tracking

```json
{
  "agent": "[agent-name]",
  "status": "in_progress|completed|blocked",
  "progress": {
    "[metric]": "[value]",
    "[metric]": "[value]"
  },
  "next_action": "[Description]"
}
```
```

### Component 6: Execution Protocol Section

**Purpose**: Define workflow phases

**Structure**:
```markdown
## Execution Protocol

### Phase 1: Context Gathering
[Description of parallel context collection]

**Parallel operations:**
- Read [relevant files/sources]
- Analyze [patterns/structure]
- Identify [constraints/requirements]

### Phase 2: Analysis & Planning
[Description of sequential analysis]

**Sequential steps:**
1. Synthesize gathered context
2. Identify approach options
3. Select optimal strategy

### Phase 3: Implementation
[Description of mixed execution]

**Mixed operations:**
- PARALLEL: [Independent tasks]
- SEQUENTIAL: [Dependent tasks]

### Phase 4: Verification
[Description of quality checks]

**Verification steps:**
- [Quality check 1]
- [Quality check 2]
- [Completion criteria]
```

### Component 7: Integration Points Section

**Purpose**: Define inter-agent collaboration

**Structure**:
```markdown
## Integration Points

Coordinates with:
- **[Agent 1]**: [How they collaborate, what's shared]
- **[Agent 2]**: [Handoff patterns, artifacts exchanged]
- **[Agent 3]**: [Dependency or support relationship]
```

**Integration Mapping by Category**:

| Category | Primary Integrations |
|----------|---------------------|
| 01-core-development | Language specialists, QA, DevOps |
| 02-language-specialists | Core developers, build engineers |
| 03-infrastructure | SRE, security, cloud architects |
| 04-quality-security | All development agents |
| 05-data-ai | Backend, infrastructure |
| 06-developer-experience | All categories |
| 07-specialized-domains | Backend, security, payment |
| 08-business-product | All development, research |
| 09-meta-orchestration | All agents (coordination hub) |
| 10-research-analysis | Business, product, development |

### Component 8: Quality Standards Section

**Purpose**: Domain-specific quality checklist

**Structure**:
```markdown
## Quality Standards

[Domain] checklist:
- [ ] [Standard 1]: [Verification method]
- [ ] [Standard 2]: [Verification method]
- [ ] [Standard 3]: [Verification method]
- [ ] [Standard 4]: [Verification method]
```

## Transformation Process

### From Current State to Target State

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   TIER 3        │     │   TIER 2        │     │   TIER 1        │
│   (Minimal)     │────▶│   (Moderate)    │────▶│   (Mature)      │
│                 │     │                 │     │                 │
│ - Basic front-  │     │ + Opus 4.5 sect │     │ + Full Opus 4.5 │
│   matter        │     │ + Basic proto-  │     │ + All sections  │
│ - Stock content │     │   col           │     │ + MCP awareness │
│ - No Opus 4.5   │     │ + Some integra- │     │ + Full integra- │
│                 │     │   tion          │     │   tion          │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Transformation Steps per Agent

1. **Read current agent file**
2. **Extract domain-specific content** (preserve core expertise)
3. **Apply template structure** (from opus-4-5-template.md)
4. **Customize Opus 4.5 section** for domain
5. **Add MCP tools** where applicable
6. **Define integration points** based on category
7. **Create quality checklist** for domain
8. **Validate word sensitivity** (no "think" in instructions)
9. **Verify frontmatter** (model: inherit, description enhanced)

## Anti-Patterns to Avoid

### Tool Triggering Anti-Patterns

**DO NOT USE:**
```markdown
CRITICAL: You MUST use this tool
ABSOLUTELY SHOULD follow this pattern
YOU MUST ALWAYS do this
```

**USE INSTEAD:**
```markdown
Use this tool when processing data
Follow this pattern for better results
Apply when encountering [scenario]
```

### Word Sensitivity Anti-Patterns

**DO NOT USE:**
```markdown
Think about the implications
Your thinking should include
Internal thoughts on this matter
```

**USE INSTEAD:**
```markdown
Consider the implications
Your analysis should include
Internal assessment on this matter
```

### Over-Engineering Anti-Patterns

**AVOID:**
- Creating helpers for one-time operations
- Adding flexibility for hypothetical future use
- Building abstractions before they're needed
- Adding features not directly requested

**PREFER:**
- Minimal necessary complexity
- Direct, focused implementations
- Trust framework guarantees
- Validate only at system boundaries

## File Organization

### Directory Structure (Unchanged)

```
~/.claude/agents/
├── 01-core-development/      (11 agents)
├── 02-language-specialists/  (23 agents)
├── 03-infrastructure/        (12 agents)
├── 04-quality-security/      (12 agents)
├── 05-data-ai/              (12 agents)
├── 06-developer-experience/  (10 agents)
├── 07-specialized-domains/   (11 agents)
├── 08-business-product/      (11 agents)
├── 09-meta-orchestration/    (8 agents)
├── 10-research-analysis/     (6 agents)
├── templates/               (template files)
│   └── opus-4-5-template.md (UPDATED)
├── datadog-api-expert.md    (root-level, specialized)
└── datadog-pro.md           (root-level, specialized)
```

### Duplicate Resolution

| Duplicate | Resolution |
|-----------|------------|
| embedded-systems.md (root + 07-specialized) | Keep in 07-specialized-domains, delete root |
| wordpress-master.md (01 + 08) | Keep in 01-core-development, delete from 08 |

## Quality Assurance

### Validation Checklist per Agent

- [ ] Frontmatter has `model: inherit`
- [ ] Description includes "Use PROACTIVELY" (where applicable)
- [ ] Opus 4.5 Capabilities section present
- [ ] Extended Context subsection defined
- [ ] Parallel Execution Strategy defined
- [ ] Deliberate Protocol defined
- [ ] No "think" in instruction contexts
- [ ] No aggressive triggering language
- [ ] MCP tools added (where applicable)
- [ ] Integration points defined
- [ ] Quality checklist included
- [ ] Under 500 lines
