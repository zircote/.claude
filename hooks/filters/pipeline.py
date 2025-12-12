"""
Filter Pipeline for Prompt Capture Hook

Chains content filters together in the correct order:
1. Secrets (more security-critical, filter first)
2. Profanity (commit safety)

Returns a unified result with all filtering information.
"""

from dataclasses import dataclass
from typing import List

from .secrets import filter_secrets
from .profanity import filter_profanity
from .log_entry import FilterInfo


@dataclass
class FilterResult:
    """Result of running the filter pipeline."""
    original_length: int
    filtered_text: str
    profanity_count: int
    secret_count: int
    secret_types: List[str]

    def to_filter_info(self) -> FilterInfo:
        """Convert to FilterInfo for log entries."""
        return FilterInfo(
            profanity_count=self.profanity_count,
            secret_count=self.secret_count,
            secret_types=self.secret_types
        )

    @property
    def was_filtered(self) -> bool:
        """Check if any content was filtered."""
        return self.profanity_count > 0 or self.secret_count > 0


def filter_pipeline(text: str) -> FilterResult:
    """
    Run the full filter pipeline on text.

    Order of operations:
    1. Filter secrets first (security-critical)
    2. Filter profanity second

    This order ensures secrets aren't accidentally preserved
    if they happen to contain profanity-like substrings.

    Args:
        text: The text to filter

    Returns:
        FilterResult with filtered text and statistics
    """
    original_length = len(text)

    # Step 1: Filter secrets
    text_after_secrets, secret_types = filter_secrets(text)
    secret_count = len(secret_types)

    # Step 2: Filter profanity
    filtered_text, profanity_count = filter_profanity(text_after_secrets)

    return FilterResult(
        original_length=original_length,
        filtered_text=filtered_text,
        profanity_count=profanity_count,
        secret_count=secret_count,
        secret_types=secret_types
    )


def quick_check(text: str) -> bool:
    """
    Quick check if text contains any sensitive content.

    Useful for deciding whether to run full pipeline.

    Args:
        text: Text to check

    Returns:
        True if text likely contains sensitive content
    """
    # Run full pipeline but just check if anything was filtered
    result = filter_pipeline(text)
    return result.was_filtered
