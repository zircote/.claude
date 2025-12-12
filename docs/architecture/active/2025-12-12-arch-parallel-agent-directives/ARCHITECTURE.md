---
document_type: architecture
project_id: ARCH-2025-12-12-001
version: 1.0.0
last_updated: 2025-12-12
status: draft
---

# Parallel Agent Directives for /arch Workflows - Technical Architecture

## System Overview

This enhancement modifies the `/arch:*` command suite to systematically leverage parallel specialist agents. The changes are entirely prompt-based - no code modifications required. The architecture involves:

1. **Directive injection** into command prompts enforcing parallel execution
2. **Template modifications** embedding agent assignments in planning artifacts
3. **Reference integration** connecting tasks to the agent catalog

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Implementation method | Prompt engineering only | No runtime changes needed; leverages existing Task tool |
| Agent assignment level | Both phase and task | Flexibility for different granularities |
| Enforcement strength | Strong with quality gates | Balance speed with correctness |
| Agent naming | Exact names from catalog | Direct mapping to `subagent_type` parameter |

## Component Design

### Component 0: Worktree Prompt Logging Initialization (Bug Fix)

**Purpose**: Ensure prompt capture hooks work when Claude Code launches in a new worktree.

**Problem**: Current worktree creation flow launches Claude Code in the new terminal, but prompt logging infrastructure doesn't exist yet in the worktree. The hooks check for `.prompt-log-enabled` marker and write to `PROMPT_LOG.json` - both must exist BEFORE Claude starts.

**Solution**: Modify the worktree creation sequence in `/arch:p` to create logging infrastructure before launching Claude Code.

**Required Sequence**:

```bash
# 1. Create worktree (existing)
git worktree add -b "${BRANCH_NAME}" "${WORKTREE_PATH}"

# 2. Create project directory structure IN THE WORKTREE
PROJECT_DIR="${WORKTREE_PATH}/docs/architecture/active/${DATE}-${SLUG}"
mkdir -p "${PROJECT_DIR}"

# 3. Initialize prompt logging infrastructure BEFORE launch
touch "${PROJECT_DIR}/.prompt-log-enabled"
echo '{"sessions":[],"prompts":[]}' > "${PROJECT_DIR}/PROMPT_LOG.json"

# 4. Initialize README.md with metadata (so project is discoverable)
cat > "${PROJECT_DIR}/README.md" << 'HEREDOC'
---
project_id: ${PROJECT_ID}
project_name: "${PROJECT_NAME}"
slug: ${SLUG}
status: draft
created: ${TIMESTAMP}
...
---
HEREDOC

# 5. THEN launch Claude Code with the prompt
~/.claude/skills/worktree-manager/scripts/launch-agent.sh \
  "${WORKTREE_PATH}" \
  "Architecture planning" \
  --prompt "/arch:p ${ORIGINAL_ARGS}"
```

**Key Constraint**: Steps 2-4 MUST complete BEFORE step 5. The hooks will find the marker file when Claude Code starts in the new session.

---

### Component 0a: Document Synchronization Fix (Bug Fix)

**Purpose**: Ensure `/arch:i` properly updates checkboxes and status fields during task/phase transitions.

**Problem**: The document synchronization described in `/arch:i` Phase 5 is not being executed. When tasks complete:
- Acceptance criteria checkboxes remain unchecked `[ ]` instead of `[x]`
- Status fields in frontmatter stay `draft` instead of updating to `in-progress` or `completed`
- Phase deliverable checkboxes aren't updated

**Solution**: Add explicit synchronization directives to `/arch:i` that mandate checkbox and status updates.

**Required Sync Points**:

```markdown
<sync_enforcement>
## Document Synchronization (MANDATORY)

After EVERY task status change, you MUST sync to other documents:

### When marking a task DONE:
1. In IMPLEMENTATION_PLAN.md:
   - Find the task by ID (e.g., "Task 1.1")
   - Change ALL `- [ ]` to `- [x]` in its Acceptance Criteria
2. In PROGRESS.md:
   - Update Task Status table row
   - Update Phase Status percentages

### When first task starts (project begins):
1. In README.md frontmatter: `status: draft` → `status: in-progress`
2. In README.md frontmatter: Set `started: [current timestamp]`

### When phase completes:
1. In IMPLEMENTATION_PLAN.md:
   - Mark Phase Deliverables checkboxes as `[x]`
   - Mark Phase Exit Criteria checkboxes as `[x]`
2. In CHANGELOG.md: Add phase completion entry

### When project completes:
1. In README.md frontmatter: `status: in-progress` → `status: completed`
2. In README.md frontmatter: Set `completed: [current timestamp]`

DO NOT skip synchronization. Changes to PROGRESS.md MUST propagate to other documents.
</sync_enforcement>
```

**Key Constraint**: Sync operations must happen immediately after status changes, not deferred.

---

### Component 0b: Standalone Prompt Capture Plugin (Bug Fix)

**Purpose**: Ensure prompt capture hook executes during Claude Code sessions.

**Problem**: The hookify plugin's `hooks.json` had multiple hook groups in the `UserPromptSubmit` event array. Patching hookify proved fragile - consolidation still didn't work reliably.

**Solution**: Create a standalone `prompt-capture` plugin with its own hook registration.

**Plugin Structure**:
```
~/.claude/plugins/local/prompt-capture/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest with hooks reference
├── hooks/
│   ├── hooks.json            # UserPromptSubmit hook registration
│   └── prompt_capture_hook.py # Main hook script (moved from ~/.claude/hooks/)
├── filters/
│   ├── __init__.py
│   ├── pipeline.py           # Existing filter pipeline
│   ├── log_entry.py          # Log entry creation
│   └── log_writer.py         # JSON log writing
└── README.md
```

**plugin.json**:
```json
{
  "name": "prompt-capture",
  "version": "1.0.0",
  "description": "Captures user prompts during architecture work",
  "hooks": "./hooks/hooks.json"
}
```

**hooks/hooks.json**:
```json
{
  "description": "Prompt capture logging for architecture projects",
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/prompt_capture_hook.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

**Installation**:
1. Create local marketplace: `~/.claude/marketplaces/local.json`
2. Install: `claude plugins install --marketplace ~/.claude/marketplaces/local.json prompt-capture`
3. Revert hookify patches (no longer needed)

**Key Benefits**:
- Clean separation - prompt capture is its own plugin
- No patch management when hookify updates
- Can be enabled/disabled via `/plugin` commands
- Standard plugin hook registration pattern

---

### Component 1: Parallel Execution Directive Block

A reusable directive block to be inserted into each `/arch:*` command.

**Purpose**: Enforce parallel Task tool invocation for independent work.

**Template**:

```markdown
<parallel_execution_directive>
## Parallel Agent Orchestration (MANDATORY)

You are an orchestrator, not a solo executor. You MUST leverage parallel specialist agents.

### Execution Rules

1. **ALWAYS launch parallel Task tool calls** when tasks are independent
   - Independent = one task's output does NOT inform another's input
   - Send a SINGLE message with MULTIPLE Task tool invocations

2. **Use named specialist agents** from `~/.claude/agents/`:
   - Research tasks → `research-analyst`, `competitive-analyst`
   - Code analysis → `code-reviewer`, `security-auditor`
   - Architecture → `api-designer`, `microservices-architect`
   - Implementation → `python-pro`, `typescript-pro`, `backend-developer`, etc.
   - Infrastructure → `devops-engineer`, `terraform-engineer`, `kubernetes-specialist`
   - Quality → `test-automator`, `performance-engineer`

3. **Sequential ONLY when required**:
   - When output of Agent A informs input of Agent B
   - When explicit ordering is critical for correctness

4. **Quality gates**:
   - Wrong agent is better than no agent
   - Agents can escalate or recommend different specialists
   - Prefer specialist over generic "Explore" when domain is clear

### Example Parallel Dispatch

For research phase, launch ALL of these in a single response:

Task 1: subagent_type="research-analyst" - External research
Task 2: subagent_type="code-reviewer" - Codebase analysis
Task 3: subagent_type="security-auditor" - Security review
Task 4: subagent_type="api-designer" - API/interface analysis

DO NOT wait for Task 1 to complete before launching Task 2.
</parallel_execution_directive>
```

**Insertion Points**:
- `commands/arch/p.md`: After `<role>` section
- `commands/arch/i.md`: After `<role>` section
- `commands/arch/c.md`: Before close-out protocol

---

### Component 2: Enhanced IMPLEMENTATION_PLAN.md Template

**Purpose**: Embed agent assignments directly in the planning artifact.

**Changes to Task Template**:

```markdown
#### Task [N.M]: [Title]
- **Description**: [What to do]
- **Estimated Effort**: [Hours/Days]
- **Dependencies**: None | [Task refs]
- **Agent**: [agent-name from ~/.claude/agents/]
- **Parallel Group**: [Group ID for tasks that can run together]
- **Acceptance Criteria**:
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]
- **Notes**: [Any additional context]
```

**New Fields**:
| Field | Purpose | Example Values |
|-------|---------|----------------|
| Agent | Specialist to execute task | `backend-developer`, `python-pro`, `devops-engineer` |
| Parallel Group | Tasks in same group run concurrently | `PG-1`, `PG-2`, `independent` |

**Enhanced Phase Summary Table**:

```markdown
## Phase Summary

| Phase | Goal | Lead Agent | Parallel Agents | Key Deliverables |
|-------|------|------------|-----------------|------------------|
| Phase 1: Foundation | Setup infrastructure | devops-engineer | security-auditor, documentation-engineer | CI/CD, security baseline |
| Phase 2: Core | Implement features | backend-developer | frontend-developer, api-designer | API, UI components |
| Phase 3: Integration | Connect systems | fullstack-developer | test-automator, performance-engineer | E2E flows, tests |
| Phase 4: Polish | Quality & docs | code-reviewer | technical-writer, qa-expert | Reviews, documentation |
```

---

### Component 3: Agent Recommendation Section

**Purpose**: Provide guidance on agent selection within the planning artifact.

**Template** (new section in IMPLEMENTATION_PLAN.md):

```markdown
## Agent Recommendations

This section maps task categories to recommended specialist agents.

### By Task Type

| Task Type | Primary Agent | Alternatives | Notes |
|-----------|--------------|--------------|-------|
| API design | api-designer | backend-developer, graphql-architect | Use graphql-architect for GraphQL |
| Database work | postgres-pro | database-administrator | postgres-pro for PostgreSQL specifics |
| Frontend UI | frontend-developer | react-specialist, vue-expert | Match to framework |
| Security review | security-auditor | penetration-tester | pen-tester for active testing |
| Performance | performance-engineer | database-optimizer | db-optimizer for query issues |
| Documentation | documentation-engineer | technical-writer | tech-writer for user docs |
| Infrastructure | devops-engineer | terraform-engineer, kubernetes-specialist | terraform for IaC, k8s for containers |
| Testing | test-automator | qa-expert | qa-expert for test strategy |
| Research | research-analyst | competitive-analyst | competitive for market analysis |
| Code review | code-reviewer | security-auditor | Include security for sensitive code |

### Parallel Execution Groups

Tasks within the same group have no dependencies and MUST be executed in parallel:

| Group | Tasks | Agents |
|-------|-------|--------|
| PG-1 | 1.1, 1.2, 1.3 | devops-engineer, security-auditor, documentation-engineer |
| PG-2 | 2.1, 2.2 | backend-developer, frontend-developer |
| Sequential | 3.1 → 3.2 | fullstack-developer → test-automator |
```

---

### Component 4: PROGRESS.md Agent Tracking

**Purpose**: Track which agent completed each task.

**Enhanced Task Status Table**:

```markdown
## Task Status

| ID | Description | Agent | Status | Started | Completed | Notes |
|----|-------------|-------|--------|---------|-----------|-------|
| 1.1 | Setup CI/CD | devops-engineer | done | 2025-12-12 | 2025-12-12 | |
| 1.2 | Security baseline | security-auditor | done | 2025-12-12 | 2025-12-12 | Ran parallel with 1.1 |
| 2.1 | Implement API | backend-developer | in-progress | 2025-12-12 | | |
```

---

### Component 5: Research Phase Named Agents

**Purpose**: Replace generic "Subagent 1" labels with named specialists.

**Current** (in `/arch:p`):
```
Subagent 1 - Existing Codebase Analysis:
"Explore the entire codebase..."

Subagent 2 - Technical Research:
"Search the web for best practices..."
```

**Enhanced**:
```markdown
### Parallel Research Agents

Launch ALL of these simultaneously using Task tool with specified subagent_type:

**Agent 1 - Codebase Analysis** (`subagent_type="code-reviewer"`):
"Explore the entire codebase to understand current architecture, patterns,
and conventions. Identify files and modules relevant to [project]. Document
all integration points, dependencies, and constraints."

**Agent 2 - Technical Research** (`subagent_type="research-analyst"`):
"Search the web for best practices, patterns, and solutions related to [project].
Find authoritative sources, documentation, and case studies. Identify proven
approaches and common pitfalls to avoid."

**Agent 3 - Security Analysis** (`subagent_type="security-auditor"`):
"Review the project requirements and existing codebase for security implications.
Identify authentication, authorization, data protection requirements. Flag
potential vulnerabilities and recommend mitigations."

**Agent 4 - Architecture Review** (`subagent_type="architect-reviewer"`):
"Analyze existing system architecture and proposed changes. Evaluate scalability,
maintainability, and integration complexity. Identify architectural risks."
```

---

## Data Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                      /arch:p Planning Flow                              │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  User Input                                                            │
│      │                                                                 │
│      ▼                                                                 │
│  ┌─────────────────┐                                                   │
│  │ Requirements    │                                                   │
│  │ Elicitation     │  (Sequential - needs user input)                  │
│  └────────┬────────┘                                                   │
│           │                                                            │
│           ▼                                                            │
│  ┌─────────────────────────────────────────────────────────┐          │
│  │              PARALLEL RESEARCH PHASE                     │          │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │          │
│  │  │ code-reviewer│  │research-     │  │security-     │  │          │
│  │  │ (codebase)   │  │analyst (web) │  │auditor       │  │          │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │          │
│  │         │                  │                  │         │          │
│  │         └──────────────────┼──────────────────┘         │          │
│  │                            │                            │          │
│  └────────────────────────────┼────────────────────────────┘          │
│                               ▼                                        │
│                    ┌─────────────────┐                                 │
│                    │ Synthesize      │                                 │
│                    │ Research Results│                                 │
│                    └────────┬────────┘                                 │
│                             │                                          │
│                             ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐          │
│  │           PARALLEL DOCUMENTATION PHASE                   │          │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │          │
│  │  │api-designer  │  │documentation-│  │architect-    │  │          │
│  │  │(ARCH.md)     │  │engineer(REQ) │  │reviewer(ADR) │  │          │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │          │
│  └─────────────────────────────────────────────────────────┘          │
│                               │                                        │
│                               ▼                                        │
│                    ┌─────────────────┐                                 │
│                    │ IMPLEMENTATION  │                                 │
│                    │ PLAN.md with    │                                 │
│                    │ Agent Assignments│                                │
│                    └─────────────────┘                                 │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### With Existing Agent Catalog

| Integration | Mechanism |
|-------------|-----------|
| Agent lookup | Reference `~/.claude/agents/[category]/[agent].md` |
| subagent_type | Use exact filename without `.md` extension |
| Tool access | Agents inherit tools from their definition |

### With Task Tool API

```
Task tool parameters:
- subagent_type: REQUIRED - agent name from catalog
- prompt: REQUIRED - task description
- description: OPTIONAL - short summary for tracking
- model: OPTIONAL - defaults to inherit (opus-4-5)
```

### With CLAUDE.md

The existing "Parallel Specialist Subagents" section in CLAUDE.md already documents agent categories. This enhancement:
- References that section from `/arch:*` commands
- Does NOT duplicate agent documentation
- Adds only the enforcement directive

---

## Dependency-Aware Execution

### Parallelization Rules

```
PARALLEL (launch together):
├── Tasks in same Parallel Group
├── Tasks with no dependency relationship
└── Different phases of review (code + security + performance)

SEQUENTIAL (wait for completion):
├── Tasks with explicit "Dependencies: [task]"
├── Synthesis after parallel research
└── Implementation after architecture approval
```

### Quality Safeguards

1. **Dependency declaration**: Tasks must declare dependencies explicitly
2. **Parallel Group assignment**: Tasks without groups default to sequential
3. **Agent escalation**: Agents can recommend different specialists
4. **Human checkpoint**: User approval before phase transitions

---

## Testing Strategy

### Verification Approach

Since this is prompt engineering, testing involves:

1. **Manual execution testing**: Run `/arch:p` and observe Task tool call patterns
2. **Artifact inspection**: Verify IMPLEMENTATION_PLAN.md contains agent assignments
3. **Parallel execution confirmation**: Check multiple Task calls in single response
4. **Agent utilization review**: Confirm named agents vs generic Explore

### Success Indicators

- [ ] Multiple Task tool calls appear in single Claude response
- [ ] subagent_type parameters reference named agents
- [ ] IMPLEMENTATION_PLAN.md tasks have Agent field populated
- [ ] Phase Summary shows Lead Agent and Parallel Agents
- [ ] PROGRESS.md tracks which agent completed each task

---

## Rollout Considerations

### Backward Compatibility

- Existing planning artifacts remain valid (Agent field optional)
- Old PROGRESS.md files work without Agent column
- Commands function if agent catalog not present (degraded mode)

### Migration Path

1. Update command files (p.md, i.md, s.md, c.md)
2. Existing active projects continue with old format
3. New projects get agent-aware templates
4. No migration of historical artifacts required

---

## Future Considerations

1. **Agent performance tracking**: Capture which agents produce best results
2. **Auto-assignment**: Suggest agents based on task description keywords
3. **Agent chaining**: Output of one agent feeds into another automatically
4. **Workload balancing**: Distribute work based on agent capacity
