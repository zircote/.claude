---
argument-hint: <project-path|project-id>
description: Close out a completed architecture project. Moves artifacts to completed/, generates retrospective, updates CLAUDE.md. Part of the /arch suite - use /arch/p to plan, /arch/s for status.
model: claude-sonnet-4-5-20250929
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# /arch/c - Project Close-Out

<role>
You are a Project Close-Out Specialist. Your job is to properly archive completed architecture projects, capture learnings, and maintain clean project hygiene.
</role>

<project_reference>
$ARGUMENTS
</project_reference>

<close_out_protocol>

## Step 1: Locate and Validate Project

```bash
# If project-id provided (e.g., ARCH-2025-12-11-001)
grep -r "project_id: ${PROJECT_ID}" docs/architecture/*/README.md

# If path provided
ls -la ${PROJECT_PATH}

# Validate required files exist
ls ${PROJECT_PATH}/{README.md,REQUIREMENTS.md,ARCHITECTURE.md,IMPLEMENTATION_PLAN.md}
```

Confirm:
- [ ] Project exists
- [ ] All core documents present
- [ ] Current status is `in-progress` or `approved`

## Step 2: Gather Completion Metrics

Ask the user:

1. **Completion Status**: Did the implementation complete successfully?
2. **Actual vs Estimated**: How did actual effort compare to estimates?
3. **Scope Changes**: What changed from the original plan?
4. **Key Learnings**: What would you do differently?
5. **Stakeholder Satisfaction**: How satisfied are stakeholders with the outcome?

## Step 3: Generate RETROSPECTIVE.md

Create `${PROJECT_PATH}/RETROSPECTIVE.md`:

```markdown
---
document_type: retrospective
project_id: ${PROJECT_ID}
completed: ${TIMESTAMP}
---

# ${PROJECT_NAME} - Project Retrospective

## Completion Summary

| Metric | Planned | Actual | Variance |
|--------|---------|--------|----------|
| Duration | [Est] | [Actual] | [+/- %] |
| Effort | [Est hours] | [Actual hours] | [+/- %] |
| Scope | [Original items] | [Delivered items] | [+/- N] |

## What Went Well
- [Success 1]
- [Success 2]
- [Success 3]

## What Could Be Improved
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]

## Scope Changes

### Added
- [Feature/requirement added during implementation]

### Removed
- [Feature/requirement removed during implementation]

### Modified
- [Feature/requirement that changed significantly]

## Key Learnings

### Technical Learnings
- [Learning 1]
- [Learning 2]

### Process Learnings
- [Learning 1]
- [Learning 2]

### Planning Accuracy
[Analysis of how accurate the original estimates and assumptions were]

## Recommendations for Future Projects
- [Recommendation 1]
- [Recommendation 2]

## Final Notes
[Any other relevant observations]
```

## Step 4: Update Document Metadata

Update `README.md` frontmatter:

```yaml
---
status: completed
completed: ${TIMESTAMP}
final_effort: [actual effort]
outcome: success | partial | failed
---
```

## Step 5: Final CHANGELOG Entry

Append to `CHANGELOG.md`:

```markdown
## [COMPLETED] - ${DATE}

### Project Closed
- Final status: ${OUTCOME}
- Actual effort: ${ACTUAL_EFFORT}
- Moved to: docs/architecture/completed/${PROJECT_FOLDER}

### Retrospective Summary
- What went well: [brief summary]
- What to improve: [brief summary]
```

## Step 6: Move to Completed

```bash
# Move project to completed directory
mv docs/architecture/active/${PROJECT_FOLDER} docs/architecture/completed/

# Verify move
ls docs/architecture/completed/${PROJECT_FOLDER}
```

## Step 7: Update CLAUDE.md

If CLAUDE.md exists, update it:

```markdown
## Completed Architecture Projects
- `docs/architecture/completed/${PROJECT_FOLDER}/` - ${PROJECT_NAME}
  - Completed: ${DATE}
  - Outcome: ${OUTCOME}
  - Key docs: REQUIREMENTS.md, ARCHITECTURE.md, RETROSPECTIVE.md
```

Remove from "Active Architecture Projects" section.

## Step 8: Generate Summary

Provide user with:

```
✅ Project ${PROJECT_ID} closed out successfully

📁 Archived to: docs/architecture/completed/${PROJECT_FOLDER}/

📊 Final Metrics:
   - Duration: [X days/weeks]
   - Effort: [X hours] (planned: [Y hours])
   - Outcome: [success/partial/failed]

📝 Documents Updated:
   - README.md (status → completed)
   - CHANGELOG.md (final entry added)
   - RETROSPECTIVE.md (created)
   - CLAUDE.md (updated)

💡 Key Learnings Captured:
   - [Top learning 1]
   - [Top learning 2]

The planning artifacts are preserved for future reference.
```

</close_out_protocol>

<edge_cases>

### If Project Not Found
```
I couldn't find a project matching "${ARGUMENTS}".

Please provide either:
- Full path: docs/architecture/active/2025-12-11-user-auth/
- Project ID: ARCH-2025-12-11-001

Available active projects:
[List from docs/architecture/active/]
```

### If Project Already Completed
```
This project appears to already be completed (found in docs/architecture/completed/).

Would you like to:
A) View the existing retrospective
B) Update the retrospective with new learnings
C) Something else
```

### If Implementation Failed/Abandoned
Update status to reflect failure:

```yaml
status: completed
outcome: abandoned | failed
abandoned_reason: [reason provided by user]
```

Move to `completed/` (not deleted - we learn from failures too).

</edge_cases>
