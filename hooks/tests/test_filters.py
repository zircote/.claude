"""Tests for the filter modules (profanity, secrets, pipeline)."""

import unittest
import sys
import os

# Add hooks directory to path
HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

from filters.profanity import filter_profanity
from filters.secrets import filter_secrets
from filters.pipeline import filter_pipeline


class TestProfanityFilter(unittest.TestCase):
    """Tests for profanity filtering."""

    def test_clean_text_unchanged(self):
        """Clean text should pass through unchanged."""
        text = "This is a normal message about programming."
        result, count = filter_profanity(text)
        self.assertEqual(result, text)
        self.assertEqual(count, 0)

    def test_profanity_filtered(self):
        """Profane words should be replaced with [FILTERED]."""
        text = "This is a damn test."
        result, count = filter_profanity(text)
        self.assertIn("[FILTERED]", result)
        self.assertNotIn("damn", result.lower())
        self.assertGreaterEqual(count, 1)

    def test_multiple_profanities(self):
        """Multiple profane words should all be filtered."""
        text = "What the hell is this crap?"
        result, count = filter_profanity(text)
        self.assertGreaterEqual(result.count("[FILTERED]"), 2)
        self.assertGreaterEqual(count, 2)

    def test_case_insensitive(self):
        """Profanity detection should be case-insensitive."""
        text = "This is DAMN annoying."
        result, count = filter_profanity(text)
        self.assertIn("[FILTERED]", result)
        self.assertGreaterEqual(count, 1)

    def test_word_boundaries(self):
        """Should only match whole words, not substrings."""
        text = "I need to assess this classic problem."
        result, count = filter_profanity(text)
        # "ass" appears in "assess" and "classic" but shouldn't match
        self.assertIn("assess", result)
        self.assertIn("classic", result)
        self.assertEqual(count, 0)

    def test_empty_string(self):
        """Empty string should return empty string."""
        result, count = filter_profanity("")
        self.assertEqual(result, "")
        self.assertEqual(count, 0)


class TestSecretsFilter(unittest.TestCase):
    """Tests for secret/credential filtering."""

    def test_clean_text_unchanged(self):
        """Text without secrets should pass through unchanged."""
        text = "This is a normal API call with no credentials."
        result, types = filter_secrets(text)
        self.assertEqual(result, text)
        self.assertEqual(len(types), 0)

    def test_aws_access_key(self):
        """AWS access keys should be filtered."""
        text = "My AWS key is AKIAIOSFODNN7EXAMPLE"
        result, types = filter_secrets(text)
        self.assertIn("[SECRET:aws_access_key]", result)
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", result)
        self.assertIn("aws_access_key", types)

    def test_github_pat(self):
        """GitHub personal access tokens should be filtered."""
        text = "Use this token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        result, types = filter_secrets(text)
        self.assertIn("[SECRET:github_pat]", result)
        self.assertNotIn("ghp_", result)
        self.assertIn("github_pat", types)

    def test_generic_password_assignment(self):
        """Password assignments with quotes should be filtered."""
        text = 'Set DB_PASSWORD="MySecretPassword123!"'
        result, types = filter_secrets(text)
        self.assertIn("[SECRET:", result)
        self.assertNotIn("MySecretPassword123!", result)

    def test_bearer_token(self):
        """Bearer tokens should be filtered."""
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result, types = filter_secrets(text)
        self.assertIn("[SECRET:bearer_token]", result)

    def test_multiple_secrets(self):
        """Multiple secrets should all be filtered."""
        text = "AWS: AKIAIOSFODNN7EXAMPLE, GitHub: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        result, types = filter_secrets(text)
        self.assertGreaterEqual(result.count("[SECRET:"), 2)
        self.assertGreaterEqual(len(types), 2)

    def test_empty_string(self):
        """Empty string should return empty string."""
        result, types = filter_secrets("")
        self.assertEqual(result, "")
        self.assertEqual(len(types), 0)


class TestFilterPipeline(unittest.TestCase):
    """Tests for the combined filter pipeline."""

    def test_clean_text_unchanged(self):
        """Clean text should pass through with no filters applied."""
        text = "Normal programming discussion."
        result = filter_pipeline(text)
        self.assertEqual(result.filtered_text, text)
        self.assertEqual(result.profanity_count, 0)
        self.assertEqual(result.secret_count, 0)

    def test_both_filters_applied(self):
        """Both secret and profanity filters should run."""
        text = "What the hell, my token is ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        result = filter_pipeline(text)
        self.assertIn("[FILTERED]", result.filtered_text)
        self.assertIn("[SECRET:", result.filtered_text)
        self.assertGreaterEqual(result.profanity_count, 1)
        self.assertGreaterEqual(result.secret_count, 1)

    def test_filter_info_generation(self):
        """FilterResult should generate proper FilterInfo."""
        text = "Damn, my key is AKIAIOSFODNN7EXAMPLE"
        result = filter_pipeline(text)
        filter_info = result.to_filter_info()
        self.assertIsNotNone(filter_info)
        self.assertGreaterEqual(filter_info.profanity_count, 1)
        self.assertGreaterEqual(filter_info.secret_count, 1)

    def test_empty_input(self):
        """Empty input should return empty result."""
        result = filter_pipeline("")
        self.assertEqual(result.filtered_text, "")
        self.assertEqual(result.profanity_count, 0)
        self.assertEqual(result.secret_count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
