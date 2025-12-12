"""
Secret Detection Module for Prompt Capture Hook

Provides regex patterns for detecting secrets, API keys, tokens, and passwords
in text content before logging.

Based on patterns from gitleaks and secrets-patterns-db projects.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Dict, Pattern

# Pre-compiled regex patterns for performance
SECRET_PATTERNS: Dict[str, Pattern] = {
    # AWS
    "aws_access_key": re.compile(r'\b((?:A3T[A-Z0-9]|AKIA|ASIA|ABIA|ACCA)[A-Z2-7]{16})\b'),
    "aws_secret_key": re.compile(r'(?i)aws.{0,20}secret.{0,20}[\'"][0-9a-zA-Z/+=]{40}[\'"]'),
    "aws_mws_key": re.compile(r'amzn\.mws\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),

    # GitHub
    "github_pat": re.compile(r'ghp_[A-Za-z0-9_]{36,}'),
    "github_oauth": re.compile(r'gho_[A-Za-z0-9_]{36,}'),
    "github_app": re.compile(r'(?:ghu|ghs)_[A-Za-z0-9_]{36,}'),
    "github_refresh": re.compile(r'ghr_[A-Za-z0-9_]{36,}'),

    # GitLab
    "gitlab_pat": re.compile(r'glpat-[A-Za-z0-9\-_]{20,}'),

    # AI Services
    "openai_key": re.compile(r'sk-[a-zA-Z0-9]{20,}T3BlbkFJ[a-zA-Z0-9]{20,}'),
    "anthropic_key": re.compile(r'sk-ant-api\d{2}-[a-zA-Z0-9_\-]{80,}'),

    # Google
    "google_api_key": re.compile(r'AIza[0-9A-Za-z\-_]{35}'),
    "google_oauth": re.compile(r'ya29\.[0-9A-Za-z\-_]+'),

    # Stripe
    "stripe_secret": re.compile(r'sk_live_[0-9a-zA-Z]{24,}'),
    "stripe_publishable": re.compile(r'pk_live_[0-9a-zA-Z]{24,}'),

    # Slack
    "slack_token": re.compile(r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*'),
    "slack_webhook": re.compile(r'https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8,12}/[a-zA-Z0-9_]{24}'),

    # Twilio
    "twilio_api_key": re.compile(r'SK[0-9a-fA-F]{32}'),

    # SendGrid
    "sendgrid_api_key": re.compile(r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}'),

    # Mailgun
    "mailgun_api_key": re.compile(r'key-[0-9a-zA-Z]{32}'),

    # Generic patterns
    "bearer_token": re.compile(r'Bearer\s+[a-zA-Z0-9\-_.~+\/]+=*'),
    "basic_auth": re.compile(r'Basic\s+[a-zA-Z0-9+/]+=*'),
    "jwt": re.compile(r'ey[a-zA-Z0-9]{17,}\.ey[a-zA-Z0-9\/\\_-]{17,}\.[a-zA-Z0-9\/\\_-]{10,}'),

    # Connection strings
    "postgres_uri": re.compile(r'postgres(?:ql)?://[^\s\'"]+'),
    "mysql_uri": re.compile(r'mysql://[^\s\'"]+'),
    "mongodb_uri": re.compile(r'mongodb(?:\+srv)?://[^\s\'"]+'),
    "redis_uri": re.compile(r'redis://[^\s\'"]+'),

    # Private keys (detect headers)
    "private_key_rsa": re.compile(r'-----BEGIN RSA PRIVATE KEY-----'),
    "private_key_dsa": re.compile(r'-----BEGIN DSA PRIVATE KEY-----'),
    "private_key_ec": re.compile(r'-----BEGIN EC PRIVATE KEY-----'),
    "private_key_openssh": re.compile(r'-----BEGIN OPENSSH PRIVATE KEY-----'),
    "private_key_pgp": re.compile(r'-----BEGIN PGP PRIVATE KEY BLOCK-----'),
    "private_key_generic": re.compile(r'-----BEGIN PRIVATE KEY-----'),

    # Password patterns (context-aware)
    "password_assignment": re.compile(r'(?i)(?:password|passwd|pwd)\s*[:=]\s*[\'"][^\'"]{8,}[\'"]'),
    "secret_assignment": re.compile(r'(?i)(?:secret|api[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*[\'"][^\'"]{10,}[\'"]'),
}


@dataclass
class SecretMatch:
    """Represents a detected secret in text."""
    secret_type: str
    match: str
    start: int
    end: int

    @property
    def masked(self) -> str:
        """Return masked version showing only first/last few chars."""
        if len(self.match) <= 8:
            return "[SECRET]"
        return f"{self.match[:4]}...{self.match[-4:]}"


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
