"""
Filter Pipeline for claude-spec Prompt Capture Hook

Chains content filters together in the correct order:
1. Secrets (security-critical, filter first)
2. Truncation (if content is too long)

Returns a unified result with all filtering information.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Pattern, Tuple

from .log_entry import FilterInfo

# Maximum content length before truncation
MAX_CONTENT_LENGTH = 50000

# Pre-compiled regex patterns for secret detection
SECRET_PATTERNS: Dict[str, Pattern] = {
    # AWS
    "aws_access_key": re.compile(r'\b((?:A3T[A-Z0-9]|AKIA|ASIA|ABIA|ACCA)[A-Z2-7]{16})\b'),
    "aws_secret_key": re.compile(r'(?i)aws.{0,20}secret.{0,20}[\'"][0-9a-zA-Z/+=]{40}[\'"]'),

    # GitHub
    "github_pat": re.compile(r'ghp_[A-Za-z0-9_]{36,}'),
    "github_oauth": re.compile(r'gho_[A-Za-z0-9_]{36,}'),
    "github_app": re.compile(r'(?:ghu|ghs)_[A-Za-z0-9_]{36,}'),

    # AI Services
    "openai_key": re.compile(r'sk-[a-zA-Z0-9]{20,}T3BlbkFJ[a-zA-Z0-9]{20,}'),
    "anthropic_key": re.compile(r'sk-ant-api\d{2}-[a-zA-Z0-9_\-]{80,}'),

    # Google
    "google_api_key": re.compile(r'AIza[0-9A-Za-z\-_]{35}'),

    # Stripe
    "stripe_secret": re.compile(r'sk_live_[0-9a-zA-Z]{24,}'),
    "stripe_publishable": re.compile(r'pk_live_[0-9a-zA-Z]{24,}'),

    # Slack
    "slack_token": re.compile(r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*'),

    # Generic patterns
    "bearer_token": re.compile(r'Bearer\s+[a-zA-Z0-9\-_.~+\/]+=*'),
    "jwt": re.compile(r'ey[a-zA-Z0-9]{17,}\.ey[a-zA-Z0-9\/\\_-]{17,}\.[a-zA-Z0-9\/\\_-]{10,}'),

    # Connection strings
    "postgres_uri": re.compile(r'postgres(?:ql)?://[^\s\'"]+'),
    "mysql_uri": re.compile(r'mysql://[^\s\'"]+'),
    "mongodb_uri": re.compile(r'mongodb(?:\+srv)?://[^\s\'"]+'),
    "redis_uri": re.compile(r'redis://[^\s\'"]+'),

    # Private keys (detect headers)
    "private_key": re.compile(r'-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY'),

    # Password patterns (context-aware)
    "password_assignment": re.compile(
        r'(?i)(?:password|passwd|pwd)\s*[:=]\s*[\'"][^\'"]{8,}[\'"]'
    ),
    "secret_assignment": re.compile(
        r'(?i)(?:secret|api[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*[\'"][^\'"]{10,}[\'"]'
    ),
}


@dataclass
class SecretMatch:
    """Represents a detected secret in text."""
    secret_type: str
    match: str
    start: int
    end: int


@dataclass
class FilterResult:
    """Result of running the filter pipeline."""
    original_length: int
    filtered_text: str
    secret_count: int
    secret_types: List[str] = field(default_factory=list)
    was_truncated: bool = False

    def to_filter_info(self) -> FilterInfo:
        """Convert to FilterInfo for log entries."""
        return FilterInfo(
            secret_count=self.secret_count,
            secret_types=self.secret_types,
            was_truncated=self.was_truncated
        )

    @property
    def was_filtered(self) -> bool:
        """Check if any content was filtered."""
        return self.secret_count > 0 or self.was_truncated


def detect_secrets(text: str) -> List[SecretMatch]:
    """
    Detect secrets in text using pre-compiled patterns.

    Args:
        text: The text to scan for secrets

    Returns:
        List of SecretMatch objects for each detected secret
    """
    matches = []

    for secret_type, pattern in SECRET_PATTERNS.items():
        for match in pattern.finditer(text):
            matches.append(SecretMatch(
                secret_type=secret_type,
                match=match.group(0),
                start=match.start(),
                end=match.end()
            ))

    # Sort by position for consistent replacement
    matches.sort(key=lambda m: m.start)

    return matches


def filter_secrets(text: str) -> Tuple[str, List[str]]:
    """
    Replace detected secrets with type-labeled placeholders.

    Args:
        text: The text to filter

    Returns:
        Tuple of (filtered_text, list_of_secret_types_found)
    """
    matches = detect_secrets(text)

    if not matches:
        return text, []

    # Replace from end to start to preserve positions
    result = text
    secret_types = []

    for match in reversed(matches):
        placeholder = f"[SECRET:{match.secret_type}]"
        result = result[:match.start] + placeholder + result[match.end:]
        secret_types.append(match.secret_type)

    # Return types in original order
    secret_types.reverse()

    return result, secret_types


def truncate_text(text: str, max_length: int = MAX_CONTENT_LENGTH) -> Tuple[str, bool]:
    """
    Truncate text if it exceeds max length.

    Args:
        text: Text to potentially truncate
        max_length: Maximum allowed length

    Returns:
        Tuple of (text, was_truncated)
    """
    if len(text) <= max_length:
        return text, False

    truncate_notice = f"\n...[TRUNCATED: {len(text) - max_length + 100} chars removed]..."
    truncated = text[:max_length - len(truncate_notice)] + truncate_notice
    return truncated, True


def filter_pipeline(text: str) -> FilterResult:
    """
    Run the full filter pipeline on text.

    Order of operations:
    1. Filter secrets first (security-critical)
    2. Truncate if too long

    Args:
        text: The text to filter

    Returns:
        FilterResult with filtered text and statistics
    """
    original_length = len(text)

    # Step 1: Filter secrets
    text_after_secrets, secret_types = filter_secrets(text)
    secret_count = len(secret_types)

    # Step 2: Truncate if needed
    filtered_text, was_truncated = truncate_text(text_after_secrets)

    return FilterResult(
        original_length=original_length,
        filtered_text=filtered_text,
        secret_count=secret_count,
        secret_types=secret_types,
        was_truncated=was_truncated
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
    result = filter_pipeline(text)
    return result.was_filtered
