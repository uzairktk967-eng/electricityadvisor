"""Deterministic text normalization and tokenization."""

import re
import unicodedata

TOKEN_PATTERN = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|[a-z]+(?:'[a-z]+)?", re.IGNORECASE)


def normalize_text(text: str) -> str:
    """Normalize Unicode, case, punctuation spacing and whitespace."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = normalized.replace("’", "'")
    normalized = re.sub(r"[^\w.,+'/-]+", " ", normalized, flags=re.UNICODE)
    return " ".join(normalized.split())


def tokenize(text: str) -> list[str]:
    """Return word and numeric tokens; grouped thousands and decimals stay intact."""
    return TOKEN_PATTERN.findall(normalize_text(text))
