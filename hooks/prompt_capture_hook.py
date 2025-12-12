#!/usr/bin/env python3
"""
Prompt Capture Hook for Claude Code

This hook intercepts UserPromptSubmit events during /arch:* sessions,
filters sensitive content, and logs prompts to PROMPT_LOG.json.

Usage:
    Registered as a UserPromptSubmit hook in Claude Code.
    Receives JSON via stdin, outputs JSON via stdout.

Input format:
    {
        "hook_event_name": "UserPromptSubmit",
        "user_prompt": "string",
        "session_id": "string",
        "cwd": "string",
        "transcript_path": "string"
    }

Output format:
    {
        "decision": "approve",
        "systemMessage": "optional message",
        "additionalContext": "optional context"
    }
"""

import json
import sys
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Edge case limits
MAX_PROMPT_LENGTH = 100000  # 100KB max per prompt to prevent memory issues
MAX_LOG_ENTRY_SIZE = 50000  # Truncate content if over 50KB

# Add hooks directory to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

try:
    from filters.pipeline import filter_pipeline
    from filters.log_entry import LogEntry
    from filters.log_writer import append_to_log
    FILTERS_AVAILABLE = True
except ImportError as e:
    # Filters not available - will pass through without logging
    FILTERS_AVAILABLE = False
    sys.stderr.write(f"prompt_capture_hook: Filter import error: {e}\n")


def pass_through(message: str = "") -> Dict[str, Any]:
    """Return a pass-through response that allows the prompt to proceed."""
    response = {"decision": "approve"}
    if message:
        response["systemMessage"] = message
    return response


def read_input() -> Optional[Dict[str, Any]]:
    """Read and parse JSON input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        # Log error but don't crash - fail open
        sys.stderr.write(f"prompt_capture_hook: JSON decode error: {e}\n")
        return None
    except Exception as e:
        sys.stderr.write(f"prompt_capture_hook: Unexpected error reading input: {e}\n")
        return None


def write_output(response: Dict[str, Any]) -> None:
    """Write JSON response to stdout."""
    try:
        print(json.dumps(response), file=sys.stdout)
    except Exception as e:
        # Fallback to minimal valid response
        sys.stderr.write(f"prompt_capture_hook: Error writing output: {e}\n")
        print('{"decision": "approve"}', file=sys.stdout)


def find_active_project_dir(cwd: str) -> Optional[str]:
    """
    Find the active architecture project directory that has logging enabled.

    Searches for .prompt-log-enabled marker in docs/architecture/active/*/.

    Args:
        cwd: Current working directory (project root)

    Returns:
        Path to the project directory if found and enabled, None otherwise
    """
    if not cwd:
        return None

    active_dir = os.path.join(cwd, "docs", "architecture", "active")

    if not os.path.isdir(active_dir):
        return None

    try:
        for project_folder in os.listdir(active_dir):
            project_path = os.path.join(active_dir, project_folder)
            if os.path.isdir(project_path):
                marker_path = os.path.join(project_path, ".prompt-log-enabled")
                if os.path.isfile(marker_path):
                    return project_path
    except OSError:
        # Permission error or other filesystem issue
        return None

    return None


def is_logging_enabled(cwd: str) -> bool:
    """
    Check if prompt logging is enabled for the current project.

    Logging is enabled if a .prompt-log-enabled file exists in an active
    architecture project directory under docs/architecture/active/.

    Args:
        cwd: Current working directory

    Returns:
        True if logging is enabled, False otherwise
    """
    return find_active_project_dir(cwd) is not None


def is_arch_context(input_data: Dict[str, Any]) -> bool:
    """
    Detect if current session is within /arch:* command context.

    Detection strategies:
    1. Check if user_prompt starts with /arch:
    2. Check transcript for recent /arch: commands
    3. Check for arch command markers in session

    Args:
        input_data: Hook input containing user_prompt, transcript_path, etc.

    Returns:
        True if in an /arch:* session, False otherwise
    """
    user_prompt = input_data.get("user_prompt", "")

    # Strategy 1: Direct command detection
    # Check if user is running an /arch: command right now
    if user_prompt.strip().startswith("/arch:"):
        return True

    # Strategy 2: Check transcript for recent /arch: activity
    # This catches follow-up prompts within an /arch session
    transcript_path = input_data.get("transcript_path", "")
    if transcript_path and os.path.isfile(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                # Read last 50KB of transcript (recent context)
                f.seek(0, 2)  # Go to end
                file_size = f.tell()
                read_size = min(file_size, 50 * 1024)
                f.seek(max(0, file_size - read_size))
                recent_content = f.read()

                # Look for /arch: command patterns
                arch_patterns = [
                    "/arch:p",
                    "/arch:i",
                    "/arch:s",
                    "/arch:c",
                    "/arch:log",
                    "arch:p is running",
                    "arch:i is running",
                    "arch:s is running",
                    "arch:c is running",
                ]
                for pattern in arch_patterns:
                    if pattern in recent_content:
                        return True
        except (OSError, IOError):
            # Can't read transcript - assume not in arch context
            pass

    return False


def truncate_content(content: str, max_length: int = MAX_LOG_ENTRY_SIZE) -> str:
    """Truncate content if too long, preserving information about truncation."""
    if len(content) <= max_length:
        return content
    # Keep first portion and add truncation notice
    truncate_notice = f"\n...[TRUNCATED: {len(content) - max_length + 100} chars removed]..."
    return content[:max_length - len(truncate_notice)] + truncate_notice


def generate_session_id() -> str:
    """Generate a unique session ID if none provided."""
    return f"hook-{uuid.uuid4().hex[:12]}"


def main() -> None:
    """Main entry point for the prompt capture hook."""
    # Read input
    input_data = read_input()

    if input_data is None:
        # Malformed input - fail open
        write_output(pass_through())
        return

    # Extract fields with defaults
    cwd = input_data.get("cwd", "")
    user_prompt = input_data.get("user_prompt", "")
    session_id = input_data.get("session_id", "") or generate_session_id()

    # Edge case: empty prompt
    if not user_prompt or not user_prompt.strip():
        write_output(pass_through())
        return

    # Edge case: extremely long prompt
    if len(user_prompt) > MAX_PROMPT_LENGTH:
        user_prompt = truncate_content(user_prompt, MAX_PROMPT_LENGTH)

    # Check if logging is enabled
    if not is_logging_enabled(cwd):
        write_output(pass_through())
        return

    # Check if we're in an /arch:* context
    if not is_arch_context(input_data):
        write_output(pass_through())
        return

    # Get project directory for logging
    project_dir = find_active_project_dir(cwd)
    if not project_dir:
        write_output(pass_through())
        return

    # Check if filters are available
    if not FILTERS_AVAILABLE:
        write_output(pass_through())
        return

    # Detect /arch: command if present
    command = None
    prompt_stripped = user_prompt.strip()
    if prompt_stripped.startswith("/arch:"):
        # Extract command (e.g., "/arch:p" from "/arch:p some args")
        parts = prompt_stripped.split(None, 1)
        if parts:
            command = parts[0]

    # Filter the prompt content
    filter_result = filter_pipeline(user_prompt)

    # Truncate filtered content if still too long for log
    log_content = truncate_content(filter_result.filtered_text, MAX_LOG_ENTRY_SIZE)

    # Create and write log entry
    entry = LogEntry.create(
        session_id=session_id,
        entry_type="user_input",
        content=log_content,
        command=command,
        cwd=cwd,
        filter_info=filter_result.to_filter_info()
    )

    success = append_to_log(project_dir, entry)

    if success:
        write_output(pass_through())
    else:
        # Log write failed but don't block user
        write_output(pass_through())


if __name__ == "__main__":
    main()
