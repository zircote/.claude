---
argument-hint: "on|off|status|show"
description: "Toggle prompt logging for architecture work"
---

# /arch:log - Prompt Logging Control

<role>
You manage prompt logging for architecture projects. You can enable/disable logging and display log status/contents.
</role>

<command_argument>
$ARGUMENTS
</command_argument>

<execution>
## Parse Command

Based on the argument provided:

### `on` - Enable logging
1. Find the active architecture project in `docs/architecture/active/`
2. Create `.prompt-log-enabled` marker file in the project directory
3. Confirm logging is enabled

### `off` - Disable logging
1. Find the active architecture project
2. Remove `.prompt-log-enabled` marker file
3. Confirm logging is disabled

### `status` - Show current status
1. Check if `.prompt-log-enabled` exists in any active project
2. Report logging status and project name
3. Show log file size if exists

### `show` - Display recent log entries
1. Find PROMPT_LOG.json in the active project
2. Display last 10 entries in readable format
3. Show summary statistics

## Implementation

Execute the appropriate action based on the argument:

```bash
# Find active project
ACTIVE_DIR="docs/architecture/active"
PROJECT_DIR=$(find "$ACTIVE_DIR" -maxdepth 1 -type d ! -name "active" | head -1)

if [ -z "$PROJECT_DIR" ]; then
    echo "No active architecture project found"
    exit 0
fi

PROJECT_NAME=$(basename "$PROJECT_DIR")
MARKER_FILE="$PROJECT_DIR/.prompt-log-enabled"
LOG_FILE="$PROJECT_DIR/PROMPT_LOG.json"
```

For `on`:
```bash
touch "$MARKER_FILE"
echo "✓ Prompt logging enabled for: $PROJECT_NAME"
```

For `off`:
```bash
rm -f "$MARKER_FILE"
echo "✓ Prompt logging disabled for: $PROJECT_NAME"
```

For `status`:
```bash
if [ -f "$MARKER_FILE" ]; then
    echo "📝 Logging: ENABLED"
else
    echo "📝 Logging: DISABLED"
fi
echo "📂 Project: $PROJECT_NAME"
if [ -f "$LOG_FILE" ]; then
    ENTRIES=$(wc -l < "$LOG_FILE")
    SIZE=$(du -h "$LOG_FILE" | cut -f1)
    echo "📊 Log entries: $ENTRIES ($SIZE)"
fi
```

For `show`:
- Read PROMPT_LOG.json
- Parse NDJSON entries
- Display last 10 entries formatted nicely

## Response Format

After executing the command, provide a clear confirmation message.
</execution>
