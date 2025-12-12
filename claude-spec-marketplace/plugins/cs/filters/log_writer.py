"""
Log Writer Module for claude-spec Prompt Capture Hook

Provides atomic NDJSON append operations for the prompt log.
Uses file locking to handle concurrent writes safely.
"""

import fcntl
import json
import os
import sys
from typing import List

from .log_entry import LogEntry


PROMPT_LOG_FILENAME = ".prompt-log.json"


def get_log_path(project_dir: str) -> str:
    """
    Get the full path to the prompt log file for a project.

    Args:
        project_dir: Path to the spec project directory

    Returns:
        Full path to .prompt-log.json
    """
    return os.path.join(project_dir, PROMPT_LOG_FILENAME)


def append_to_log(project_dir: str, entry: LogEntry) -> bool:
    """
    Atomically append a log entry to the project's .prompt-log.json.

    Uses file locking to ensure safe concurrent writes.
    Creates the file if it doesn't exist.

    Args:
        project_dir: Path to the spec project directory
        entry: LogEntry to append

    Returns:
        True if successful, False otherwise
    """
    log_path = get_log_path(project_dir)

    try:
        # Create parent directory if needed
        parent_dir = os.path.dirname(log_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        # Open in append mode, create if doesn't exist
        with open(log_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                # Write JSON line with newline
                f.write(entry.to_json() + "\n")
                f.flush()
                os.fsync(f.fileno())  # Ensure written to disk
            finally:
                # Release lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return True

    except (OSError, IOError) as e:
        sys.stderr.write(f"claude-spec prompt_capture: Error writing log: {e}\n")
        return False


def read_log(project_dir: str) -> List[LogEntry]:
    """
    Read all entries from the prompt log.

    Args:
        project_dir: Path to the spec project directory

    Returns:
        List of LogEntry objects, empty list if file doesn't exist or errors
    """
    log_path = get_log_path(project_dir)

    if not os.path.isfile(log_path):
        return []

    entries = []

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(LogEntry.from_json(line))
                except json.JSONDecodeError:
                    sys.stderr.write(
                        f"claude-spec prompt_capture: Skipping corrupted line "
                        f"{line_num} in {log_path}\n"
                    )
    except (OSError, IOError) as e:
        sys.stderr.write(f"claude-spec prompt_capture: Error reading log: {e}\n")

    return entries


def get_recent_entries(project_dir: str, count: int = 10) -> List[LogEntry]:
    """
    Get the most recent log entries.

    Args:
        project_dir: Path to the spec project directory
        count: Number of recent entries to return

    Returns:
        List of LogEntry objects (most recent last)
    """
    entries = read_log(project_dir)
    return entries[-count:] if entries else []


def log_exists(project_dir: str) -> bool:
    """Check if a prompt log exists for the project."""
    return os.path.isfile(get_log_path(project_dir))


def clear_log(project_dir: str) -> bool:
    """
    Clear (delete) the prompt log for a project.

    Args:
        project_dir: Path to the spec project directory

    Returns:
        True if successful or file didn't exist, False on error
    """
    log_path = get_log_path(project_dir)

    if not os.path.isfile(log_path):
        return True

    try:
        os.remove(log_path)
        return True
    except OSError as e:
        sys.stderr.write(f"claude-spec prompt_capture: Error clearing log: {e}\n")
        return False
