"""Tests for the diff parser module."""

from pathlib import Path

from prview.diff_parser import parse
from prview.models import DiffData


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _load_sample() -> DiffData:
    text = (FIXTURE_DIR / "sample.diff").read_text()
    return parse(text)


class TestSampleDiff:
    """Tests against the hand-crafted sample.diff fixture."""

    def test_file_count(self):
        data = _load_sample()
        assert len(data.files) == 4

    def test_added_file(self):
        data = _load_sample()
        f = data.files[0]
        assert f.path == "utils/helpers.py"
        assert f.status == "added"
        assert f.old_path is None
        assert f.added_lines == 4
        assert f.removed_lines == 0
        assert len(f.hunks) == 1

    def test_modified_file(self):
        data = _load_sample()
        f = data.files[1]
        assert f.path == "src/app.py"
        assert f.status == "modified"
        assert f.old_path is None
        assert len(f.hunks) == 2
        assert f.added_lines == 4
        assert f.removed_lines == 2

    def test_modified_file_hunk_headers(self):
        data = _load_sample()
        f = data.files[1]
        assert "@@ -1,7 +1,8 @@" in f.hunks[0].header
        assert "@@ -20,6 +21,7 @@" in f.hunks[1].header

    def test_deleted_file(self):
        data = _load_sample()
        f = data.files[2]
        assert f.path == "old_config.py"
        assert f.status == "deleted"
        assert f.old_path is None
        assert f.added_lines == 0
        assert f.removed_lines == 5
        assert len(f.hunks) == 1

    def test_renamed_file(self):
        data = _load_sample()
        f = data.files[3]
        assert f.path == "src/settings.py"
        assert f.status == "renamed"
        assert f.old_path == "src/config.py"
        assert f.added_lines == 3
        assert f.removed_lines == 2
        assert len(f.hunks) == 1

    def test_line_types_first_hunk_of_modified(self):
        """Check individual DiffLine objects in the first hunk of the modified file."""
        data = _load_sample()
        hunk = data.files[1].hunks[0]

        # First line is context
        assert hunk.lines[0].type == "context"
        assert hunk.lines[0].content == '"""Main application module."""'

        # Find the added 'import sys' line
        added = [l for l in hunk.lines if l.type == "add"]
        assert any("import sys" in l.content for l in added)

        # Find the removed 'print("hello")' line
        removed = [l for l in hunk.lines if l.type == "remove"]
        assert any('print("hello")' in l.content for l in removed)

    def test_line_numbers(self):
        """Context lines should have both old and new line numbers."""
        data = _load_sample()
        hunk = data.files[1].hunks[0]
        context_lines = [l for l in hunk.lines if l.type == "context"]
        for cl in context_lines:
            assert cl.old_lineno is not None
            assert cl.new_lineno is not None

        # Added lines should only have new_lineno
        add_lines = [l for l in hunk.lines if l.type == "add"]
        for al in add_lines:
            assert al.new_lineno is not None
            assert al.old_lineno is None

        # Removed lines should only have old_lineno
        rem_lines = [l for l in hunk.lines if l.type == "remove"]
        for rl in rem_lines:
            assert rl.old_lineno is not None
            assert rl.new_lineno is None


class TestEdgeCases:
    def test_empty_string(self):
        data = parse("")
        assert isinstance(data, DiffData)
        assert data.files == []

    def test_whitespace_only(self):
        data = parse("   \n\n  ")
        assert isinstance(data, DiffData)
        assert data.files == []
