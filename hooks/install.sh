#!/bin/bash
# Prompt Capture Hook Installation Script
# Run this after cloning the repo or updating the hookify plugin

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${HOME}/.claude"
HOOKIFY_PLUGIN_DIR="${CLAUDE_DIR}/plugins/cache/claude-code-plugins/hookify/0.1.0"

echo "=== Prompt Capture Hook Installation ==="
echo ""

# Check if we're in the right place
if [[ ! -f "${SCRIPT_DIR}/prompt_capture_hook.py" ]]; then
    echo "Error: prompt_capture_hook.py not found in ${SCRIPT_DIR}"
    echo "Make sure you're running this from the hooks/ directory"
    exit 1
fi

# Check if hookify plugin exists
if [[ ! -d "${HOOKIFY_PLUGIN_DIR}" ]]; then
    echo "Warning: Hookify plugin not found at ${HOOKIFY_PLUGIN_DIR}"
    echo "Install the hookify plugin first, then re-run this script."
    echo ""
    echo "The hook files are already in place at ~/.claude/hooks/"
    echo "Once hookify is installed, run:"
    echo "  cp -r ~/.claude/patches/hookify-0.1.0/* ${HOOKIFY_PLUGIN_DIR}/"
    exit 0
fi

# Apply hookify patch
echo "Applying hookify patch..."
if [[ -d "${CLAUDE_DIR}/patches/hookify-0.1.0" ]]; then
    cp -r "${CLAUDE_DIR}/patches/hookify-0.1.0/"* "${HOOKIFY_PLUGIN_DIR}/"
    echo "✓ Hookify patched successfully"
else
    echo "Warning: Patch directory not found at ${CLAUDE_DIR}/patches/hookify-0.1.0"
    echo "The hooks.json needs to be manually updated to include prompt_capture_hook.py"
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Usage:"
echo "  /arch:log on      - Enable prompt logging for active project"
echo "  /arch:log off     - Disable prompt logging"
echo "  /arch:log status  - Check logging status"
echo "  /arch:log show    - Show recent log entries"
echo ""
echo "Logs are stored in PROMPT_LOG.json within each architecture project."
echo "They are automatically analyzed when you run /arch:c to close a project."
