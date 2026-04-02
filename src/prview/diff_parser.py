"""Diff parser module — converts raw unified diff text into DiffData models."""

from __future__ import annotations

from unidiff import PatchSet, LINE_TYPE_ADDED, LINE_TYPE_REMOVED, LINE_TYPE_CONTEXT

from prview.models import DiffData, DiffFile, DiffHunk, DiffLine


_LINE_TYPE_MAP = {
    LINE_TYPE_ADDED: "add",
    LINE_TYPE_REMOVED: "remove",
    LINE_TYPE_CONTEXT: "context",
}


def _strip_prefix(path: str, prefix: str) -> str:
    """Strip a/ or b/ prefix from a path if present."""
    if path.startswith(prefix):
        return path[len(prefix):]
    return path


def _file_status(pf) -> str:
    if pf.is_added_file:
        return "added"
    if pf.is_removed_file:
        return "deleted"
    if pf.is_rename:
        return "renamed"
    return "modified"


def parse(text: str) -> DiffData:
    """Parse a unified diff string into a DiffData model."""
    if not text or not text.strip():
        return DiffData()

    patch = PatchSet(text)
    files: list[DiffFile] = []

    for pf in patch:
        path = _strip_prefix(pf.path, "b/")
        old_path = _strip_prefix(pf.source_file, "a/") if pf.is_rename else None

        hunks: list[DiffHunk] = []
        for hunk in pf:
            lines: list[DiffLine] = []
            for line in hunk:
                line_type = _LINE_TYPE_MAP.get(line.line_type)
                if line_type is None:
                    continue
                content = line.value.rstrip("\n")
                lines.append(DiffLine(
                    type=line_type,
                    content=content,
                    old_lineno=line.source_line_no or None,
                    new_lineno=line.target_line_no or None,
                ))
            hunks.append(DiffHunk(
                header=str(hunk).split("\n", 1)[0],
                lines=lines,
            ))

        files.append(DiffFile(
            path=path,
            old_path=old_path,
            status=_file_status(pf),
            hunks=hunks,
            added_lines=pf.added,
            removed_lines=pf.removed,
        ))

    return DiffData(files=files)
