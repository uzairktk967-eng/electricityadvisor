"""Evidence-aware fact storage with type and domain validation."""

from collections import defaultdict
from typing import Any, Iterable

from .models import FactRecord

VALID_STATUSES = {"confirmed", "rejected", "uncertain", "missing"}


class FactValidationError(ValueError):
    """Raised when a fact value is incompatible with its catalogue definition."""


class FactStore:
    def __init__(self, fact_catalogue: dict[str, Any]):
        self._definitions = {item["id"]: item for item in fact_catalogue.get("facts", [])}
        self._records: dict[str, list[FactRecord]] = defaultdict(list)

    def add(
        self,
        fact_id: str,
        value: Any = None,
        *,
        status: str = "confirmed",
        source: str = "user_input",
        note: str = "",
    ) -> FactRecord:
        if fact_id not in self._definitions:
            raise FactValidationError(f"Unknown fact: {fact_id}")
        if status not in VALID_STATUSES:
            raise FactValidationError(f"Unsupported evidence status: {status}")
        if status != "missing":
            self._validate_value(fact_id, value)
        elif value is not None:
            raise FactValidationError("A missing fact must have value=None")
        record = FactRecord(fact_id, value, status, source, note)
        self._records[fact_id].append(record)
        return record

    def extend(self, records: Iterable[FactRecord]) -> None:
        for record in records:
            self.add(
                record.fact_id,
                record.value,
                status=record.status,
                source=record.source,
                note=record.note,
            )

    def records(self, fact_id: str) -> list[FactRecord]:
        return list(self._records.get(fact_id, []))

    def all_records(self) -> dict[str, list[FactRecord]]:
        return {key: list(value) for key, value in self._records.items()}

    def evidence(self, fact_id: str) -> dict[str, Any]:
        records = self._records.get(fact_id, [])
        confirmed = [record.value for record in records if record.status == "confirmed"]
        unique_confirmed = []
        for value in confirmed:
            if value not in unique_confirmed:
                unique_confirmed.append(value)
        if len(unique_confirmed) > 1:
            return {"status": "conflict", "value": None, "records": records}
        if len(unique_confirmed) == 1:
            return {"status": "confirmed", "value": unique_confirmed[0], "records": records}
        statuses = {record.status for record in records}
        if "uncertain" in statuses:
            status = "uncertain"
        elif "rejected" in statuses:
            status = "rejected"
        elif "missing" in statuses:
            status = "missing"
        else:
            status = "missing"
        return {"status": status, "value": None, "records": records}

    def _validate_value(self, fact_id: str, value: Any) -> None:
        definition = self._definitions[fact_id]
        kind = definition["type"]
        valid = {
            "string": lambda v: isinstance(v, str),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "enum": lambda v: isinstance(v, (str, int, float, bool)),
        }[kind](value)
        if not valid:
            raise FactValidationError(f"{fact_id} expects {kind}, received {type(value).__name__}")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in definition and value < definition["minimum"]:
                raise FactValidationError(f"{fact_id} must be >= {definition['minimum']}")
            if "maximum" in definition and value > definition["maximum"]:
                raise FactValidationError(f"{fact_id} must be <= {definition['maximum']}")
        allowed = definition.get("allowed_values")
        if allowed is not None and value not in allowed:
            raise FactValidationError(f"{fact_id} must be one of {allowed}")
