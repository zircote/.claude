# Hookify Plugin Patch (v0.1.0)

## Problem
The hookify plugin hooks fail with `No module named 'hookify'` because:
1. The hooks use `CLAUDE_PLUGIN_ROOT` environment variable to set up Python import paths
2. Claude Code expands `${CLAUDE_PLUGIN_ROOT}` in the command string but does NOT export it as an env var
3. The Python scripts see `None` for `os.environ.get('CLAUDE_PLUGIN_ROOT')`

## Fix
Changed all hook scripts to derive the plugin path from `__file__` instead of relying on the environment variable, and updated imports from package-style (`from hookify.core...`) to relative-style (`from core...`).

## Files Patched
- `hooks/pretooluse.py`
- `hooks/posttooluse.py`
- `hooks/stop.py`
- `hooks/userpromptsubmit.py`
- `hooks/hooks.json` - Added prompt_capture_hook to UserPromptSubmit chain
- `core/rule_engine.py`

## Prompt Capture Hook Addition (2025-12-12)
Added `~/.claude/hooks/prompt_capture_hook.py` to the UserPromptSubmit hook chain.
This hook captures prompts during /arch:* sessions for retrospective analysis.
See: ARCH-2025-12-12-002 (Prompt Capture Log)

## To Restore After Plugin Update
```bash
cp -r ~/.claude/patches/hookify-0.1.0/* ~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0/
```

## Date
2024-12-11
