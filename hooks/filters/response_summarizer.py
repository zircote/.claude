"""
Response Summarizer for Prompt Capture Hook

Generates concise summaries of Claude responses for logging.
Uses heuristic extraction rather than LLM summarization for speed.
"""

import re
from typing import Optional


MAX_SUMMARY_LENGTH = 500


def summarize_response(text: str, max_length: int = MAX_SUMMARY_LENGTH) -> str:
    """
    Generate a concise summary of a Claude response.

    Extraction strategy:
    1. Extract first paragraph (typically main point)
    2. Extract bullet points or numbered lists
    3. Note presence of code blocks without full content
    4. Truncate to max_length

    Args:
        text: Full response text
        max_length: Maximum length of summary

    Returns:
        Summarized text
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    summary_parts = []

    # Extract first paragraph
    paragraphs = text.split("\n\n")
    if paragraphs:
        first_para = paragraphs[0].strip()
        if first_para:
            summary_parts.append(first_para)

    # Look for bullet points or numbered lists
    bullet_pattern = re.compile(r'^[\s]*[-*•]\s+(.+)$', re.MULTILINE)
    number_pattern = re.compile(r'^[\s]*\d+[.)]\s+(.+)$', re.MULTILINE)

    bullets = bullet_pattern.findall(text)
    numbers = number_pattern.findall(text)

    list_items = bullets[:5] + numbers[:5]  # Take first 5 of each
    if list_items:
        summary_parts.append("Key points: " + "; ".join(list_items[:5]))

    # Note code blocks without content
    code_block_count = text.count("```")
    if code_block_count >= 2:
        summary_parts.append(f"[Contains {code_block_count // 2} code block(s)]")

    # Note tool usage
    if "function_calls" in text.lower() or "antml:invoke" in text.lower():
        summary_parts.append("[Contains tool calls]")

    # Join parts
    summary = " | ".join(summary_parts)

    # Truncate if needed
    if len(summary) > max_length:
        summary = summary[:max_length - 3] + "..."

    return summary


def extract_key_actions(text: str) -> list:
    """
    Extract key actions taken from a response.

    Looks for patterns like:
    - "I'll..." or "I will..."
    - "Let me..."
    - "Creating..." "Updating..." "Implementing..."

    Args:
        text: Response text

    Returns:
        List of action strings
    """
    actions = []

    # Pattern for action statements
    action_patterns = [
        r"I(?:'ll| will) ([^.!?\n]+)",
        r"Let me ([^.!?\n]+)",
        r"(?:Creating|Updating|Implementing|Adding|Removing|Fixing) ([^.!?\n]+)",
    ]

    for pattern in action_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        actions.extend(matches[:3])  # Limit per pattern

    return actions[:10]  # Overall limit
