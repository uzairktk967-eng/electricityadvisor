"""Extract explicit fact candidates without making inference decisions."""

from dataclasses import asdict, dataclass
import re
from pathlib import Path
from typing import Any

from .normalizer import normalize_text
from .phrase_map import PhraseMap


@dataclass(frozen=True)
class FactCandidate:
    fact_id: str
    value: Any
    status: str
    source_text: str
    matched_text: str
    confidence: float
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_PHRASE_MAP = Path(__file__).resolve().parent / "domain_phrases.json"
NUMBER = r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"

# Each pattern requires a named numeric value and its domain label/unit.
NUMERIC_PATTERNS = {
    "appliance.rated_power_w": re.compile(
        rf"(?:rated\s+power|power\s+rating|rating)\s*(?:is|of|:|=)?\s*{NUMBER}\s*(?:w|watt|watts)\b"
    ),
    "appliance.standby_power_w": re.compile(
        rf"standby\s+(?:power|consumption)\s*(?:is|of|:|=)?\s*{NUMBER}\s*(?:w|watt|watts)\b"
    ),
    "appliance.quantity": re.compile(
        rf"(?:quantity|number\s+of\s+appliances|i\s+have)\s*(?:is|are|of|:|=)?\s*{NUMBER}"
    ),
    "usage.hours_per_day": re.compile(
        rf"(?:used?\s+for|usage|operating\s+time)\s*(?:is|of|:|=)?\s*{NUMBER}\s*(?:hours?|hrs?)\s*(?:per|/)\s*day"
    ),
    "usage.standby_hours_per_day": re.compile(
        rf"standby\s+(?:time|hours?)\s*(?:is|of|:|=)?\s*{NUMBER}\s*(?:hours?|hrs?)\s*(?:per|/)\s*day"
    ),
    "usage.days_per_month": re.compile(
        rf"{NUMBER}\s*days?\s*(?:per|/)\s*month"
    ),
    "tariff.price_per_kwh": re.compile(
        rf"(?:tariff|rate|price)\s*(?:is|of|:|=)?\s*{NUMBER}\s*(?:per\s*)?(?:kwh|unit)\b"
    ),
}

UNCERTAINTY = re.compile(r"\b(maybe|perhaps|approximately|approx|around|about|not sure|i think)\b")
NEGATION = re.compile(r"\b(no|not|never|without|don't|doesn't|isn't|aren't|cannot|can't)\b")


def _status_for_span(text: str, start: int, end: int, *, boolean: bool = False) -> tuple[str, str]:
    prefix = text[max(0, start - 35):start]
    span = text[start:end]
    if UNCERTAINTY.search(prefix) or UNCERTAINTY.search(span):
        return "uncertain", "Nearby uncertainty wording; confirm before using."
    if boolean and NEGATION.search(prefix):
        return "rejected", "Negation detected near the matched phrase."
    return "confirmed", ""


def _number(raw: str) -> int | float:
    value = float(raw.replace(",", ""))
    return int(value) if value.is_integer() else value


def extract_facts(text: str, phrase_map_path: str | Path | None = None) -> list[FactCandidate]:
    """Return candidate facts only; callers must confirm them before inference."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    normalized = normalize_text(text)
    if not normalized:
        return []
    phrase_map = PhraseMap.from_json(phrase_map_path or DEFAULT_PHRASE_MAP)
    candidates: list[FactCandidate] = []

    for fact_id, pattern in NUMERIC_PATTERNS.items():
        for match in pattern.finditer(normalized):
            value = _number(match.group(1))
            status, note = _status_for_span(normalized, match.start(), match.end())
            candidates.append(FactCandidate(
                fact_id, value, status, text, match.group(0), 0.95 if status == "confirmed" else 0.55, note
            ))

    for entry in phrase_map.matches(normalized):
        fact_id = entry["fact"]
        value = entry.get("value")
        start = normalized.find(entry["matched_phrase"])
        end = start + len(entry["matched_phrase"])
        status, note = _status_for_span(normalized, start, end, boolean=entry.get("type") == "boolean")
        candidates.append(FactCandidate(
            fact_id, value, status, text, entry["matched_phrase"],
            0.95 if status == "confirmed" else 0.55, note
        ))

    deduplicated: dict[tuple[str, str], FactCandidate] = {}
    for candidate in candidates:
        key = (candidate.fact_id, candidate.matched_text)
        deduplicated[key] = candidate
    return list(deduplicated.values())
