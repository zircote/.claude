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
| Opus 4.5 | `~/.claude/includes/opus-4-5.md` |

**Usage**: Read the relevant include file(s) at the start of environment-specific tasks to ensure compliance with standards.

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
