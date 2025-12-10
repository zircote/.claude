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

**Usage**: Read the relevant include file(s) at the start of environment-specific tasks to ensure compliance with standards.

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

## MCP Query Pagination
- Start with limit=20; estimate tokens per item from a small probe.
- Never exceed ~20k tokens; paginate if needed; split by team/filters if large.
- Provide partial results with clear notice when truncated.
- On "exceeds maximum allowed tokens": drop limit to 10, paginate, report "Retrieved X of Y due to token limits".
- Pattern:
```python
# Recon
probe = tool_call(limit=5)
tokens_per_item = estimate(probe) / 5
safe_limit = min(15000 / tokens_per_item, 50)

# Batches (max 5)
results = []
for i in range(5):
    batch = tool_call(limit=safe_limit, offset=i * safe_limit)
    if tokens(batch) > 20000: break
    results.extend(batch)
```

## Systems Environments
The ONLY environments that exists are NO OTHERS EVER UNLESS I EXPLICITLY STATE OTHERWISE:
- prod
- cert
- int
- dev

## Prohibited Services (HMHCO)

**Slack is NOT used at HMHCO.** Never include Slack in:
- Code implementations or examples
- GitHub Actions workflows (no slack-notify, slack-webhook actions)
- Notification pathways or alerting configurations
- Documentation examples
- CI/CD pipelines

**Microsoft Teams is the standard communication platform.** Use Teams for:
- CI/CD notifications and alerts
- Workflow status updates
- Team communications and integrations

## Memory Agent MCP
- Pass the user query EXACTLY as written (no paraphrasing).
- Use proactively for: personal info/preferences/history, entities/projects mentioned before, "Did I…"/"What did I say…" questions.
- Not for: general knowledge, real‑time data, math/logic, hypothetical topics.
- Integrate results naturally; if missing, say so and offer options; combine with general knowledge.
- Filters: agent auto-applies from .filters; only add tags if user includes them.
- Errors: check memory dir structure and user.md; suggest reconnect; offer to proceed without memory.
- Key: pass unmodified; use proactively when helpful; don’t announce "checking memory".

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
