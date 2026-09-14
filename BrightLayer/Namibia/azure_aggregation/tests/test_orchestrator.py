from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.modules.orchestrator import plan_cycle, run_cycle_pipeline

CONFIG = {
    "CYCLE_GRACE_SECONDS": 90,
    "EXPECTED_PLC_COUNT": 2,
}


def test_plan_cycle_creates_new_open_cycle():
    repo = MagicMock()
    repo.get_status.return_value = None

    now = datetime(2025, 6, 1, 10, 16, tzinfo=timezone.utc)
    plan = plan_cycle(now, CONFIG, repo)

    assert plan["cycleKey"] == "2025-06-01T10:15:00Z"
    assert plan["status"] == "open"
    assert plan["receivedCount"] == 0
    repo.upsert_status.assert_called_once()
    upserted = repo.upsert_status.call_args.args[0]
    assert upserted["status"] == "open"


def test_plan_cycle_refreshes_existing_cycle_to_ready():
    repo = MagicMock()
    repo.get_status.return_value = {"status": "open", "receivedCount": 2}

    now = datetime(2025, 6, 1, 10, 16, tzinfo=timezone.utc)
    plan = plan_cycle(now, CONFIG, repo)

    assert plan["status"] == "ready"
    assert plan["receivedCount"] == 2


def test_plan_cycle_does_not_recompute_terminal_status():
    repo = MagicMock()
    repo.get_status.return_value = {"status": "sent", "receivedCount": 2}

    now = datetime(2025, 6, 1, 10, 16, tzinfo=timezone.utc)
    plan = plan_cycle(now, CONFIG, repo)

    assert plan["status"] == "sent"


CYCLE_PLAN = {
    "cycleKey": "2025-06-01T10:15:00Z",
    "cycleStartUtc": "2025-06-01T10:15:00+00:00",
    "cycleEndUtc": "2025-06-01T10:20:00+00:00",
    "graceDeadlineUtc": "2999-01-01T00:00:00+00:00",
    "status": "open",
    "expectedCount": 2,
    "receivedCount": 0,
}


PIPELINE_CONFIG = {"MAX_RETRIES": 3}


def test_run_cycle_pipeline_stays_open_when_not_enough_data():
    fetch = MagicMock()
    fetch.run.return_value = {"receivedCount": 1}
    repo = MagicMock()

    result = run_cycle_pipeline(CYCLE_PLAN, fetch, MagicMock(), MagicMock(), repo, devices=[], config=PIPELINE_CONFIG)

    assert result["status"] == "open"
    assert "aggregate" not in result


def test_run_cycle_pipeline_aggregates_and_publishes_when_ready():
    fetch = MagicMock()
    fetch.run.return_value = {"receivedCount": 2}
    aggregate = MagicMock()
    aggregate.run.return_value = {"results": {"total_flow": {"value": 10, "status": "ok"}}}
    writeback = MagicMock()
    writeback.run.return_value = {"status": "sent", "pointCount": 1}
    repo = MagicMock()

    result = run_cycle_pipeline(CYCLE_PLAN, fetch, aggregate, writeback, repo, devices=[], config=PIPELINE_CONFIG)

    aggregate.run.assert_called_once_with("2025-06-01T10:15:00Z")
    writeback.run.assert_called_once()
    assert result["status"] == "sent"
    assert result["writeback"]["status"] == "sent"


def test_run_cycle_pipeline_stays_open_on_first_failure_for_retry():
    fetch = MagicMock()
    fetch.run.return_value = {"receivedCount": 2}
    aggregate = MagicMock()
    aggregate.run.return_value = {"results": {}}
    writeback = MagicMock()
    writeback.run.side_effect = Exception("boom")
    repo = MagicMock()
    repo.get_status.return_value = None

    result = run_cycle_pipeline(CYCLE_PLAN, fetch, aggregate, writeback, repo, devices=[], config=PIPELINE_CONFIG)

    assert result["status"] == "open"
    assert result["retryCount"] == 1
    assert "boom" in result["error"]


def test_run_cycle_pipeline_marks_failed_once_max_retries_reached():
    fetch = MagicMock()
    fetch.run.return_value = {"receivedCount": 2}
    aggregate = MagicMock()
    aggregate.run.return_value = {"results": {}}
    writeback = MagicMock()
    writeback.run.side_effect = Exception("boom")
    repo = MagicMock()
    repo.get_status.return_value = {"retryCount": 2}

    result = run_cycle_pipeline(CYCLE_PLAN, fetch, aggregate, writeback, repo, devices=[], config=PIPELINE_CONFIG)

    assert result["status"] == "failed"
    assert result["retryCount"] == 3


def test_run_cycle_pipeline_clears_retry_state_on_success_after_failure():
    fetch = MagicMock()
    fetch.run.return_value = {"receivedCount": 2}
    aggregate = MagicMock()
    aggregate.run.return_value = {"results": {}}
    writeback = MagicMock()
    writeback.run.return_value = {"status": "sent"}
    repo = MagicMock()

    result = run_cycle_pipeline(CYCLE_PLAN, fetch, aggregate, writeback, repo, devices=[], config=PIPELINE_CONFIG)

    assert result["status"] == "sent"
    final_upsert = repo.upsert_status.call_args.args[0]
    assert final_upsert["retryCount"] == 0
    assert final_upsert["lastError"] == ""


def test_run_cycle_pipeline_no_longer_propagates_exceptions():
    """Superseded by the retry/failure tests above — exceptions are now caught."""
    fetch = MagicMock()
    fetch.run.return_value = {"receivedCount": 2}
    aggregate = MagicMock()
    aggregate.run.return_value = {"results": {}}
    writeback = MagicMock()
    writeback.run.side_effect = Exception("boom")
    repo = MagicMock()
    repo.get_status.return_value = None

    result = run_cycle_pipeline(CYCLE_PLAN, fetch, aggregate, writeback, repo, devices=[], config=PIPELINE_CONFIG)
    assert result["status"] in ("open", "failed")
