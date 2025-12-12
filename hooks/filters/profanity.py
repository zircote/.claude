"""
Profanity Filter Module for Prompt Capture Hook

Provides detection and filtering of profanity in text content.
Uses a word list with word boundary matching to minimize false positives.
"""

import os
import re
from typing import List, Set, Tuple

# Module-level cache for word list
_PROFANITY_WORDS: Set[str] = set()
_PROFANITY_PATTERN: re.Pattern = None


def _get_word_list_path() -> str:
    """Get the path to the profanity word list file."""
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(module_dir, "profanity_words.txt")


def _load_word_list() -> Set[str]:
    """Load profanity words from the word list file."""
    global _PROFANITY_WORDS

    if _PROFANITY_WORDS:
        return _PROFANITY_WORDS

    word_list_path = _get_word_list_path()

    try:
        with open(word_list_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip().lower()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    _PROFANITY_WORDS.add(line)
    except (OSError, IOError):
        # If we can't load the word list, use a minimal default
        _PROFANITY_WORDS = {"fuck", "shit", "damn", "ass", "bitch"}

    return _PROFANITY_WORDS


def _get_pattern() -> re.Pattern:
    """Get compiled regex pattern for profanity detection."""
    global _PROFANITY_PATTERN

    if _PROFANITY_PATTERN is not None:
        return _PROFANITY_PATTERN

    words = _load_word_list()

    if not words:
        # Return a pattern that matches nothing
        _PROFANITY_PATTERN = re.compile(r'(?!)')
        return _PROFANITY_PATTERN

    # Escape special regex characters and join with OR
    escaped_words = [re.escape(word) for word in words]

    # Sort by length descending to match longer variants first
    escaped_words.sort(key=len, reverse=True)

    # Build pattern with word boundaries for whole-word matching
    # Use case-insensitive matching
    pattern_str = r'\b(' + '|'.join(escaped_words) + r')\b'
    _PROFANITY_PATTERN = re.compile(pattern_str, re.IGNORECASE)

    return _PROFANITY_PATTERN


def detect_profanity(text: str) -> List[str]:
    """
    Detect profanity words in text.

    Args:
        text: The text to scan

    Returns:
        List of profanity words found (lowercase)
    """
    pattern = _get_pattern()
    matches = pattern.findall(text)
    return [m.lower() for m in matches]


def filter_profanity(text: str) -> Tuple[str, int]:
    """
    Replace profanity in text with [FILTERED] placeholder.

    Args:
        text: The text to filter

    Returns:
        Tuple of (filtered_text, count_of_replacements)
    """
    pattern = _get_pattern()

    count = 0

    def replace_match(match):
        nonlocal count
        count += 1
        return "[FILTERED]"

    filtered = pattern.sub(replace_match, text)

    return filtered, count


def reload_word_list() -> None:
    """Force reload of the word list (for testing or updates)."""
    global _PROFANITY_WORDS, _PROFANITY_PATTERN
    _PROFANITY_WORDS = set()
    _PROFANITY_PATTERN = None
    _load_word_list()
