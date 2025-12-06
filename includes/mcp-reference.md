# MCP Tools, Skills & Agents Reference

## Specialist Agents
Leverage specialized agents from `~/.claude/agents/` for MCP development:

| Agent | Category | Use For |
|-------|----------|---------|
| `mcp-developer` | 06-developer-experience | MCP server development, tool creation |
| `tooling-engineer` | 06-developer-experience | CLI tools, developer tooling |
| `workflow-orchestrator` | 09-meta-orchestration | Multi-agent workflows, orchestration |

This document provides instructions for discovering and using available MCP tools, skills, and agents at runtime. Since these can change based on configuration, use auto-discovery rather than static lists.

## Auto-Discovery Protocol

### Discovering Available Tools

When you need MCP capabilities, use the `mcp-manager` agent or direct MCP tool discovery:

```
# Use the Task tool with mcp-manager agent
Task(subagent_type="mcp-manager", prompt="List all available MCP tools and their capabilities")
```

### Discovering Available Skills

Skills are listed in the Skill tool's `<available_skills>` section. To discover skills:

1. Check the Skill tool description for `<available_skills>` block
2. Skills are invoked via: `Skill(skill="<skill-name>")`

**Common Skill Categories:**
- **Development**: `frontend-development`, `backend-development`, `databases`
- **DevOps**: `devops`, `chrome-devtools`
- **Media**: `media-processing`, `ai-multimodal`, `canvas-design`
- **Documentation**: `skill-creator`, `engineer-skill-creator`
- **Utilities**: `video-downloader`, `invoice-organizer`, `changelog-generator`

### Discovering Available Agents (Task Tool)

Agents are specialized subprocesses invoked via the Task tool. The available agents are listed in the Task tool description under agent types.

**Agent Categories by Domain:**

#### Development Agents
| Agent | Use Case |
|-------|----------|
| `python-pro` | Python development, debugging, optimization |
| `typescript-pro` | TypeScript/JavaScript development |
| `golang-pro` | Go development |
| `react-specialist` | React component development |
| `frontend-developer` | Frontend development with modern frameworks |
| `backend-developer` | Backend API and service development |
| `fullstack-developer` | Full-stack application development |

#### DevOps & Infrastructure
| Agent | Use Case |
|-------|----------|
| `devops-engineer` | CI/CD, containers, infrastructure |
| `kubernetes-specialist` | Kubernetes deployment and management |
| `terraform-engineer` | Infrastructure as Code |
| `cloud-architect` | Multi-cloud architecture design |
| `sre-engineer` | Site reliability, monitoring, incident response |
| `platform-engineer` | Platform tooling and developer experience |

#### Data & AI
| Agent | Use Case |
|-------|----------|
| `data-engineer` | Data pipelines, ETL, warehousing |
| `data-scientist` | ML models, statistical analysis |
| `ml-engineer` | ML infrastructure, model deployment |
| `database-administrator` | Database optimization, administration |
| `postgres-pro` | PostgreSQL-specific expertise |

#### Quality & Security
| Agent | Use Case |
|-------|----------|
| `code-reviewer` | Code review and quality analysis |
| `test-automator` | Test automation frameworks |
| `security-engineer` | Security implementation and review |
| `penetration-tester` | Security testing (authorized contexts) |
| `performance-engineer` | Performance testing and optimization |

#### Research & Analysis
| Agent | Use Case |
|-------|----------|
| `Explore` | Codebase exploration and understanding |
| `research-analyst` | General research tasks |
| `search-specialist` | Advanced search operations |

## Usage Patterns

### Pattern 1: Direct Skill Invocation
```
# When you know which skill to use
Skill(skill="frontend-development")
```

### Pattern 2: Agent Delegation
```
# Delegate complex tasks to specialized agents
Task(
  subagent_type="python-pro",
  prompt="Optimize this function for performance: [code]"
)
```

### Pattern 3: MCP Tool Discovery
```
# Discover MCP tools for a specific task
Task(
  subagent_type="mcp-manager",
  prompt="Find MCP tools that can help with [task description]"
)
```

### Pattern 4: Parallel Agent Execution
```
# Launch multiple agents in parallel for independent tasks
# (Use single message with multiple Task tool calls)
```

## Skill Selection Guidelines

### When to Use Skills
- **Domain-specific workflows**: Use skills like `frontend-development` for React/TypeScript patterns
- **Tool-specific operations**: Use `media-processing` for FFmpeg/ImageMagick operations
- **Process guidance**: Use `code-review` for systematic review workflows

### When to Use Agents
- **Complex autonomous tasks**: Agents can explore, plan, and execute
- **Specialized expertise**: Agents have deep domain knowledge
- **Multi-step operations**: Agents maintain context across steps

### When to Use MCP Tools Directly
- **Simple operations**: Direct tool calls for straightforward tasks
- **Specific integrations**: When you know exactly which MCP tool to use

## Custom Slash Commands

Available slash commands (invoke via SlashCommand tool):
- `/use-mcp [task]` - Utilize MCP server tools
- `/git:pr [to-branch] [from-branch]` - Create pull request
- `/git:cp` - Stage, commit, and push
- `/git:cm` - Stage and commit

## Discovery Best Practices

1. **Check before assuming**: Don't assume a tool/skill/agent exists; verify in tool descriptions
2. **Use appropriate granularity**: Skills for workflows, agents for complex tasks, tools for operations
3. **Leverage parallelism**: Independent agent tasks can run concurrently
4. **Match tool to task**: Use the most specific tool available for the job

## MCP Query Pagination

When querying MCP tools that return lists, follow pagination protocol:

```python
# Probe with small limit
probe = mcp_call(limit=5)
tokens_per_item = estimate_tokens(probe) / 5

# Calculate safe limit (stay under 20k tokens)
safe_limit = min(15000 / tokens_per_item, 50)

# Paginate if needed (max 5 batches)
results = []
for i in range(5):
    batch = mcp_call(limit=safe_limit, offset=i * safe_limit)
    if estimate_tokens(batch) > 20000:
        break
    results.extend(batch)
```

## Refreshing This Reference

MCP tools, skills, and agents can change as configurations update. To get current availability:

1. **Tools**: Check MCP server configurations in `~/.claude/` or project `.claude/`
2. **Skills**: Refer to Skill tool's `<available_skills>` section
3. **Agents**: Refer to Task tool's agent type list

When uncertain about capability availability, use discovery commands rather than assuming from this reference.
