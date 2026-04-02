from prview.state import ReviewState


def test_toggle_on(tmp_path):
    state = ReviewState(tmp_path)
    state.toggle_reviewed("file.py")
    assert state.is_reviewed("file.py")


def test_toggle_off(tmp_path):
    state = ReviewState(tmp_path)
    state.toggle_reviewed("file.py")
    state.toggle_reviewed("file.py")
    assert not state.is_reviewed("file.py")


def test_reviewed_files(tmp_path):
    state = ReviewState(tmp_path)
    state.toggle_reviewed("a.py")
    state.toggle_reviewed("b.py")
    state.toggle_reviewed("c.py")
    assert state.reviewed_files() == {"a.py", "b.py", "c.py"}


def test_persistence(tmp_path):
    state = ReviewState(tmp_path)
    state.toggle_reviewed("file.py")
    state2 = ReviewState(tmp_path)
    assert state2.is_reviewed("file.py")


def test_clear(tmp_path):
    state = ReviewState(tmp_path)
    state.toggle_reviewed("a.py")
    state.toggle_reviewed("b.py")
    state.clear()
    assert not state.is_reviewed("a.py")
    assert not state.is_reviewed("b.py")


def test_missing_dir(tmp_path):
    new_dir = tmp_path / "sub" / "dir"
    state = ReviewState(new_dir)
    assert new_dir.exists()
    assert state.reviewed_files() == set()


def test_corrupt_json(tmp_path):
    reviews_file = tmp_path / "reviews.json"
    reviews_file.write_text("not valid json {{{")
    state = ReviewState(tmp_path)
    assert state.reviewed_files() == set()


def test_empty_state(tmp_path):
    state = ReviewState(tmp_path)
    assert state.reviewed_files() == set()
