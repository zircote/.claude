"""
Log Entry Schema for claude-spec Prompt Capture Hook

Defines the structure for prompt log entries in NDJSON format.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class FilterInfo:
    """Information about content filtering applied to an entry."""
    secret_count: int = 0
    secret_types: List[str] = field(default_factory=list)
    was_truncated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FilterInfo":
        """Create FilterInfo from dictionary."""
        return cls(
            secret_count=data.get("secret_count", 0),
            secret_types=data.get("secret_types", []),
            was_truncated=data.get("was_truncated", False)
        )


@dataclass
class EntryMetadata:
    """Metadata about the log entry context."""
    content_length: int = 0
    cwd: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntryMetadata":
        """Create EntryMetadata from dictionary."""
        return cls(
            content_length=data.get("content_length", 0),
            cwd=data.get("cwd", "")
        )


@dataclass
class LogEntry:
    """
    A single entry in the prompt capture log.

    Entry types:
    - user_input: Direct user prompt text
    - expanded_prompt: Full slash command expansion
    - response_summary: Summarized Claude response
    """
    timestamp: str
    session_id: str
    entry_type: str  # user_input, expanded_prompt, response_summary
    command: Optional[str]  # /spec:p, /spec:i, etc. or None
    content: str
    filter_applied: FilterInfo = field(default_factory=FilterInfo)
    metadata: EntryMetadata = field(default_factory=EntryMetadata)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "type": self.entry_type,
            "command": self.command,
            "content": self.content,
            "filter_applied": self.filter_applied.to_dict(),
            "metadata": self.metadata.to_dict()
        }

    def to_json(self) -> str:
        """Convert to JSON string (single line for NDJSON)."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogEntry":
        """Create LogEntry from dictionary."""
        return cls(
            timestamp=data.get("timestamp", ""),
            session_id=data.get("session_id", ""),
            entry_type=data.get("type", "user_input"),
            command=data.get("command"),
            content=data.get("content", ""),
            filter_applied=FilterInfo.from_dict(data.get("filter_applied", {})),
            metadata=EntryMetadata.from_dict(data.get("metadata", {}))
        )

    @classmethod
    def from_json(cls, json_str: str) -> "LogEntry":
        """Create LogEntry from JSON string."""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def create(
        cls,
        session_id: str,
        entry_type: str,
        content: str,
        command: Optional[str] = None,
        cwd: str = "",
        filter_info: Optional[FilterInfo] = None
    ) -> "LogEntry":
        """
        Factory method to create a new log entry with current timestamp.

        Args:
            session_id: Unique session identifier
            entry_type: Type of entry (user_input, expanded_prompt, response_summary)
            content: The actual content (already filtered)
            command: Optional /spec:* command if applicable
            cwd: Current working directory
            filter_info: Information about filtering applied

        Returns:
            New LogEntry instance
        """
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=session_id,
            entry_type=entry_type,
            command=command,
            content=content,
            filter_applied=filter_info or FilterInfo(),
            metadata=EntryMetadata(
                content_length=len(content),
                cwd=cwd
            )
        )
