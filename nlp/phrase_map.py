"""Phrase matching helpers for the controlled domain vocabulary."""

import json
from pathlib import Path
from typing import Any

from .normalizer import normalize_text


class PhraseMap:
    def __init__(self, entries: list[dict[str, Any]]):
        self.entries = entries
        self._validate()

    @classmethod
    def from_json(cls, path: str | Path) -> "PhraseMap":
        with Path(path).open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return cls(data["phrases"])

    def _validate(self) -> None:
        seen = set()
        for entry in self.entries:
            if not entry.get("phrase") or not entry.get("fact"):
                raise ValueError("Each phrase entry needs phrase and fact")
            key = normalize_text(entry["phrase"])
            if key in seen:
                raise ValueError(f"Duplicate normalized phrase: {key}")
            seen.add(key)

    def matches(self, text: str) -> list[dict[str, Any]]:
        normalized = f" {normalize_text(text)} "
        found = []
        for entry in sorted(self.entries, key=lambda item: len(normalize_text(item["phrase"])), reverse=True):
            phrase = normalize_text(entry["phrase"])
            if f" {phrase} " in normalized:
                found.append({**entry, "matched_phrase": phrase})
        return found
