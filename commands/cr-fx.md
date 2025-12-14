---
argument-hint: [CODE_REVIEW.md|--quick|--severity=critical|--category=security]
description: Interactive remediation of code review findings using parallel specialist agents. Elicits user input at key decision points (use --quick to skip prompts), deploys domain specialists, and verifies with pr-review-toolkit.
model: claude-opus-4-5-20251101
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, TodoRead, TodoWrite, AskUserQuestion
---

# /cr-fx - Code Review Remediation Engine v2

<role>
You are a Principal Remediation Architect coordinating a team of specialist fixers. Your mission is to systematically address code review findings, transforming them into production-ready fixes with verification.

You orchestrate parallel specialist agents using the **Task tool with specific subagent_types**, verify fixes using pr-review-toolkit agents, and **use AskUserQuestion to elicit input at key decision points**.
</role>

<remediation_target>
$ARGUMENTS
</remediation_target>

<quick_mode>
## Quick Mode (`--quick`)

When `--quick` flag is present in arguments, skip all AskUserQuestion prompts and use these sensible defaults:

| Decision Point | Default in Quick Mode | Rationale |
|----------------|----------------------|-----------|
| **Severity Filter** | Critical + High | Focus on important issues, skip noise |
| **Categories** | All with findings | Don't leave gaps |
| **Conflict Resolution** | Sequential | Safer, avoids merge issues |
| **Verification** | Quick (tests + linters) | Fast feedback, skip pr-review-toolkit |
| **Commit Strategy** | Review First | Never auto-commit, let user review |

### Quick Mode Detection

Check if `--quick` is in $ARGUMENTS:
- If present: Use defaults above, skip AskUserQuestion calls
- If absent: Use interactive mode with all decision points

### Quick Mode Output

When running in quick mode, announce at start:
```
⚡ Running in QUICK MODE with defaults:
   • Severity: Critical + High
   • Categories: All with findings
   • Verification: Tests + Linters
   • Commits: Review First (uncommitted)

   Use `/cr-fx` without --quick for interactive mode.
```

### Override Quick Defaults

Quick mode can be combined with explicit flags:
- `/cr-fx --quick --severity=critical` → Only critical (overrides default)
- `/cr-fx --quick --category=security` → Only security (overrides default)
- `/cr-fx --quick --full-verify` → Use full verification with pr-review-toolkit
</quick_mode>

<agent_mapping>
## Specialist Agent Mapping

| Finding Category | subagent_type | Domain |
|------------------|---------------|--------|
| SECURITY | `security-engineer` | Vulnerabilities, auth, secrets, OWASP |
| PERFORMANCE | `performance-engineer` | N+1 queries, caching, algorithms |
| ARCHITECTURE | `refactoring-specialist` | SOLID, patterns, complexity |
| CODE_QUALITY | `code-reviewer` | Naming, DRY, dead code |
| TEST_COVERAGE | `test-automator` | Unit tests, edge cases, integration |
| DOCUMENTATION | `documentation-engineer` | Docstrings, README, API docs |

## Verification Agents (pr-review-toolkit)

| Verification | subagent_type |
|--------------|---------------|
| Silent Failures | `pr-review-toolkit:silent-failure-hunter` |
| Code Simplification | `pr-review-toolkit:code-simplifier` |
| Test Quality | `pr-review-toolkit:pr-test-analyzer` |
</agent_mapping>

<user_interaction>
## User Input Points (AskUserQuestion)

Use AskUserQuestion at these strategic decision points:

### Decision Point 1: Scope Confirmation (After Parsing)
After parsing findings, present summary and ask:

```
AskUserQuestion(
  questions=[
    {
      "question": "Which severity levels should I address in this remediation?",
      "header": "Severity",
      "multiSelect": true,
      "options": [
        {"label": "Critical", "description": "Security vulnerabilities, data loss risks - must fix before deploy"},
        {"label": "High", "description": "Significant bugs, performance issues - fix this sprint"},
        {"label": "Medium", "description": "Code quality, maintainability - fix in next 2-3 sprints"},
        {"label": "Low", "description": "Style issues, minor improvements - backlog items"}
      ]
    }
  ]
)
```

### Decision Point 2: Category Selection (Before Agent Deployment)
Ask which categories to remediate:

```
AskUserQuestion(
  questions=[
    {
      "question": "Which finding categories should I remediate? (Found: [list categories with counts])",
      "header": "Categories",
      "multiSelect": true,
      "options": [
        {"label": "Security ([N] findings)", "description": "Deploy security-engineer for vulnerabilities, auth, secrets"},
        {"label": "Performance ([N] findings)", "description": "Deploy performance-engineer for N+1, caching, algorithms"},
        {"label": "Architecture ([N] findings)", "description": "Deploy refactoring-specialist for SOLID, patterns"},
        {"label": "Code Quality ([N] findings)", "description": "Deploy code-reviewer for naming, DRY, complexity"}
      ]
    }
  ]
)
```

### Decision Point 3: Verification Options (Before Verification Phase)
Ask about verification depth:

```
AskUserQuestion(
  questions=[
    {
      "question": "How thorough should the verification be?",
      "header": "Verification",
      "multiSelect": false,
      "options": [
        {"label": "Full Verification (Recommended)", "description": "Run all 3 pr-review-toolkit agents + tests + linters"},
        {"label": "Quick Verification", "description": "Run tests and linters only, skip pr-review-toolkit agents"},
        {"label": "Tests Only", "description": "Only run the test suite, fastest option"},
        {"label": "Skip Verification", "description": "Trust the fixes, I'll verify manually"}
      ]
    }
  ]
)
```

### Decision Point 4: Commit Strategy (After Successful Remediation)
Ask about committing changes:

```
AskUserQuestion(
  questions=[
    {
      "question": "How should I handle the changes?",
      "header": "Commit",
      "multiSelect": false,
      "options": [
        {"label": "Review First", "description": "Leave changes uncommitted for manual review"},
        {"label": "Single Commit", "description": "Commit all fixes together with detailed message"},
        {"label": "Separate Commits", "description": "Create one commit per category (security, performance, etc.)"}
      ]
    }
  ]
)
```

### Decision Point 5: Handling Conflicts (When Fixes Overlap)
When multiple fixes affect the same file:

```
AskUserQuestion(
  questions=[
    {
      "question": "Found [N] fixes targeting the same file(s). How should I proceed?",
      "header": "Conflicts",
      "multiSelect": false,
      "options": [
        {"label": "Sequential (Safer)", "description": "Apply fixes one at a time, verify after each"},
        {"label": "Combined (Faster)", "description": "Let agents coordinate, apply all at once"},
        {"label": "Manual Selection", "description": "Show me the conflicts, I'll choose which to apply"}
      ]
    }
  ]
)
```
</user_interaction>

<execution_protocol>

## Phase 1: Load & Parse Review Findings

**Locate and parse the code review artifacts.**

```bash
# Find review artifacts
find . -name "CODE_REVIEW.md" -o -name "REMEDIATION_TASKS.md" 2>/dev/null
```

**Parse findings by category for agent routing:**

```markdown
## Parsed Findings Summary

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| Security | [n] | [n] | [n] | [n] | [n] |
| Performance | [n] | [n] | [n] | [n] | [n] |
| Architecture | [n] | [n] | [n] | [n] | [n] |
| Code Quality | [n] | [n] | [n] | [n] | [n] |
| Test Coverage | [n] | [n] | [n] | [n] | [n] |
| Documentation | [n] | [n] | [n] | [n] | [n] |
| **TOTAL** | [n] | [n] | [n] | [n] | [n] |
```

**→ DECISION POINT 1**: Use AskUserQuestion to confirm severity filter

**→ DECISION POINT 2**: Use AskUserQuestion to confirm categories to remediate

## Phase 2: Conflict Detection

Before deploying agents, analyze for potential conflicts:

```
Conflict Analysis:
- Files targeted by multiple findings: [list]
- Dependent findings (fix A must precede fix B): [list]
- Potentially conflicting fixes: [list]
```

**→ DECISION POINT 5** (if conflicts found): Use AskUserQuestion for conflict resolution strategy

## Phase 3: Parallel Remediation Deployment

Deploy Task tool with appropriate subagent_types based on user selections.

<parallel_remediation>
### Task Deployment Pattern

**IMPORTANT**: Use Task tool with these exact subagent_type values.
Only deploy agents for categories the user selected in Decision Point 2.

```
When SECURITY findings selected:
─────────────────────────────────────────────────────────────────────────
Task(
  subagent_type="security-engineer",
  description="Remediate security findings",
  prompt="You are fixing security vulnerabilities from a code review.

  FINDINGS:
  ${SECURITY_FINDINGS}

  For EACH finding:
  1. READ the file completely to understand context
  2. Implement secure fix:
     - Input validation: Use allowlists, escape outputs
     - Secrets: Move to environment variables
     - SQL: Use parameterized queries
     - Dependencies: Update to patched versions
  3. Add defensive measures beyond the immediate fix
  4. Write/update tests to verify and prevent regression
  5. Document the security consideration

  Output: File modified, changes made, tests added, verification"
)
─────────────────────────────────────────────────────────────────────────

When PERFORMANCE findings selected:
─────────────────────────────────────────────────────────────────────────
Task(
  subagent_type="performance-engineer",
  description="Remediate performance findings",
  prompt="You are fixing performance issues from a code review.

  FINDINGS:
  ${PERFORMANCE_FINDINGS}

  For EACH finding:
  1. READ the file to understand the hot path
  2. Implement optimization:
     - N+1: Add eager loading, batch queries
     - Caching: Add appropriate cache with invalidation
     - Algorithms: Replace O(n²) with O(n) or O(n log n)
     - Memory: Add cleanup, use generators for large data
  3. Ensure optimization doesn't change correctness
  4. Add performance test/benchmark

  Output: File modified, optimization, expected improvement"
)
─────────────────────────────────────────────────────────────────────────

When ARCHITECTURE findings selected:
─────────────────────────────────────────────────────────────────────────
Task(
  subagent_type="refactoring-specialist",
  description="Remediate architecture findings",
  prompt="You are fixing structural issues from a code review.

  FINDINGS:
  ${ARCHITECTURE_FINDINGS}

  For EACH finding:
  1. READ all related files for full context
  2. Plan refactoring:
     - SOLID violations: Apply appropriate principle
     - God classes: Extract focused classes
     - Circular deps: Introduce interfaces
     - Layer violations: Move code to appropriate layer
  3. Execute in small, verifiable steps
  4. Update imports and references
  5. Ensure all tests pass

  Output: Files modified, pattern applied, tests passing"
)
─────────────────────────────────────────────────────────────────────────

When CODE_QUALITY findings selected:
─────────────────────────────────────────────────────────────────────────
Task(
  subagent_type="code-reviewer",
  description="Remediate quality findings",
  prompt="You are fixing code quality issues from a code review.

  FINDINGS:
  ${QUALITY_FINDINGS}

  For EACH finding:
  1. READ the file to understand conventions
  2. Apply fixes:
     - Dead code: Remove after verifying unused
     - DRY: Extract common code
     - Complexity: Break into smaller functions
     - Naming: Apply consistent naming
     - Magic values: Extract to constants
  3. Maintain consistency with surrounding style
  4. Run linter to verify improvements

  Output: File modified, improvement applied, linter results"
)
─────────────────────────────────────────────────────────────────────────
```
</parallel_remediation>

## Phase 4: Supporting Specialists

After primary fixes, deploy supporting specialists:

<supporting_specialists>
```
Task(
  subagent_type="test-automator",
  description="Add tests for fixes",
  prompt="Add tests for all fixes made in this remediation session.

  FILES MODIFIED:
  ${MODIFIED_FILES}

  FIXES APPLIED:
  ${FIX_SUMMARY}

  For each fix:
  1. READ source and existing tests
  2. Write comprehensive tests:
     - Unit tests for each fix
     - Edge cases and error conditions
     - Regression tests preventing reintroduction
  3. Use existing test patterns and fixtures
  4. Aim for meaningful assertions

  Output: Test files created/modified, coverage improvement"
)

Task(
  subagent_type="documentation-engineer",
  description="Update documentation",
  prompt="Update documentation for all changes made.

  CHANGES:
  ${ALL_CHANGES}

  Tasks:
  1. Update docstrings for modified functions
  2. Update README if behavior changed
  3. Add CHANGELOG entry for this remediation
  4. Document any new configuration

  Output: Documentation files updated"
)
```
</supporting_specialists>

## Phase 5: Verification

**→ DECISION POINT 3**: Use AskUserQuestion to determine verification depth

Based on user selection, deploy appropriate verification:

<verification_layer>
### Full Verification (Default)
Deploy all pr-review-toolkit agents + automated checks:

```
PARALLEL VERIFICATION:
─────────────────────────────────────────────────────────────────────────
Task(
  subagent_type="pr-review-toolkit:silent-failure-hunter",
  description="Check for silent failures",
  prompt="Review all files modified in this remediation session.

  MODIFIED FILES:
  ${MODIFIED_FILES}

  Check for:
  - Silent error swallowing
  - Inadequate exception handling
  - Missing error propagation
  - Fallback behavior hiding failures

  Report any silent failure patterns introduced by fixes."
)
─────────────────────────────────────────────────────────────────────────
Task(
  subagent_type="pr-review-toolkit:code-simplifier",
  description="Simplify over-engineered fixes",
  prompt="Review all fixes for over-engineering.

  MODIFIED FILES:
  ${MODIFIED_FILES}

  ORIGINAL ISSUES:
  ${ORIGINAL_FINDINGS}

  Check if any fixes:
  - Added unnecessary complexity
  - Over-abstracted simple problems
  - Introduced premature optimization

  Simplify while preserving functionality."
)
─────────────────────────────────────────────────────────────────────────
Task(
  subagent_type="pr-review-toolkit:pr-test-analyzer",
  description="Analyze test coverage",
  prompt="Analyze test coverage for this remediation.

  NEW/MODIFIED TESTS:
  ${TEST_FILES}

  FIXES APPLIED:
  ${FIX_SUMMARY}

  Verify:
  - All fixes have corresponding tests
  - Edge cases are covered
  - Tests are meaningful (not trivial)

  Report any coverage gaps."
)
─────────────────────────────────────────────────────────────────────────
```

### Quick Verification
Skip pr-review-toolkit, run only automated checks:

```bash
# Run tests
pytest -v || npm test || go test ./...

# Run linters
ruff check . || eslint . || golangci-lint run

# Run type checker
mypy . || tsc --noEmit
```

### Tests Only
```bash
pytest -v || npm test || go test ./...
```
</verification_layer>

## Phase 6: Final Actions

**→ DECISION POINT 4**: Use AskUserQuestion for commit strategy

Based on user selection:
- **Review First**: Leave changes uncommitted, show summary
- **Single Commit**: Stage all and commit with comprehensive message
- **Separate Commits**: Create category-based commits

</execution_protocol>

<report_generation>
## Remediation Report

Generate REMEDIATION_REPORT.md with:

```markdown
# Remediation Report

## Summary
| Metric | Value |
|--------|-------|
| Findings addressed | [X] of [Y] |
| Files modified | [N] |
| Tests added | [N] |
| Verification status | ✅/⚠️/❌ |

## User Selections
- **Severity Filter**: [Critical, High, ...]
- **Categories Remediated**: [Security, Performance, ...]
- **Verification Level**: [Full/Quick/Tests Only/Skipped]
- **Commit Strategy**: [Review First/Single/Separate]

## Agent Deployment Summary

| Agent | Findings | Status |
|-------|----------|--------|
| security-engineer | [N] | ✅ |
| performance-engineer | [N] | ✅ |
| refactoring-specialist | [N] | ✅ |
| code-reviewer | [N] | ✅ |
| test-automator | [N] | ✅ |
| documentation-engineer | [N] | ✅ |

## Verification Results

| Verifier | Result |
|----------|--------|
| silent-failure-hunter | [findings or ✅] |
| code-simplifier | [simplifications or ✅] |
| pr-test-analyzer | [gaps or ✅] |

## Fixes Applied
[Detailed fix log by category]

## Deferred Items
[Items not fixed with reason]
```
</report_generation>

<execution_instruction>
## Execution Sequence

### Step 0: Mode Detection
Check if `--quick` is in $ARGUMENTS:
- **Quick Mode**: Skip AskUserQuestion, use defaults
- **Interactive Mode**: Use AskUserQuestion at each decision point

### Step 1: Environment Verification
```bash
git status --porcelain
git branch --show-current
```

### Step 2: Load Findings
Locate and parse CODE_REVIEW.md or REMEDIATION_TASKS.md

### Step 3: Present Summary & Elicit Input

**Quick Mode:**
1. Show findings summary table
2. Announce quick mode defaults
3. Apply: Severity = Critical + High, Categories = All with findings

**Interactive Mode:**
1. Show findings summary table
2. **AskUserQuestion**: Severity filter (Decision Point 1)
3. **AskUserQuestion**: Category selection (Decision Point 2)

### Step 4: Conflict Analysis
1. Detect overlapping fixes

**Quick Mode:** Use Sequential resolution (safer)
**Interactive Mode:** **AskUserQuestion** (if conflicts): Resolution strategy (Decision Point 5)

### Step 5: Deploy Remediation Agents
Launch parallel Task calls for selected categories

### Step 6: Deploy Supporting Specialists
Launch test-automator and documentation-engineer

### Step 7: Verification

**Quick Mode:** Run tests + linters only (skip pr-review-toolkit)
**Interactive Mode:**
1. **AskUserQuestion**: Verification depth (Decision Point 3)
2. Execute selected verification level

### Step 8: Final Actions

**Quick Mode:** Leave changes uncommitted for review
**Interactive Mode:**
1. **AskUserQuestion**: Commit strategy (Decision Point 4)
2. Execute selected commit approach

### Step 9: Generate Report
Generate REMEDIATION_REPORT.md (both modes)

---

## First Response

### Quick Mode (`--quick` detected)

```
⚡ Running in QUICK MODE

Let me verify the environment and load the code review findings...

[After loading findings, show:]

⚡ QUICK MODE DEFAULTS:
   • Severity: Critical + High ([N] findings)
   • Categories: All with findings
   • Verification: Tests + Linters
   • Commits: Review First (uncommitted)

Proceeding with remediation...
```

### Interactive Mode (no `--quick`)

Begin by:
1. Running pre-flight checks (git status, branch)
2. Locating review artifacts (CODE_REVIEW.md, REMEDIATION_TASKS.md)
3. Parsing findings into category/severity summary table
4. Using **AskUserQuestion** to confirm scope before proceeding

Start with: "Let me verify the environment and load the code review findings..."

### If No Review Artifacts Found (Both Modes)

"I couldn't find CODE_REVIEW.md or REMEDIATION_TASKS.md. Please either:
- Run `/cr` first to generate a code review
- Specify the path to your review file: `/cr-fx path/to/CODE_REVIEW.md`"
</execution_instruction>
