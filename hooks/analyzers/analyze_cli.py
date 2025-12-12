#!/usr/bin/env python3
"""
CLI for analyzing prompt logs and generating retrospective content.

Usage:
    python3 ~/.claude/hooks/analyzers/analyze_cli.py <project_dir>
    python3 ~/.claude/hooks/analyzers/analyze_cli.py <project_dir> --format json
    python3 ~/.claude/hooks/analyzers/analyze_cli.py <project_dir> --metrics-only
"""

import argparse
import json
import os
import sys

# Add parent directory for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOOKS_DIR = os.path.dirname(SCRIPT_DIR)
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

try:
    from analyzers.log_analyzer import analyze_log, generate_interaction_analysis, LogAnalysis
    ANALYZER_AVAILABLE = True
except ImportError as e:
    ANALYZER_AVAILABLE = False
    print(f"Error: Could not import analyzer: {e}", file=sys.stderr)


def format_metrics_table(analysis: LogAnalysis) -> str:
    """Format analysis as a simple metrics table."""
    lines = []
    lines.append("Prompt Capture Log Analysis")
    lines.append("=" * 40)
    lines.append(f"Total Entries:        {analysis.total_entries}")
    lines.append(f"User Inputs:          {analysis.user_inputs}")
    lines.append(f"Expanded Prompts:     {analysis.expanded_prompts}")
    lines.append(f"Response Summaries:   {analysis.response_summaries}")
    lines.append(f"Sessions:             {analysis.session_count}")
    lines.append(f"Questions Asked:      {analysis.total_questions}")

    duration = analysis.duration_minutes()
    if duration:
        lines.append(f"Total Duration:       {duration:.0f} minutes")

    if analysis.prompt_length_avg > 0:
        lines.append(f"Avg Prompt Length:    {analysis.prompt_length_avg:.0f} chars")

    if analysis.total_filtered_content > 0:
        lines.append(f"Content Filtered:     {analysis.total_filtered_content}")
        lines.append(f"  - Profanity:        {analysis.profanity_filtered}")
        lines.append(f"  - Secrets:          {analysis.secrets_filtered}")

    if analysis.commands_used:
        lines.append("")
        lines.append("Commands Used:")
        for cmd, count in sorted(analysis.commands_used.items(), key=lambda x: -x[1]):
            lines.append(f"  {cmd}: {count}")

    return "\n".join(lines)


def format_json(analysis: LogAnalysis) -> str:
    """Format analysis as JSON."""
    data = {
        "total_entries": analysis.total_entries,
        "user_inputs": analysis.user_inputs,
        "expanded_prompts": analysis.expanded_prompts,
        "response_summaries": analysis.response_summaries,
        "session_count": analysis.session_count,
        "avg_entries_per_session": analysis.avg_entries_per_session,
        "total_questions": analysis.total_questions,
        "clarification_heavy_sessions": analysis.clarification_heavy_sessions,
        "total_filtered_content": analysis.total_filtered_content,
        "profanity_filtered": analysis.profanity_filtered,
        "secrets_filtered": analysis.secrets_filtered,
        "prompt_length_min": analysis.prompt_length_min,
        "prompt_length_max": analysis.prompt_length_max,
        "prompt_length_avg": analysis.prompt_length_avg,
        "commands_used": analysis.commands_used,
        "first_entry_time": analysis.first_entry_time,
        "last_entry_time": analysis.last_entry_time,
        "duration_minutes": analysis.duration_minutes(),
    }
    return json.dumps(data, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze prompt logs for architecture project retrospectives"
    )
    parser.add_argument(
        "project_dir",
        help="Path to the architecture project directory"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json", "text"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--metrics-only", "-m",
        action="store_true",
        help="Only show metrics, skip insights and recommendations"
    )

    args = parser.parse_args()

    if not ANALYZER_AVAILABLE:
        print("Error: Analyzer module not available", file=sys.stderr)
        return 1

    # Validate project directory
    if not os.path.isdir(args.project_dir):
        print(f"Error: Project directory not found: {args.project_dir}", file=sys.stderr)
        return 1

    # Run analysis
    analysis = analyze_log(args.project_dir)

    if analysis is None:
        print("No prompt log found or log is empty", file=sys.stderr)
        return 0  # Not an error - just no data

    # Output based on format
    if args.format == "json":
        print(format_json(analysis))
    elif args.format == "text" or args.metrics_only:
        print(format_metrics_table(analysis))
    else:  # markdown
        print(generate_interaction_analysis(analysis))

    return 0


if __name__ == "__main__":
    sys.exit(main())
