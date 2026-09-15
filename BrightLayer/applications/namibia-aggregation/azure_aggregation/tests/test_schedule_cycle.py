from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.modules.schedule_cycle import schedule_completed_cycle
from src.shared.cycle_message import CycleWorkItem


def test_schedule_completed_cycle_claims_and_returns_message():
    repo = MagicMock()
    repo.claim_cycle.return_value = True
    now = datetime(2026, 8, 24, 10, 17, 30, tzinfo=timezone.utc)

    result = schedule_completed_cycle(
        now,
        {"CYCLE_INTERVAL_MINUTES": 5},
        repo,
        correlation_id="run-1",
    )

    assert result["status"] == "queued"
    message = CycleWorkItem.from_json(result["message"])
    assert message.cycleKey == "2026-08-24T10:10:00Z"
    assert message.cycleStartUtc == "2026-08-24T10:10:00+00:00"
    assert message.cycleEndUtc == "2026-08-24T10:15:00+00:00"
    repo.claim_cycle.assert_called_once()


def test_schedule_completed_cycle_does_not_emit_duplicate_message():
    repo = MagicMock()
    repo.claim_cycle.return_value = False

    result = schedule_completed_cycle(
        datetime(2026, 8, 24, 10, 15, tzinfo=timezone.utc),
        {"CYCLE_INTERVAL_MINUTES": 5},
        repo,
        correlation_id="run-2",
    )

    assert result == {
        "cycleKey": "2026-08-24T10:10:00Z",
        "status": "duplicate",
        "message": None,
    }