"""Typed result models used by the inference engine."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class FactRecord:
    fact_id: str
    value: Any
    status: str = "confirmed"
    source: str = "user_input"
    note: str = ""


@dataclass
class ConclusionResult:
    conclusion_id: str
    value: Any
    unit: str | None
    rule_ids: list[str] = field(default_factory=list)
    priority: int = 0
    caveat: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InferenceResult:
    conclusions: dict[str, ConclusionResult]
    fired_rules: list[str]
    trace: list[dict[str, Any]]
    conflicts: list[dict[str, Any]]
    iterations: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "conclusions": {key: value.to_dict() for key, value in self.conclusions.items()},
            "fired_rules": list(self.fired_rules),
            "trace": list(self.trace),
            "conflicts": list(self.conflicts),
            "iterations": self.iterations,
        }


@dataclass
class BackwardQueryResult:
    target: str
    alternatives: list[dict[str, Any]]
    trace: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
