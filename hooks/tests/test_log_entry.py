"""Tests for log entry and log writer modules."""

import json
import os
import sys
import tempfile
import unittest

# Add hooks directory to path
HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

from filters.log_entry import LogEntry, FilterInfo, EntryMetadata
from filters.log_writer import append_to_log, read_log, PROMPT_LOG_FILENAME


class TestLogEntry(unittest.TestCase):
    """Tests for LogEntry dataclass."""

    def test_create_user_input_entry(self):
        """Should create a valid user input entry."""
        entry = LogEntry.create(
            session_id="test-session-123",
            entry_type="user_input",
            content="Test prompt content",
            command="/arch:p",
            cwd="/path/to/project"
        )

        self.assertEqual(entry.session_id, "test-session-123")
        self.assertEqual(entry.entry_type, "user_input")
        self.assertEqual(entry.content, "Test prompt content")
        self.assertEqual(entry.command, "/arch:p")
        self.assertIsNotNone(entry.timestamp)
        self.assertEqual(entry.metadata.cwd, "/path/to/project")

    def test_create_expanded_prompt_entry(self):
        """Should create a valid expanded prompt entry."""
        entry = LogEntry.create(
            session_id="test-session",
            entry_type="expanded_prompt",
            content="The expanded content from slash command",
            command="/arch:p"
        )

        self.assertEqual(entry.entry_type, "expanded_prompt")

    def test_create_response_summary_entry(self):
        """Should create a valid response summary entry."""
        entry = LogEntry.create(
            session_id="test-session",
            entry_type="response_summary",
            content="Summary of Claude's response"
        )

        self.assertEqual(entry.entry_type, "response_summary")

    def test_create_with_filter_info(self):
        """Should include filter info when provided."""
        filter_info = FilterInfo(
            profanity_count=2,
            secret_count=1,
            secret_types=["aws_access_key"]
        )

        entry = LogEntry.create(
            session_id="test",
            entry_type="user_input",
            content="Filtered content",
            filter_info=filter_info
        )

        self.assertEqual(entry.filter_applied.profanity_count, 2)
        self.assertEqual(entry.filter_applied.secret_count, 1)
        self.assertIn("aws_access_key", entry.filter_applied.secret_types)

    def test_to_json(self):
        """Should serialize to valid JSON."""
        entry = LogEntry.create(
            session_id="test-json",
            entry_type="user_input",
            content="Test content"
        )

        json_str = entry.to_json()
        parsed = json.loads(json_str)

        self.assertEqual(parsed["session_id"], "test-json")
        self.assertEqual(parsed["type"], "user_input")
        self.assertEqual(parsed["content"], "Test content")

    def test_from_dict(self):
        """Should deserialize from dict."""
        data = {
            "timestamp": "2025-01-01T00:00:00Z",
            "session_id": "test-dict",
            "type": "user_input",
            "content": "Dict content",
            "command": "/arch:i",
            "filter_applied": {
                "profanity_count": 0,
                "secret_count": 0,
                "secret_types": []
            },
            "metadata": {
                "content_length": 12,
                "cwd": "/test"
            }
        }

        entry = LogEntry.from_dict(data)
        self.assertEqual(entry.session_id, "test-dict")
        self.assertEqual(entry.content, "Dict content")
        self.assertEqual(entry.command, "/arch:i")

    def test_metadata_content_length(self):
        """Metadata should auto-calculate content length."""
        entry = LogEntry.create(
            session_id="test",
            entry_type="user_input",
            content="12345"  # 5 characters
        )

        self.assertEqual(entry.metadata.content_length, 5)


class TestLogWriter(unittest.TestCase):
    """Tests for log writing functionality."""

    def test_append_to_log_creates_file(self):
        """Should create log file if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            entry = LogEntry.create(
                session_id="test",
                entry_type="user_input",
                content="Test"
            )

            result = append_to_log(tmpdir, entry)

            self.assertTrue(result)
            log_path = os.path.join(tmpdir, PROMPT_LOG_FILENAME)
            self.assertTrue(os.path.exists(log_path))

    def test_append_multiple_entries(self):
        """Should append multiple entries to same file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(3):
                entry = LogEntry.create(
                    session_id="test",
                    entry_type="user_input",
                    content=f"Entry {i}"
                )
                append_to_log(tmpdir, entry)

            log_path = os.path.join(tmpdir, PROMPT_LOG_FILENAME)
            with open(log_path) as f:
                lines = f.readlines()

            self.assertEqual(len(lines), 3)

    def test_read_log(self):
        """Should read back entries correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write entries
            for i in range(2):
                entry = LogEntry.create(
                    session_id="test",
                    entry_type="user_input",
                    content=f"Entry {i}"
                )
                append_to_log(tmpdir, entry)

            # Read back
            entries = read_log(tmpdir)

            self.assertEqual(len(entries), 2)
            self.assertEqual(entries[0].content, "Entry 0")
            self.assertEqual(entries[1].content, "Entry 1")

    def test_read_log_empty_dir(self):
        """Should return empty list for directory without log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            entries = read_log(tmpdir)
            self.assertEqual(entries, [])

    def test_ndjson_format(self):
        """Each entry should be a single JSON line."""
        with tempfile.TemporaryDirectory() as tmpdir:
            entry = LogEntry.create(
                session_id="test",
                entry_type="user_input",
                content="Single line test"
            )
            append_to_log(tmpdir, entry)

            log_path = os.path.join(tmpdir, PROMPT_LOG_FILENAME)
            with open(log_path) as f:
                content = f.read()

            # Should be single line (plus newline)
            lines = content.strip().split("\n")
            self.assertEqual(len(lines), 1)

            # Should be valid JSON
            parsed = json.loads(lines[0])
            self.assertEqual(parsed["content"], "Single line test")


if __name__ == "__main__":
    unittest.main(verbosity=2)
