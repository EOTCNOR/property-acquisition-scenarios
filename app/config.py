from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AppConfig:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.defaults_path = base_path / "config" / "app_defaults.json"
        self.labels_path = base_path / "config" / "ui_labels.json"
        self.defaults = self._load_json(self.defaults_path)
        self.labels = self._load_json(self.labels_path)

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def default(self, section: str, key: str, fallback: Any) -> Any:
        entry = self.defaults.get(section, {}).get(key)
        if isinstance(entry, dict):
            return entry.get("value", fallback)
        return entry if entry is not None else fallback

    def description(self, section: str, key: str, fallback: str) -> str:
        entry = self.defaults.get(section, {}).get(key)
        if isinstance(entry, dict):
            return entry.get("description", fallback)
        return fallback

    def label(self, path: str, fallback: str) -> str:
        value: Any = self.labels
        for part in path.split("."):
            if not isinstance(value, dict) or part not in value:
                return fallback
            value = value[part]
        return value if isinstance(value, str) else fallback

