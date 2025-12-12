---
document_type: progress
project_id: ${PROJECT_ID}
created: ${DATE}
last_updated: ${DATE}
---

# ${PROJECT_NAME} - Progress Tracker

## Status Summary

| Metric | Value |
|--------|-------|
| **Overall Progress** | 0% |
| **Current Phase** | Phase 1 |
| **Tasks Complete** | 0/${TASK_COUNT} |
| **Agents Used** | 0 |
| **Started** | ${DATE} |
| **Last Activity** | ${DATE} |

## Phase Progress

| Phase | Name | Status | Progress | Tasks |
|-------|------|--------|----------|-------|
| 1 | ${PHASE_1_NAME} | pending | 0% | 0/2 |
| 2 | ${PHASE_2_NAME} | pending | 0% | 0/2 |
| 3 | ${PHASE_3_NAME} | pending | 0% | 0/1 |

## Task Log

### Phase 1: ${PHASE_1_NAME}

| Task | Description | Agent | Status | Started | Completed | Notes |
|------|-------------|-------|--------|---------|-----------|-------|
| 1.1 | [Description] | [agent] | pending | - | - | |
| 1.2 | [Description] | [agent] | pending | - | - | |

### Phase 2: ${PHASE_2_NAME}

| Task | Description | Agent | Status | Started | Completed | Notes |
|------|-------------|-------|--------|---------|-----------|-------|
| 2.1 | [Description] | [agent] | pending | - | - | |
| 2.2 | [Description] | [agent] | pending | - | - | |

### Phase 3: ${PHASE_3_NAME}

| Task | Description | Agent | Status | Started | Completed | Notes |
|------|-------------|-------|--------|---------|-----------|-------|
| 3.1 | [Description] | [agent] | pending | - | - | |

## Agent Execution Log

Records all subagent invocations for retrospective analysis.

| Timestamp | Task | Agent Type | Agent ID | Status | Duration | Notes |
|-----------|------|------------|----------|--------|----------|-------|
| - | - | - | - | - | - | - |

## Divergences from Plan

Documents any deviations from the original implementation plan.

| Date | Task | Original Plan | Actual | Reason |
|------|------|---------------|--------|--------|
| - | - | - | - | - |

## Blockers & Issues

| Issue | Severity | Status | Resolution |
|-------|----------|--------|------------|
| - | - | - | - |

## Session History

| Session | Date | Tasks Completed | Notes |
|---------|------|-----------------|-------|
| 1 | ${DATE} | - | Initial creation |

---

## Update Instructions

This file is updated by `/cs:i` (implementation tracker):

1. **Task Status Change**: Update task row, recalculate phase/overall progress
2. **Agent Launch**: Add entry to Agent Execution Log
3. **Plan Divergence**: Document in Divergences section
4. **Blocker Found**: Add to Blockers & Issues
5. **Session End**: Add to Session History

### Status Values

- `pending` - Not started
- `in-progress` - Currently being worked on
- `done` - Completed successfully
- `skipped` - Intentionally skipped
- `blocked` - Cannot proceed due to blocker

### Progress Calculation

```
Phase Progress = (done_tasks / total_phase_tasks) * 100
Overall Progress = (done_tasks / total_tasks) * 100
```
