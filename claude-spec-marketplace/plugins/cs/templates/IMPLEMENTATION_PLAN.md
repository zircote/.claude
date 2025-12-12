---
document_type: implementation_plan
project_id: ${PROJECT_ID}
version: 1.0.0
status: draft
---

# ${PROJECT_NAME} - Implementation Plan

## Overview

**Total Phases**: ${PHASE_COUNT}
**Total Tasks**: ${TASK_COUNT}
**Estimated Agent Load**: ${AGENT_COUNT} parallel agents max

## Phases

### Phase 1: ${PHASE_1_NAME}

**Objective**: [Phase goal]
**Dependencies**: None
**Deliverables**: [What this phase produces]

| Task | Description | Agent | Status |
|------|-------------|-------|--------|
| 1.1 | [Task description] | [agent-type] | ⬜ |
| 1.2 | [Task description] | [agent-type] | ⬜ |

#### Task Details

##### Task 1.1: [Title]

**Agent**: `[agent-type]` from `~/.claude/agents/[category]/`
**Parallelizable**: Yes/No
**Inputs**: [Required inputs]
**Outputs**: [Expected outputs]
**Acceptance Criteria**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

---

### Phase 2: ${PHASE_2_NAME}

**Objective**: [Phase goal]
**Dependencies**: Phase 1 completion
**Deliverables**: [What this phase produces]

| Task | Description | Agent | Status |
|------|-------------|-------|--------|
| 2.1 | [Task description] | [agent-type] | ⬜ |
| 2.2 | [Task description] | [agent-type] | ⬜ |

<parallel_execution_directive>
Tasks 2.1 and 2.2 are independent and MUST be executed in parallel using the Task tool with multiple content blocks in a single message.

Required agent launches:
- Task 2.1: `subagent_type="[agent-type]"`
- Task 2.2: `subagent_type="[agent-type]"`
</parallel_execution_directive>

---

### Phase 3: ${PHASE_3_NAME}

**Objective**: [Phase goal]
**Dependencies**: Phase 2 completion
**Deliverables**: [What this phase produces]

| Task | Description | Agent | Status |
|------|-------------|-------|--------|
| 3.1 | [Task description] | [agent-type] | ⬜ |

---

## Agent Catalog Reference

| Agent Type | Category | Use For |
|------------|----------|---------|
| frontend-developer | 01-core-development | UI components, React/Vue/Angular |
| backend-developer | 01-core-development | APIs, services, business logic |
| python-pro | 02-language-specialists | Python implementation |
| typescript-pro | 02-language-specialists | TypeScript implementation |
| devops-engineer | 03-infrastructure | CI/CD, deployment |
| code-reviewer | 04-quality-security | Code review, quality checks |
| test-automator | 04-quality-security | Test creation, automation |
| prompt-engineer | 05-data-ai | Command prompts, templates |
| cli-developer | 06-developer-experience | CLI tools, scripts |

See `~/.claude/agents/` for full catalog.

## Status Legend

- ⬜ Pending
- 🔄 In Progress
- ✅ Complete
- ⏭️ Skipped
- ❌ Blocked

## Document Sync Requirements

<sync_enforcement>
When task status changes:
1. Update checkbox in this file: `[ ]` → `[x]`
2. Update PROGRESS.md with timestamp
3. Update README.md frontmatter status if phase completes
</sync_enforcement>

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | Low/Med/High | Low/Med/High | [Strategy] |

## Rollback Plan

If implementation fails:
1. [Rollback step 1]
2. [Rollback step 2]
