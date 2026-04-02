import json
from pathlib import Path


class ReviewState:
    def __init__(self, state_dir: str | Path | None = None):
        if state_dir is None:
            self._state_dir = Path.cwd() / ".prview"
        else:
            self._state_dir = Path(state_dir)
        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = self._state_dir / "reviews.json"
        self._reviewed: set[str] = self._load()

    def _load(self) -> set[str]:
        try:
            data = json.loads(self._state_file.read_text())
            return set(data["reviewed"])
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            return set()

    def _save(self) -> None:
        data = {"version": 1, "reviewed": sorted(self._reviewed)}
        self._state_file.write_text(json.dumps(data, indent=2) + "\n")

    def is_reviewed(self, file_path: str) -> bool:
        return file_path in self._reviewed

    def toggle_reviewed(self, file_path: str) -> None:
        if file_path in self._reviewed:
            self._reviewed.discard(file_path)
        else:
            self._reviewed.add(file_path)
        self._save()

    def reviewed_files(self) -> set[str]:
        return set(self._reviewed)

    def clear(self) -> None:
        self._reviewed.clear()
        self._save()
