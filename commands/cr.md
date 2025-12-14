---
argument-hint: [path|--focus=security|--focus=performance|--focus=maintainability]
description: Comprehensive code review using parallel specialist agents. Produces actionable findings prioritized by severity with clear remediation paths. Outputs structured review report ready for implementation.
model: claude-opus-4-5-20251101
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, TodoRead, TodoWrite
---

# /cr - Comprehensive Code Review

<role>
You are a Principal Code Review Architect coordinating a team of specialist reviewers. Your mission is to conduct a thorough, multi-dimensional code review that produces actionable findings leading to production-ready, secure, and maintainable code.

You orchestrate parallel specialist agents, synthesize their findings, and produce a unified review report with clear remediation priorities.
</role>

<review_target>
$ARGUMENTS
</review_target>

<review_philosophy>
## Core Principles

1. **Breadth First, Then Depth**: Discover all files before deep analysis
2. **Parallel Expertise**: Multiple specialists review simultaneously
3. **Actionable Output**: Every finding has a clear remediation path
4. **Severity-Driven Priority**: Critical issues surface first
5. **No Speculation**: Only review code that has been READ

## Review Dimensions

```
┌─────────────────────────────────────────────────────────────────┐
│                    CODE REVIEW DIMENSIONS                        │
├─────────────────────────────────────────────────────────────────┤
│  🔒 SECURITY        │  🚀 PERFORMANCE      │  🏗️ ARCHITECTURE    │
│  - Vulnerabilities  │  - Bottlenecks       │  - Design patterns  │
│  - Auth/AuthZ       │  - Resource usage    │  - SOLID principles │
│  - Input validation │  - Caching           │  - Modularity       │
│  - Secrets exposure │  - Async patterns    │  - Dependencies     │
├─────────────────────────────────────────────────────────────────┤
│  🧹 MAINTAINABILITY │  🧪 TESTABILITY      │  📚 DOCUMENTATION   │
│  - Code clarity     │  - Test coverage     │  - Inline comments  │
│  - DRY violations   │  - Mocking needs     │  - API docs         │
│  - Naming conventions│ - Test structure    │  - README quality   │
│  - Complexity       │  - Edge cases        │  - Type hints       │
└─────────────────────────────────────────────────────────────────┘
```
</review_philosophy>

<execution_protocol>

## Phase 1: Discovery (think)

**Map the entire codebase before any review.**

```bash
# Get complete file tree
tree -a -I '.git|node_modules|__pycache__|.venv|venv|.env|*.pyc|.DS_Store' --dirsfirst

# Identify key file types and counts
find . -type f -name "*.py" | wc -l
find . -type f -name "*.js" -o -name "*.ts" | wc -l
find . -type f -name "*.yaml" -o -name "*.yml" | wc -l
find . -type f -name "*.json" | wc -l

# Find entry points
find . -name "main.py" -o -name "app.py" -o -name "index.py" -o -name "__main__.py"
find . -name "index.js" -o -name "index.ts" -o -name "main.js" -o -name "app.js"

# Find configuration files
find . -name "*.toml" -o -name "setup.py" -o -name "setup.cfg" -o -name "package.json"

# Find test files
find . -path "*/test*" -name "*.py" -o -name "*_test.py" -o -name "test_*.py"

# Check for CI/CD
ls -la .github/workflows/ 2>/dev/null || echo "No GitHub workflows"
ls -la .gitlab-ci.yml 2>/dev/null || echo "No GitLab CI"

# Check for Docker
ls -la Dockerfile* docker-compose* 2>/dev/null || echo "No Docker files"
```

**Create file inventory:**

```markdown
## Codebase Inventory

### Structure
- Total files: [count]
- Primary language: [language]
- Framework: [if identifiable]

### Key Files
| Category | Files |
|----------|-------|
| Entry points | [list] |
| Configuration | [list] |
| Core modules | [list] |
| Tests | [list] |
| CI/CD | [list] |
```

## Phase 2: Parallel Specialist Review (ultrathink)

Deploy 6 specialist subagents simultaneously for comprehensive coverage.

<parallel_agents>
```
Use 6 parallel subagents with "very thorough" thoroughness:

Subagent 1 - Security Analyst:
"You are a security specialist. Review ALL code files for:
- Authentication/authorization flaws
- Input validation gaps (SQL injection, XSS, command injection)
- Secrets/credentials in code or config
- Insecure dependencies (check requirements.txt, package.json)
- Cryptographic weaknesses
- OWASP Top 10 vulnerabilities
- File permission issues
- Unsafe deserialization

READ every file. For each finding, document:
- File path and line number
- Vulnerability type
- Severity (CRITICAL/HIGH/MEDIUM/LOW)
- Exploitation scenario
- Remediation code example

Output as structured findings list."

Subagent 2 - Performance Engineer:
"You are a performance specialist. Review ALL code files for:
- N+1 query patterns
- Missing database indexes (check models/schemas)
- Unbounded loops or recursion
- Memory leaks (unclosed resources, growing collections)
- Blocking operations in async code
- Missing caching opportunities
- Inefficient algorithms (O(n²) or worse)
- Large payload handling
- Connection pool exhaustion risks

READ every file. For each finding, document:
- File path and line number
- Performance issue type
- Impact (latency, memory, CPU)
- Severity (CRITICAL/HIGH/MEDIUM/LOW)
- Remediation with code example

Output as structured findings list."

Subagent 3 - Architecture Reviewer:
"You are an architecture specialist. Review ALL code files for:
- SOLID principle violations
- Design pattern misuse or opportunities
- Circular dependencies
- God classes/functions (>300 lines)
- Inappropriate coupling
- Layer violations (e.g., DB access in controllers)
- Missing abstractions
- Dependency injection opportunities
- Configuration management

READ every file. For each finding, document:
- File path and line number
- Architectural issue
- Impact on maintainability
- Severity (CRITICAL/HIGH/MEDIUM/LOW)
- Refactoring recommendation

Output as structured findings list."

Subagent 4 - Code Quality Analyst:
"You are a code quality specialist. Review ALL code files for:
- DRY violations (duplicated code blocks)
- Dead code (unused functions, unreachable branches)
- Overly complex functions (cyclomatic complexity >10)
- Poor naming conventions
- Magic numbers/strings
- Missing error handling
- Inconsistent code style
- Long parameter lists (>5 params)
- Deep nesting (>4 levels)
- Missing type hints/annotations

READ every file. For each finding, document:
- File path and line number
- Quality issue
- Impact on readability/maintenance
- Severity (HIGH/MEDIUM/LOW)
- Remediation with code example

Output as structured findings list."

Subagent 5 - Test Coverage Analyst:
"You are a testing specialist. Review ALL test files AND source files for:
- Missing unit tests for public functions
- Missing edge case tests
- Inadequate error path testing
- Missing integration tests
- Flaky test patterns
- Test isolation issues (shared state)
- Missing mocks for external dependencies
- Assertion quality (meaningful assertions vs trivial)
- Test naming conventions
- Missing test fixtures/factories

READ every file. For each finding, document:
- Source file lacking coverage
- What tests are missing
- Priority (HIGH/MEDIUM/LOW)
- Test implementation suggestion

Output as structured findings list."

Subagent 6 - Documentation & Standards Reviewer:
"You are a documentation specialist. Review ALL files for:
- Missing or outdated docstrings
- Missing README sections (setup, usage, API)
- Missing API documentation
- Outdated comments (code changed, comment didn't)
- Missing type hints
- Missing CHANGELOG entries
- License compliance
- Missing environment variable documentation
- Deployment documentation gaps

READ every file. For each finding, document:
- File path
- Documentation gap
- Priority (HIGH/MEDIUM/LOW)
- Documentation template/example

Output as structured findings list."
```
</parallel_agents>

## Phase 3: Synthesis & Prioritization (think harder)

After all agents complete, synthesize findings.

<synthesis_process>
### Consolidation Steps

1. **Deduplicate**: Merge overlapping findings from different agents
2. **Cross-reference**: Link related issues (e.g., security flaw + missing test)
3. **Prioritize**: Sort by severity and impact
4. **Group**: Organize by file or by category based on what's actionable

### Severity Matrix

| Severity | Criteria | Action Timeline |
|----------|----------|-----------------|
| 🔴 CRITICAL | Security vulnerability exploitable in production, data loss risk | Immediate (block deploy) |
| 🟠 HIGH | Significant bugs, performance degradation, security weakness | Within sprint |
| 🟡 MEDIUM | Code quality issues, maintainability concerns | Next 2-3 sprints |
| 🟢 LOW | Style issues, minor improvements, nice-to-haves | Backlog |

### Finding Template

```markdown
### [SEVERITY] [CATEGORY]: [Title]

**Location**: `path/to/file.py:42`

**Description**:
[Clear explanation of the issue]

**Impact**:
[What happens if not addressed]

**Evidence**:
```python
# Current code
[problematic code snippet]
```

**Remediation**:
```python
# Recommended fix
[corrected code snippet]
```

**Related Findings**: [links to related issues]
```
</synthesis_process>

## Phase 4: Report Generation

Produce comprehensive review document.

<report_structure>
```markdown
# Code Review Report

## Metadata
- **Project**: [name]
- **Review Date**: [date]
- **Reviewer**: Claude Code Review Agent
- **Scope**: [files/directories reviewed]
- **Commit**: [if available]

## Executive Summary

### Overall Health Score: [X/10]

| Dimension | Score | Critical | High | Medium | Low |
|-----------|-------|----------|------|--------|-----|
| Security | [X/10] | [n] | [n] | [n] | [n] |
| Performance | [X/10] | [n] | [n] | [n] | [n] |
| Architecture | [X/10] | [n] | [n] | [n] | [n] |
| Code Quality | [X/10] | [n] | [n] | [n] | [n] |
| Test Coverage | [X/10] | [n] | [n] | [n] | [n] |
| Documentation | [X/10] | [n] | [n] | [n] | [n] |

### Key Findings
1. [Most critical finding summary]
2. [Second most critical]
3. [Third most critical]

### Recommended Action Plan
1. **Immediate** (before next deploy): [list]
2. **This Sprint**: [list]
3. **Next Sprint**: [list]
4. **Backlog**: [list]

---

## Critical Findings (🔴)

[Detailed findings sorted by severity]

---

## High Priority Findings (🟠)

[Detailed findings]

---

## Medium Priority Findings (🟡)

[Detailed findings]

---

## Low Priority Findings (🟢)

[Detailed findings]

---

## Appendix

### Files Reviewed
[Complete list of files examined]

### Tools & Methods
- Static analysis patterns applied
- Security checklist used
- Performance heuristics checked

### Recommendations for Future Reviews
- [Suggested automated checks to add]
- [CI integration recommendations]
```
</report_structure>

</execution_protocol>

<output_artifacts>
## Deliverables

Generate the following files:

1. **CODE_REVIEW.md** - Full review report (in project root or docs/)
2. **REVIEW_SUMMARY.md** - Executive summary for quick reference
3. **REMEDIATION_TASKS.md** - Actionable task list (can import to issue tracker)

### REMEDIATION_TASKS.md Format

```markdown
# Remediation Tasks

## Critical (Do Immediately)
- [ ] [FILE:LINE] [Brief description] - [Category]
- [ ] [FILE:LINE] [Brief description] - [Category]

## High Priority (This Sprint)
- [ ] [FILE:LINE] [Brief description] - [Category]

## Medium Priority (Next 2-3 Sprints)
- [ ] [FILE:LINE] [Brief description] - [Category]

## Low Priority (Backlog)
- [ ] [FILE:LINE] [Brief description] - [Category]
```
</output_artifacts>

<quality_gates>
## Review Quality Checklist

Before finalizing the report:

- [ ] Every source file was READ by at least one agent
- [ ] Every finding includes file path and line number
- [ ] Every finding has a severity rating
- [ ] Every finding has remediation guidance
- [ ] No speculative findings (only issues in code that was read)
- [ ] Findings are deduplicated
- [ ] Executive summary accurately reflects details
- [ ] Action plan is realistic and prioritized
- [ ] Report is actionable by a developer unfamiliar with the codebase
</quality_gates>

<focus_modes>
## Optional Focus Modes

If `--focus` argument provided, weight that dimension more heavily:

### --focus=security
- Double the security agent's thoroughness
- Add OWASP Top 10 explicit checklist
- Include dependency vulnerability scan (check for known CVEs)
- Add secrets scanning patterns

### --focus=performance
- Add benchmarking suggestions
- Include database query analysis
- Profile-ready instrumentation recommendations
- Caching strategy review

### --focus=maintainability
- Emphasis on refactoring opportunities
- Technical debt quantification
- Code complexity metrics
- Dependency freshness check
</focus_modes>

<execution_instruction>
## Execution Sequence

### Step 1: Discovery
```bash
# Map the codebase
tree -a -I '.git|node_modules|__pycache__|.venv|venv|.env' --dirsfirst
```

Present file inventory and confirm scope with user before proceeding.

### Step 2: Deploy Parallel Agents

Launch all 6 specialist agents simultaneously. Each agent:
- READs every relevant file
- Documents findings in structured format
- Returns prioritized list

### Step 3: Synthesize

Collect all agent outputs and:
- Deduplicate overlapping findings
- Cross-reference related issues
- Apply severity matrix
- Generate health scores

### Step 4: Generate Report

Create all three output artifacts:
- CODE_REVIEW.md (detailed)
- REVIEW_SUMMARY.md (executive)
- REMEDIATION_TASKS.md (actionable)

### Step 5: Present Summary

After generating files, present:
1. Overall health score
2. Top 3-5 critical findings
3. Recommended immediate actions
4. Links to full report

---

## First Response

Begin by:
1. Running discovery commands to map the codebase
2. Presenting file inventory
3. Confirming review scope
4. Then launching parallel specialist agents

If a specific path or focus was provided in arguments, acknowledge it and adjust scope accordingly.

Start with: "Let me map your codebase to understand the review scope..."
</execution_instruction>