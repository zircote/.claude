"""Tests for the log analyzer module."""

import os
import sys
import tempfile
import unittest

# Add hooks directory to path
HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

from filters.log_entry import LogEntry, FilterInfo
from filters.log_writer import append_to_log
from analyzers.log_analyzer import (
    analyze_log,
    generate_interaction_analysis,
    LogAnalysis,
    SessionStats
)


class TestLogAnalyzer(unittest.TestCase):
    """Tests for log analysis functionality."""

    def _create_test_log(self, tmpdir, entries_data):
        """Helper to create a test log with specified entries."""
        for data in entries_data:
            filter_info = data.get("filter_info")
            if filter_info:
                filter_info = FilterInfo(**filter_info)

            entry = LogEntry.create(
                session_id=data.get("session_id", "test-session"),
                entry_type=data.get("entry_type", "user_input"),
                content=data.get("content", "Test"),
                command=data.get("command"),
                filter_info=filter_info
            )
            append_to_log(tmpdir, entry)

    def test_analyze_empty_log(self):
        """Should return None for directory without log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = analyze_log(tmpdir)
            self.assertIsNone(result)

    def test_analyze_single_entry(self):
        """Should analyze a single entry correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_test_log(tmpdir, [
                {"content": "Test prompt", "entry_type": "user_input"}
            ])

            analysis = analyze_log(tmpdir)

            self.assertIsNotNone(analysis)
            self.assertEqual(analysis.total_entries, 1)
            self.assertEqual(analysis.user_inputs, 1)
            self.assertEqual(analysis.expanded_prompts, 0)
            self.assertEqual(analysis.response_summaries, 0)

    def test_analyze_mixed_entry_types(self):
        """Should count different entry types correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_test_log(tmpdir, [
                {"entry_type": "user_input", "content": "User 1"},
                {"entry_type": "expanded_prompt", "content": "Expanded 1"},
                {"entry_type": "user_input", "content": "User 2"},
                {"entry_type": "response_summary", "content": "Summary 1"},
            ])

            analysis = analyze_log(tmpdir)

            self.assertEqual(analysis.total_entries, 4)
            self.assertEqual(analysis.user_inputs, 2)
            self.assertEqual(analysis.expanded_prompts, 1)
            self.assertEqual(analysis.response_summaries, 1)

    def test_count_questions(self):
        """Should count prompts containing questions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_test_log(tmpdir, [
                {"content": "What is this?", "entry_type": "user_input"},
                {"content": "Do this task", "entry_type": "user_input"},
                {"content": "How does it work?", "entry_type": "user_input"},
            ])

            analysis = analyze_log(tmpdir)

            self.assertEqual(analysis.total_questions, 2)

    def test_track_commands(self):
        """Should track command usage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_test_log(tmpdir, [
                {"command": "/arch:p", "content": "Test 1"},
                {"command": "/arch:p", "content": "Test 2"},
                {"command": "/arch:i", "content": "Test 3"},
            ])

            analysis = analyze_log(tmpdir)

            self.assertIn("/arch:p", analysis.commands_used)
            self.assertEqual(analysis.commands_used["/arch:p"], 2)
            self.assertEqual(analysis.commands_used["/arch:i"], 1)

    def test_track_filtered_content(self):
        """Should count filtered content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_test_log(tmpdir, [
                {
                    "content": "Clean",
                    "filter_info": {"profanity_count": 0, "secret_count": 0, "secret_types": []}
                },
                {
                    "content": "[FILTERED]",
                    "filter_info": {"profanity_count": 2, "secret_count": 0, "secret_types": []}
                },
                {
                    "content": "[SECRET:aws]",
                    "filter_info": {"profanity_count": 0, "secret_count": 1, "secret_types": ["aws_key"]}
                },
            ])

            analysis = analyze_log(tmpdir)

            self.assertEqual(analysis.profanity_filtered, 2)
            self.assertEqual(analysis.secrets_filtered, 1)
            self.assertEqual(analysis.total_filtered_content, 2)

    def test_prompt_length_stats(self):
        """Should calculate prompt length statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_test_log(tmpdir, [
                {"content": "Short", "entry_type": "user_input"},  # 5 chars
                {"content": "A much longer prompt here", "entry_type": "user_input"},  # 25 chars
                {"content": "Medium length", "entry_type": "user_input"},  # 13 chars
            ])

            analysis = analyze_log(tmpdir)

            self.assertEqual(analysis.prompt_length_min, 5)
            self.assertEqual(analysis.prompt_length_max, 25)
            self.assertGreater(analysis.prompt_length_avg, 10)
            self.assertLess(analysis.prompt_length_avg, 20)

    def test_session_grouping(self):
        """Should group entries by session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_test_log(tmpdir, [
                {"session_id": "session-1", "content": "S1-1"},
                {"session_id": "session-1", "content": "S1-2"},
                {"session_id": "session-2", "content": "S2-1"},
            ])

            analysis = analyze_log(tmpdir)

            self.assertEqual(analysis.session_count, 2)
            self.assertEqual(analysis.avg_entries_per_session, 1.5)


class TestInteractionAnalysisGenerator(unittest.TestCase):
    """Tests for retrospective markdown generation."""

    def test_generate_basic_analysis(self):
        """Should generate valid markdown."""
        analysis = LogAnalysis(
            total_entries=10,
            user_inputs=8,
            expanded_prompts=1,
            response_summaries=1,
            session_count=2,
            avg_entries_per_session=5.0,
            total_questions=3,
            prompt_length_avg=100.0
        )

        markdown = generate_interaction_analysis(analysis)

        self.assertIn("## Interaction Analysis", markdown)
        self.assertIn("| Total Prompts | 10 |", markdown)
        self.assertIn("| User Inputs | 8 |", markdown)
        self.assertIn("| Sessions | 2 |", markdown)

    def test_include_commands_section(self):
        """Should include commands when present."""
        analysis = LogAnalysis(
            total_entries=5,
            user_inputs=5,
            session_count=1,
            avg_entries_per_session=5.0,
            commands_used={"/arch:p": 3, "/arch:i": 2}
        )

        markdown = generate_interaction_analysis(analysis)

        self.assertIn("### Commands Used", markdown)
        self.assertIn("`/arch:p`: 3 times", markdown)
        self.assertIn("`/arch:i`: 2 times", markdown)

    def test_include_filtering_stats(self):
        """Should include filtering stats when present."""
        analysis = LogAnalysis(
            total_entries=5,
            user_inputs=5,
            session_count=1,
            avg_entries_per_session=5.0,
            total_filtered_content=3,
            profanity_filtered=2,
            secrets_filtered=1
        )

        markdown = generate_interaction_analysis(analysis)

        self.assertIn("### Content Filtering", markdown)
        self.assertIn("Profanity filtered: 2", markdown)
        self.assertIn("Secrets filtered: 1", markdown)

    def test_high_clarification_insight(self):
        """Should flag high-clarification sessions."""
        analysis = LogAnalysis(
            total_entries=20,
            user_inputs=20,
            session_count=1,
            avg_entries_per_session=20.0,
            total_questions=15,
            clarification_heavy_sessions=1
        )

        markdown = generate_interaction_analysis(analysis)

        self.assertIn("High clarification sessions", markdown)

    def test_question_heavy_insight(self):
        """Should flag question-heavy interactions."""
        analysis = LogAnalysis(
            total_entries=10,
            user_inputs=10,
            session_count=1,
            avg_entries_per_session=10.0,
            total_questions=8  # 80% questions
        )

        markdown = generate_interaction_analysis(analysis)

        self.assertIn("Question-heavy interaction", markdown)

    def test_short_prompts_insight(self):
        """Should note short prompts."""
        analysis = LogAnalysis(
            total_entries=5,
            user_inputs=5,
            session_count=1,
            avg_entries_per_session=5.0,
            prompt_length_avg=30.0  # Under 50
        )

        markdown = generate_interaction_analysis(analysis)

        self.assertIn("Short prompts", markdown)

    def test_detailed_prompts_insight(self):
        """Should note detailed prompts."""
        analysis = LogAnalysis(
            total_entries=5,
            user_inputs=5,
            session_count=1,
            avg_entries_per_session=5.0,
            prompt_length_avg=600.0  # Over 500
        )

        markdown = generate_interaction_analysis(analysis)

        self.assertIn("Detailed prompts", markdown)


if __name__ == "__main__":
    unittest.main(verbosity=2)
