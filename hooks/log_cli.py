#!/usr/bin/env python3
"""
CLI utility for prompt capture logging.

Allows /arch commands to log expanded prompts and response summaries
directly from shell scripts or command definitions.

Usage:
    python3 ~/.claude/hooks/log_cli.py expanded "The expanded prompt content..."
    python3 ~/.claude/hooks/log_cli.py response "Response summary text..."
    python3 ~/.claude/hooks/log_cli.py status
"""

import argparse
import os
import sys
from typing import Optional

# Add hooks directory to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

try:
    from filters.pipeline import filter_pipeline
    from filters.log_entry import LogEntry
    from filters.log_writer import append_to_log, PROMPT_LOG_FILENAME
    FILTERS_AVAILABLE = True
except ImportError as e:
    FILTERS_AVAILABLE = False
    print(f"Error: Could not import logging modules: {e}", file=sys.stderr)


def find_active_project_dir(cwd: str) -> Optional[str]:
    """Find the active architecture project with logging enabled."""
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
        return None

    return None


def get_session_id() -> str:
    """Get session ID from environment or generate one."""
    return os.environ.get("CLAUDE_SESSION_ID", "cli-session")


def log_expanded_prompt(content: str, command: Optional[str] = None) -> bool:
    """Log an expanded prompt entry."""
    if not FILTERS_AVAILABLE:
        print("Error: Logging modules not available", file=sys.stderr)
        return False

    cwd = os.getcwd()
    project_dir = find_active_project_dir(cwd)

    if not project_dir:
        # Silently succeed if logging not enabled - not an error
        return True

    filter_result = filter_pipeline(content)

    entry = LogEntry.create(
        session_id=get_session_id(),
        entry_type="expanded_prompt",
        content=filter_result.filtered_text,
        command=command,
        cwd=cwd,
        filter_info=filter_result.to_filter_info()
    )

    return append_to_log(project_dir, entry)


def log_response_summary(content: str, command: Optional[str] = None) -> bool:
    """Log a response summary entry."""
    if not FILTERS_AVAILABLE:
        print("Error: Logging modules not available", file=sys.stderr)
        return False

    cwd = os.getcwd()
    project_dir = find_active_project_dir(cwd)

    if not project_dir:
        return True

    filter_result = filter_pipeline(content)

    entry = LogEntry.create(
        session_id=get_session_id(),
        entry_type="response_summary",
        content=filter_result.filtered_text,
        command=command,
        cwd=cwd,
        filter_info=filter_result.to_filter_info()
    )

    return append_to_log(project_dir, entry)


def show_status() -> None:
    """Show current logging status."""
    cwd = os.getcwd()
    project_dir = find_active_project_dir(cwd)

    if not project_dir:
        print("Logging: DISABLED (no active project with .prompt-log-enabled)")
        return

    project_name = os.path.basename(project_dir)
    print(f"Logging: ENABLED")
    print(f"Project: {project_name}")

    log_path = os.path.join(project_dir, PROMPT_LOG_FILENAME)
    if os.path.isfile(log_path):
        size = os.path.getsize(log_path)
        with open(log_path, "r") as f:
            lines = sum(1 for _ in f)
        print(f"Log entries: {lines}")
        print(f"Log size: {size} bytes")
    else:
        print("Log file: Not created yet")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CLI utility for prompt capture logging"
    )
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # Expanded prompt command
    expanded_parser = subparsers.add_parser(
        "expanded",
        help="Log an expanded prompt"
    )
    expanded_parser.add_argument("content", help="The expanded prompt content")
    expanded_parser.add_argument(
        "--command", "-c",
        help="The /arch command that triggered this"
    )

    # Response summary command
    response_parser = subparsers.add_parser(
        "response",
        help="Log a response summary"
    )
    response_parser.add_argument("content", help="The response summary")
    response_parser.add_argument(
        "--command", "-c",
        help="The /arch command context"
    )

    # Status command
    subparsers.add_parser("status", help="Show logging status")

    args = parser.parse_args()

    if args.action == "expanded":
        success = log_expanded_prompt(args.content, args.command)
        return 0 if success else 1
    elif args.action == "response":
        success = log_response_summary(args.content, args.command)
        return 0 if success else 1
    elif args.action == "status":
        show_status()
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
