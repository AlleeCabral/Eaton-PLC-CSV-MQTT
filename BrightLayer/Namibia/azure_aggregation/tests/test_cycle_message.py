import json

import pytest

from src.shared.cycle_message import CycleWorkItem


def make_work_item(**overrides):
    values = {
        "schemaVersion": 1,
        "cycleKey": "2026-08-24T10:00:00Z",
        "cycleStartUtc": "2026-08-24T10:00:00+00:00",
        "cycleEndUtc": "2026-08-24T10:05:00+00:00",
        "correlationId": "run-1",
    }
    values.update(overrides)
    return CycleWorkItem(**values)


def test_cycle_work_item_round_trips_compact_json():
    item = make_work_item()

    restored = CycleWorkItem.from_json(item.to_json())

    assert restored == item
    assert json.loads(item.to_json())["schemaVersion"] == 1


def test_cycle_work_item_rejects_unsupported_schema():
    with pytest.raises(ValueError, match="Unsupported"):
        make_work_item(schemaVersion=2)


def test_cycle_work_item_rejects_invalid_bounds():
    with pytest.raises(ValueError, match="later than"):
        make_work_item(cycleEndUtc="2026-08-24T10:00:00+00:00")


def test_cycle_work_item_rejects_extra_fields():
    payload = make_work_item().to_json()
    values = json.loads(payload)
    values["secret"] = "must-not-be-accepted"

    with pytest.raises(ValueError, match="missing or unexpected"):
        CycleWorkItem.from_json(json.dumps(values))