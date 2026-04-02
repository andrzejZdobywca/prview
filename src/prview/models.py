"""Core data models for prview.

These dataclasses are the shared contract between all modules.
Designed to be diffable themselves (for future diff-of-diffs support).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class DiffLine:
    """A single line in a diff hunk."""

    type: Literal["add", "remove", "context"]
    content: str
    old_lineno: int | None
    new_lineno: int | None


@dataclass
class DiffHunk:
    """A contiguous block of changes within a file."""

    header: str
    lines: list[DiffLine] = field(default_factory=list)


@dataclass
class DiffFile:
    """A single file's diff."""

    path: str
    old_path: str | None
    status: Literal["added", "modified", "deleted", "renamed", "binary"]
    hunks: list[DiffHunk] = field(default_factory=list)
    added_lines: int = 0
    removed_lines: int = 0

    @property
    def display_path(self) -> str:
        """Path for display, showing rename arrow if applicable."""
        if self.old_path and self.old_path != self.path:
            return f"{self.old_path} -> {self.path}"
        return self.path


@dataclass
class DiffData:
    """Top-level container for a complete diff."""

    files: list[DiffFile] = field(default_factory=list)
    base_ref: str | None = None
    head_ref: str | None = None
