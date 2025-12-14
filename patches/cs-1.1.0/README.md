# cs Plugin Patch v1.1.0

## Issue Fixed
The plugin manifest had `"hooks": "../hooks/hooks.json"` which violates the validation rule that hooks paths must start with `./`.

## Changes
1. `.claude-plugin/plugin.json` - Changed hooks path to `"./hooks/hooks.json"`
2. `.claude-plugin/hooks/` directory - Created with symlink to actual hooks.json

## Apply Patch
After plugin update, run:
```bash
# Copy patched manifest
cp ~/.claude/patches/cs-1.1.0/.claude-plugin/plugin.json \
   ~/.claude/plugins/cache/claude-spec-marketplace/cs/*/. claude-plugin/

# Create hooks symlink
cd ~/.claude/plugins/cache/claude-spec-marketplace/cs/*/.claude-plugin
mkdir -p hooks
ln -sf ../../hooks/hooks.json hooks/hooks.json
```

## Date
2024-12-13
