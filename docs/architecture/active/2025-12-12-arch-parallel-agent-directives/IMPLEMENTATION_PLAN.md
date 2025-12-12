---
document_type: implementation_plan
project_id: ARCH-2025-12-12-001
version: 1.0.0
last_updated: 2025-12-12
status: draft
estimated_effort: 4-6 hours
---

# Parallel Agent Directives for /arch Workflows - Implementation Plan

## Overview

This plan implements systematic parallel agent orchestration across the `/arch:*` command suite. All changes are prompt engineering - modifying markdown command files to embed agent assignments and parallel execution directives.

## Phase Summary

| Phase | Goal | Lead Agent | Parallel Agents | Key Deliverables |
|-------|------|------------|-----------------|------------------|
| Phase 1: Foundation | Fix worktree logging, add directive block, create prompt-capture plugin | cli-developer | documentation-engineer, mcp-developer | Worktree fix, directive template, standalone plugin |
| Phase 2: Command Updates | Update all four /arch commands | prompt-engineer | code-reviewer | Modified p.md, i.md, s.md, c.md |
| Phase 3: Template Enhancement | Update artifact templates | documentation-engineer | architect-reviewer | Enhanced IMPLEMENTATION_PLAN template |
| Phase 4: Validation | Test and verify changes | test-automator | code-reviewer | Verified parallel execution |

---

## Agent Recommendations

### By Task Type

| Task Type | Primary Agent | Alternatives | Notes |
|-----------|--------------|--------------|-------|
| Command prompt editing | prompt-engineer | cli-developer | prompt-engineer for directive language |
| Template modification | documentation-engineer | technical-writer | Focus on structured templates |
| Worktree script fixes | cli-developer | devops-engineer | Bash scripting expertise |
| Architecture review | architect-reviewer | code-reviewer | Validate design consistency |
| Testing verification | test-automator | qa-expert | Manual execution testing |

### Parallel Execution Groups

| Group | Tasks | Agents | Rationale |
|-------|-------|--------|-----------|
| PG-1.1 | 1.1, 1.2, 1.3 | cli-developer, prompt-engineer, mcp-developer | Independent: worktree fix, directive creation, plugin creation |
| PG-2.1 | 2.1, 2.2, 2.3, 2.4 | prompt-engineer (x4) | Independent: each command file separate |
| PG-3.1 | 3.1, 3.2 | documentation-engineer, architect-reviewer | Independent: templates vs review |
| Sequential | 4.1 → 4.2 | test-automator → code-reviewer | Depends: test before review |

---

## Phase 1: Foundation

**Goal**: Fix worktree prompt logging bug and create reusable directive block
**Prerequisites**: None
**Lead Agent**: cli-developer
**Parallel Agents**: documentation-engineer

### Tasks

#### Task 1.1: Fix Worktree Prompt Logging Initialization
- **Description**: Modify `/arch:p` worktree creation sequence to initialize prompt logging infrastructure (`.prompt-log-enabled` marker and `PROMPT_LOG.json`) BEFORE launching Claude Code in the new terminal.
- **Estimated Effort**: 1 hour
- **Dependencies**: None
- **Agent**: cli-developer
- **Parallel Group**: PG-1.1
- **Acceptance Criteria**:
  - [ ] Worktree creation creates project directory structure
  - [ ] `.prompt-log-enabled` file created before launch-agent.sh call
  - [ ] `PROMPT_LOG.json` initialized with empty structure before launch
  - [ ] README.md with metadata created so project is discoverable
- **Notes**: This fixes a bug where prompt capture hooks fail because marker file doesn't exist when Claude starts

#### Task 1.2: Create Parallel Execution Directive Block
- **Description**: Write the reusable `<parallel_execution_directive>` XML block that will be inserted into each `/arch:*` command to enforce parallel agent orchestration.
- **Estimated Effort**: 30 minutes
- **Dependencies**: None
- **Agent**: prompt-engineer
- **Parallel Group**: PG-1.1
- **Acceptance Criteria**:
  - [ ] Directive block includes MUST language for parallel execution
  - [ ] Lists agent categories with example specialists
  - [ ] Includes sequential exception criteria
  - [ ] Provides example parallel dispatch pattern
- **Notes**: This block will be copy-pasted into each command file

#### Task 1.3: Create Standalone Prompt Capture Plugin
- **Description**: Create a standalone `prompt-capture` plugin with proper hook registration, replacing the fragile hookify patching approach. Move existing hook script into plugin structure.
- **Estimated Effort**: 1 hour
- **Dependencies**: None
- **Agent**: mcp-developer
- **Parallel Group**: PG-1.1
- **Acceptance Criteria**:
  - [ ] Plugin directory structure created at `~/.claude/plugins/local/prompt-capture/`
  - [ ] `.claude-plugin/plugin.json` with hooks reference
  - [ ] `hooks/hooks.json` registering UserPromptSubmit hook
  - [ ] Hook script moved from `~/.claude/hooks/prompt_capture_hook.py` to plugin
  - [ ] Filter modules included in plugin (`filters/*.py`)
  - [ ] Local marketplace created at `~/.claude/marketplaces/local.json`
  - [ ] Plugin installable via `claude plugins install`
  - [ ] Hookify patches removed (no longer needed)
- **Notes**: This fixes the bug where prompt capture hook was never triggered due to hookify's multi-group hook structure

### Phase 1 Deliverables
- [ ] Fixed worktree creation sequence in `/arch:p`
- [ ] Standalone directive block ready for insertion
- [ ] Prompt capture plugin created and installable

### Phase 1 Exit Criteria
- [ ] Worktree creation initializes logging before launch
- [ ] Directive block reviewed and approved
- [ ] Prompt capture plugin working independently

---

## Phase 2: Command Updates

**Goal**: Update all four `/arch:*` commands with parallel execution directives
**Prerequisites**: Phase 1 complete (directive block ready)
**Lead Agent**: prompt-engineer
**Parallel Agents**: code-reviewer

### Tasks

#### Task 2.1: Update `/arch:p` (Planning Command)
- **Description**: Insert parallel execution directive, update research phase to use named agents, enhance IMPLEMENTATION_PLAN.md template with Agent fields.
- **Estimated Effort**: 1.5 hours
- **Dependencies**: Task 1.1 (worktree fix), Task 1.2 (directive block)
- **Agent**: prompt-engineer
- **Parallel Group**: PG-2.1 (can run with 2.2, 2.3, 2.4 after Phase 1)
- **Acceptance Criteria**:
  - [ ] `<parallel_execution_directive>` inserted after `<role>`
  - [ ] Research phase uses named agents: code-reviewer, research-analyst, security-auditor, architect-reviewer
  - [ ] IMPLEMENTATION_PLAN.md template includes `- **Agent**:` field
  - [ ] Phase Summary table includes Lead Agent and Parallel Agents columns
  - [ ] Agent Recommendations section added to template
  - [ ] Worktree creation sequence fixed per Task 1.1
- **Notes**: This is the largest update - planning command sets the pattern for others

#### Task 2.2: Update `/arch:i` (Implementation Command)
- **Description**: Insert parallel execution directive, update PROGRESS.md template with Agent column, add parallel task execution guidance, AND fix document synchronization bug.
- **Estimated Effort**: 1 hour
- **Dependencies**: Task 1.2 (directive block)
- **Agent**: prompt-engineer
- **Parallel Group**: PG-2.1
- **Acceptance Criteria**:
  - [ ] `<parallel_execution_directive>` inserted after `<role>`
  - [ ] PROGRESS.md Task Status table includes Agent column
  - [ ] Guidance on executing tasks by Parallel Group
  - [ ] Session notes template references agent assignments
  - [ ] `<sync_enforcement>` block added mandating checkbox/status updates
  - [ ] Explicit sync points defined: task done, phase complete, project complete
  - [ ] Status field transitions enforced: draft → in-progress → completed
- **Notes**: Implementation command must honor Agent and Parallel Group from plan. Also fixes bug where checkboxes and status fields weren't being updated during transitions.

#### Task 2.3: Update `/arch:s` (Status Command)
- **Description**: Add agent utilization statistics to portfolio view (P2 enhancement - optional).
- **Estimated Effort**: 30 minutes
- **Dependencies**: Task 1.2 (directive block)
- **Agent**: prompt-engineer
- **Parallel Group**: PG-2.1
- **Acceptance Criteria**:
  - [ ] Status output shows agent assignment coverage (if implemented)
  - [ ] Or: Document as future enhancement and skip
- **Notes**: Lower priority - status command is read-only

#### Task 2.4: Update `/arch:c` (Close-out Command)
- **Description**: Insert parallel execution directive for retrospective generation, add agent performance capture to RETROSPECTIVE.md template.
- **Estimated Effort**: 30 minutes
- **Dependencies**: Task 1.2 (directive block)
- **Agent**: prompt-engineer
- **Parallel Group**: PG-2.1
- **Acceptance Criteria**:
  - [ ] Parallel agents used for retrospective gathering if applicable
  - [ ] RETROSPECTIVE.md template includes agent performance notes section
- **Notes**: Close-out is mostly sequential but can parallelize some analysis

### Phase 2 Deliverables
- [ ] Updated `commands/arch/p.md`
- [ ] Updated `commands/arch/i.md`
- [ ] Updated `commands/arch/s.md` (or documented skip)
- [ ] Updated `commands/arch/c.md`

### Phase 2 Exit Criteria
- [ ] All command files contain parallel execution directive
- [ ] Templates include agent assignment fields
- [ ] Named agents specified for research phases

---

## Phase 3: Template Enhancement

**Goal**: Ensure all artifact templates support agent tracking
**Prerequisites**: Phase 2 complete (commands updated)
**Lead Agent**: documentation-engineer
**Parallel Agents**: architect-reviewer

### Tasks

#### Task 3.1: Verify Template Consistency
- **Description**: Review all templates in updated commands to ensure consistent Agent field format, Parallel Group notation, and agent recommendation tables.
- **Estimated Effort**: 30 minutes
- **Dependencies**: Phase 2 complete
- **Agent**: documentation-engineer
- **Parallel Group**: PG-3.1
- **Acceptance Criteria**:
  - [ ] All task templates use same `- **Agent**:` format
  - [ ] Parallel Group notation consistent across templates
  - [ ] Agent Recommendations table format standardized
- **Notes**: Consistency enables automation in future

#### Task 3.2: Architecture Review
- **Description**: Review all changes against ARCHITECTURE.md design, verify integration points, confirm backward compatibility.
- **Estimated Effort**: 30 minutes
- **Dependencies**: Phase 2 complete
- **Agent**: architect-reviewer
- **Parallel Group**: PG-3.1
- **Acceptance Criteria**:
  - [ ] All components from ARCHITECTURE.md implemented
  - [ ] No breaking changes to existing artifacts
  - [ ] Integration with agent catalog verified
- **Notes**: Final design validation before testing

### Phase 3 Deliverables
- [ ] Template consistency verified
- [ ] Architecture compliance confirmed

### Phase 3 Exit Criteria
- [ ] All templates follow consistent format
- [ ] No design deviations from ARCHITECTURE.md

---

## Phase 4: Validation

**Goal**: Verify parallel execution works correctly
**Prerequisites**: Phase 3 complete
**Lead Agent**: test-automator
**Parallel Agents**: code-reviewer

### Tasks

#### Task 4.1: Manual Execution Test
- **Description**: Run `/arch:p` with a test project idea and verify parallel Task tool calls are generated, named agents are used, and artifacts contain agent assignments.
- **Estimated Effort**: 1 hour
- **Dependencies**: Phase 3 complete
- **Agent**: test-automator
- **Parallel Group**: Sequential (4.1 → 4.2)
- **Acceptance Criteria**:
  - [ ] Multiple Task tool calls appear in single Claude response
  - [ ] subagent_type parameters reference named agents (not generic Explore)
  - [ ] IMPLEMENTATION_PLAN.md created with Agent fields populated
  - [ ] Worktree creation initializes prompt logging correctly
- **Notes**: This is manual verification - observe Claude's behavior

#### Task 4.2: Final Code Review
- **Description**: Review all modified command files for correctness, security, and style consistency.
- **Estimated Effort**: 30 minutes
- **Dependencies**: Task 4.1 complete
- **Agent**: code-reviewer
- **Parallel Group**: Sequential (after 4.1)
- **Acceptance Criteria**:
  - [ ] No syntax errors in markdown
  - [ ] Directive language is clear and unambiguous
  - [ ] No security concerns with bash commands
  - [ ] Consistent style across all files
- **Notes**: Final quality gate before merge

### Phase 4 Deliverables
- [ ] Test execution log/notes
- [ ] Code review approval

### Phase 4 Exit Criteria
- [ ] Parallel execution verified working
- [ ] All code reviewed and approved
- [ ] Ready for merge to main

---

## Dependency Graph

```
Phase 1 (Foundation):
  Task 1.1 (worktree fix) ───┐
                              ├──► Phase 2
  Task 1.2 (directive)   ────┘

Phase 2 (Commands) - ALL PARALLEL after Phase 1:
  Task 2.1 (p.md) ────┐
  Task 2.2 (i.md) ────┼──► Phase 3
  Task 2.3 (s.md) ────┤
  Task 2.4 (c.md) ────┘

Phase 3 (Templates) - PARALLEL:
  Task 3.1 (consistency) ───┐
                             ├──► Phase 4
  Task 3.2 (arch review) ───┘

Phase 4 (Validation) - SEQUENTIAL:
  Task 4.1 (test) ──► Task 4.2 (review) ──► DONE
```

---

## Risk Mitigation Tasks

| Risk | Mitigation Task | Phase |
|------|-----------------|-------|
| Over-parallelization causing quality issues | Include dependency-awareness language in directives | 1 |
| Prompt length increases significantly | Use concise directive language, reference CLAUDE.md | 2 |
| Worktree logging still broken | Test worktree creation explicitly in Phase 4 | 4 |

---

## Testing Checklist

- [ ] Worktree creation initializes `.prompt-log-enabled` before launch
- [ ] Prompt capture plugin installs successfully
- [ ] Prompt capture hook triggers on UserPromptSubmit (test with `/arch:log on`)
- [ ] `/arch:p` generates parallel Task tool calls
- [ ] Named agents used (research-analyst, code-reviewer, etc.)
- [ ] IMPLEMENTATION_PLAN.md contains Agent field in task template
- [ ] PROGRESS.md contains Agent column
- [ ] No regression in existing `/arch:*` functionality

---

## Documentation Tasks

- [ ] Update CHANGELOG.md with implementation notes
- [ ] Update project README.md status to in-review
- [ ] No separate documentation needed (changes are self-documenting in commands)

---

## Launch Checklist

- [ ] All 4 command files updated
- [ ] Worktree logging fix verified
- [ ] Parallel execution observed in test run
- [ ] Code review approved
- [ ] Ready to merge to main branch

---

## Post-Launch

- [ ] Monitor first few `/arch:p` executions for parallel behavior
- [ ] Gather feedback on agent assignment effectiveness
- [ ] Consider auto-assignment enhancement based on usage patterns
- [ ] Archive planning documents to completed/
