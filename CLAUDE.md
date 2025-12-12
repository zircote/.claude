# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# Global Claude Instructions — Concise

**ALWAYS** ask questions when producing a plan until you have reached 95% or GREATER confidence. ALWAYS DO THIS.

These rules guide Claude across projects. Preserve protocols; keep wording minimal.

## Environment & Standards Includes

When working in these environments, read and follow the corresponding file:

| Environment | Include File |
|-------------|--------------|
| Python | `~/.claude/includes/python.md` |
| React/TypeScript | `~/.claude/includes/react.md` |
| Go | `~/.claude/includes/golang.md` |
| Git/Version Control | `~/.claude/includes/git.md` |
| Testing (any language) | `~/.claude/includes/testing.md` |
| Documentation | `~/.claude/includes/documentation.md` |
| MCP Tools/Skills/Agents | `~/.claude/includes/mcp-reference.md` |
| GitHub Actions | `~/.claude/includes/github-actions.md` |
| Version Discovery | `~/.claude/includes/version-discovery.md` |
| Opus 4.5 (General) | `~/.claude/includes/opus-4-5.md` |
| Opus 4.5 (Agentic) | `~/.claude/includes/opus-4-5-agent.md` |
| HMHCO Organization | `~/.claude/includes/hmhco.md` |

**Usage**: Read the relevant include file(s) at the start of environment-specific tasks to ensure compliance with standards.

## Custom Commands

### Git Workflow (`/git`)

| Command | Description |
|---------|-------------|
| `/git:cm` | Stage all files and create a commit (conventional commits, splits new vs modified) |
| `/git:cp` | Stage, commit, and push all changes |
| `/git:pr [to-branch]` | Create a pull request using `gh` CLI |

### Architecture Planning (`/arch`)

| Command | Description |
|---------|-------------|
| `/arch:p <project-idea>` | Strategic project planner with Socratic requirements elicitation, PRD, and implementation plan |
| `/arch:s [project-id\|--list\|--expired]` | Project status, portfolio listing, find expired plans |
| `/arch:c <project-path\|project-id>` | Close out completed project, archive artifacts, generate retrospective |

Workflow: `/arch:p` to plan → `/arch:s` to monitor → `/arch:c` to complete

### Opus 4.5 Optimized

| Command | Description |
|---------|-------------|
| `/explore <path\|pattern\|question>` | Exhaustive codebase exploration with parallel subagents and anti-hallucination enforcement |
| `/deep-research <topic\|url>` | Multi-phase research protocol with structured deliverables and quality gates |

## Git Worktree Management

**Always use the `worktree-manager` skill** for ALL git worktree operations. This is the ONLY approved method.

Trigger phrases: "create worktree", "spin up worktrees", "worktree status", "cleanup worktrees"

**Initial prompt support**: Add `with prompt "template"` to auto-execute tasks in each worktree:
```
spin up worktrees for auth, payments with prompt "run tests for {{service}}"
```
Template variables: `{{service}}`, `{{branch}}`, `{{project}}`, `{{port}}`, `{{ports}}`

**DO NOT** use raw `git worktree` commands directly or create ad-hoc worktree workflows.

## Plugin Maintenance

Plugin patches are stored in `~/.claude/patches/`. After plugin updates, reapply patches:
```bash
cp -r ~/.claude/patches/<plugin>-<version>/* ~/.claude/plugins/cache/claude-code-plugins/<plugin>/<version>/
```

For detailed repository structure, see `~/.claude/llms.txt`.

## Skills Quick Reference

Skills are in `~/.claude/skills/`. Key categories:
- **Documents**: `pdf`, `docx`, `xlsx`, `pptx`
- **Media**: `ai-multimodal`, `media-processing`, `chrome-devtools`
- **Development**: `frontend-development`, `backend-development`, `databases`, `devops`
- **AI/Prompting**: `anthropic-prompt-engineer`, `anthropic-architect`
- **Utilities**: `docs-seeker`, `changelog-generator`, `mcp-builder`

Invoke via Skill tool or trigger phrases defined in each skill's `SKILL.md`.

## Opus 4.5 Quick Reference

Key behaviors when running as Opus 4.5:
- **Word sensitivity**: Avoid "think" when extended thinking disabled; use "consider", "evaluate", "believe"
- **Tool triggering**: More responsive than previous models—use normal phrasing, avoid "CRITICAL: MUST"
- **Subagent orchestration**: Proactively delegates to subagents when beneficial (native capability)
- **State discovery**: Excels at discovering state from filesystem—prefer fresh context over compaction
- **Git for state**: Use git logs and structured files (tests.json, progress.txt) for multi-session tasks
- **Investigate first**: Read files before answering—no speculation about unread code

## Parallel Specialist Subagents
Leverage the Task tool with specialized subagents from `~/.claude/agents/` for efficiency.

### Agent Categories (`~/.claude/agents/`)
| Category | Specialists | Use For |
|----------|-------------|---------|
| `01-core-development` | frontend-developer, backend-developer, fullstack-developer, api-designer, microservices-architect, mobile-developer | Application architecture, API design, UI/UX implementation |
| `02-language-specialists` | python-pro, typescript-pro, golang-pro, rust-engineer, java-architect, react-specialist, nextjs-developer | Language-specific implementation, framework expertise |
| `03-infrastructure` | devops-engineer, sre-engineer, kubernetes-specialist, terraform-engineer, cloud-architect, database-administrator | Infrastructure, deployment, cloud, networking |
| `04-quality-security` | code-reviewer, security-auditor, penetration-tester, test-automator, performance-engineer, debugger | Code quality, security analysis, testing, debugging |
| `05-data-ai` | data-scientist, data-engineer, ml-engineer, llm-architect, postgres-pro, prompt-engineer | Data pipelines, ML/AI, database optimization |
| `06-developer-experience` | documentation-engineer, cli-developer, build-engineer, refactoring-specialist, mcp-developer | DX tooling, documentation, build systems |
| `07-specialized-domains` | fintech-engineer, blockchain-developer, game-developer, iot-engineer, payment-integration | Domain-specific expertise |
| `08-business-product` | product-manager, technical-writer, ux-researcher, scrum-master | Product, documentation, process |
| `09-meta-orchestration` | multi-agent-coordinator, workflow-orchestrator, task-distributor | Complex multi-agent workflows |
| `10-research-analysis` | research-analyst, competitive-analyst, market-researcher, trend-analyst | Research, analysis, market intelligence |

### Parallel Execution Rules
- **When to parallelize**: Launch multiple specialists simultaneously when tasks are independent (no output dependencies)
- **Specialist matching**: Route work to the most domain-appropriate agent from `~/.claude/agents/`
- **Dependency awareness**: Only serialize when one agent's output informs another's parameters
- **Consolidation**: Synthesize parallel agent results into a unified response

### Example Patterns
```
PARALLEL: Full-stack feature with security review
→ Launch frontend-developer + backend-developer + security-auditor simultaneously

PARALLEL: Infrastructure + monitoring setup
→ Launch terraform-engineer + sre-engineer + devops-engineer in parallel

PARALLEL: Code quality sweep
→ Launch code-reviewer + performance-engineer + test-automator together

SEQUENTIAL: Research → Implementation
→ research-analyst completes → use findings to guide python-pro implementation

SEQUENTIAL: Design → Build → Review
→ api-designer → backend-developer → code-reviewer (each depends on prior output)
```

Prefer parallel specialist agents over sequential single-threaded work when the task naturally decomposes into independent expert domains.

## API Response Validation
- Treat unexpected empties as suspicious. Do not proceed.
- Steps: STOP → try minimal query → ask user to confirm → document quirk in ~/.claude/learnings/.
- Indicators: user says data exists but API returns 0/empty/null; complex query fails; added filters break.
- Fallback:
```python
r = api_call(complex_params)
if not r and context_suggests_data:
    s = api_call(minimal_params)
    if s: warn_user("Complex query 0, using simplified"); use s
    else: ask_user("API shows 0 — match your UI?")
```
- Be honest: state "API returned 0"; list causes; try alternatives; ask for UI confirmation.
- When actually missing:
```
"The [tool] shows no [data] for the period.
Possible reasons: (1) most likely, (2) alternative, (3) unlikely.
Next: actionable step(s)."
```
- Document quirks: symptom, workaround, date, failing vs working example.
- Golden rule: when in doubt about data quality → ASK THE USER.
