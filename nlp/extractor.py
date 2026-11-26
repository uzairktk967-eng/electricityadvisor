"""Extract explicit fact candidates without making inference decisions.

The extractor intentionally handles one appliance profile at a time. A paragraph
containing several different appliance profiles must not be flattened into one
set of facts because that would create false evidence conflicts.
"""

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
OPTIONAL_COPULA = r"\s*(?:(?:is|are|of|at|around|about)\s*)?"
HOURS = r"(?:hours?|hrs?|h)"
PER_DAY = r"(?:per\s+day|a\s+day|each\s+day|daily|/\s*day)"

# Accept common plain-English alternatives while keeping every number tied to
# a recognizable label and unit. Generic power/hour patterns deliberately
# exclude standby wording, which has its own fact identifiers.
NUMERIC_PATTERNS = {
    "appliance.rated_power_w": re.compile(
        rf"(?<!standby\s)(?:rated\s+power|power\s+rating|rated\s+at|"
        rf"rated|rating|power\s+is|power\s+of|draws?|consumes?)"
        rf"{OPTIONAL_COPULA}{NUMBER}\s*(?:w|watt|watts)\b"
    ),
    "appliance.standby_power_w": re.compile(
        rf"standby\s+(?:power|consumption)(?:\s+is|\s+of|\s*:|\s*=)?\s*"
        rf"{NUMBER}\s*(?:w|watt|watts)\b"
    ),
    "appliance.quantity": re.compile(
        rf"(?:quantity|number\s+of\s+appliances|i\s+have|there\s+are|"
        rf"we\s+have)\s*(?:is|are|of|:|=)?\s*"
        rf"({NUMBER}|one|two|three|four|five|six|seven|eight|nine|ten)\b"
    ),
    "usage.hours_per_day": re.compile(
        rf"(?<!standby\s)(?:used?\s+for|runs?\s*(?:for)?|run\s+for|"
        rf"operates?\s+for|operating\s+for|works?\s+for|"
        rf"usage(?:\s+time)?|operating\s+time)"
        rf"\s*(?:(?:is|of|for)\s*)?{NUMBER}\s*{HOURS}\s*{PER_DAY}\b"
    ),
    "usage.standby_hours_per_day": re.compile(
        rf"standby\s+(?:time|hours?)(?:\s+is|\s+of|\s*:|\s*=)?\s*"
        rf"{NUMBER}\s*{HOURS}\s*{PER_DAY}\b"
    ),
    "usage.days_per_month": re.compile(
        rf"(?:for\s+)?{NUMBER}\s*days?\s*(?:per\s+month|a\s+month|"
        rf"each\s+month|in\s+the\s+month|monthly)"
    ),
    "tariff.price_per_kwh": re.compile(
        rf"(?:tariff|rate|price)(?:\s+is|\s+of|\s*:|\s*=)?\s*"
        rf"(?:rs\.?\s*)?(?:rupees?\s*)?{NUMBER}\s*"
        rf"(?:rs\.?\s*)?(?:rupees?\s*)?(?:per\s*)?(?:kwh|unit)\b"
    ),
}

WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
UNCERTAINTY = re.compile(r"\b(maybe|perhaps|approximately|approx|around|about|not sure|i think)\b")
NEGATION = re.compile(r"\b(no|not|never|without|don't|doesn't|isn't|aren't|cannot|can't)\b")


def _status_for_span(text: str, start: int, end: int, *, boolean: bool = False) -> tuple[str, str]:
    prefix = text[max(0, start - 45):start]
    span = text[start:end]
    if UNCERTAINTY.search(prefix) or UNCERTAINTY.search(span):
        return "uncertain", "Nearby uncertainty wording; confirm before using."
    if boolean and NEGATION.search(prefix):
        return "rejected", "Negation detected near the matched phrase."
    return "confirmed", ""


def _number(raw: str) -> int | float:
    normalized = raw.casefold()
    if normalized in WORD_NUMBERS:
        return WORD_NUMBERS[normalized]
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
                fact_id, value, status, text, match.group(0),
                0.95 if status == "confirmed" else 0.55, note
            ))

    for entry in phrase_map.matches(normalized):
        fact_id = entry["fact"]
        value = entry.get("value")
        start = normalized.find(entry["matched_phrase"])
        end = start + len(entry["matched_phrase"])
        status, note = _status_for_span(
            normalized, start, end, boolean=entry.get("type") == "boolean"
        )
        candidates.append(FactCandidate(
            fact_id, value, status, text, entry["matched_phrase"],
            0.95 if status == "confirmed" else 0.55, note
        ))

    deduplicated: dict[tuple[str, str], FactCandidate] = {}
    for candidate in candidates:
        key = (candidate.fact_id, candidate.matched_text)
        deduplicated[key] = candidate
    return list(deduplicated.values())
