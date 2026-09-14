from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict


SCHEMA_VERSION = 1


def _parse_utc(value: str, field_name: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must include a timezone")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class CycleWorkItem:
    schemaVersion: int
    cycleKey: str
    cycleStartUtc: str
    cycleEndUtc: str
    correlationId: str

    def __post_init__(self) -> None:
        if self.schemaVersion != SCHEMA_VERSION:
            raise ValueError(f"Unsupported cycle work-item schema version: {self.schemaVersion}")
        if not self.cycleKey or not self.correlationId:
            raise ValueError("cycleKey and correlationId are required")
        start = _parse_utc(self.cycleStartUtc, "cycleStartUtc")
        end = _parse_utc(self.cycleEndUtc, "cycleEndUtc")
        if end <= start:
            raise ValueError("cycleEndUtc must be later than cycleStartUtc")

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"), sort_keys=True)

    @classmethod
    def from_json(cls, payload: str) -> "CycleWorkItem":
        try:
            data: Dict[str, Any] = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError("Cycle work item must be valid JSON") from exc
        if not isinstance(data, dict):
            raise ValueError("Cycle work item must be a JSON object")
        try:
            return cls(**data)
        except TypeError as exc:
            raise ValueError("Cycle work item has missing or unexpected fields") from exc