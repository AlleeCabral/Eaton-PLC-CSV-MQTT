from unittest.mock import MagicMock

import pytest

from src.modules.process_cycle import IncompleteCycleError, process_cycle_work_item
from src.shared.cycle_message import CycleWorkItem

ENABLED_CONFIG = {"AGGREGATION_MODE": "permissive", "WRITEBACK_MODE": "enabled"}
DRY_RUN_CONFIG = {"AGGREGATION_MODE": "permissive", "WRITEBACK_MODE": "dry_run"}


ITEM = CycleWorkItem(
    schemaVersion=1,
    cycleKey="2026-08-24T10:00:00Z",
    cycleStartUtc="2026-08-24T10:00:00+00:00",
    cycleEndUtc="2026-08-24T10:05:00+00:00",
    correlationId="run-1",
)


def make_context(fetch_result):
    repo = MagicMock()
    repo.get_status.return_value = {"status": "queued"}
    fetch = MagicMock()
    fetch.run.return_value = fetch_result
    aggregate = MagicMock()
    aggregate.run.return_value = {"results": {"production_today": {"value": 17, "status": "ok"}}}
    writeback = MagicMock()
    writeback.run.return_value = {"status": "sent", "pointCount": 1}
    return {
        "repo": repo,
        "devices": [
            {"deviceId": "d1", "tagTrait": "today"},
            {"deviceId": "d2", "tagTrait": "today"},
        ],
        "fetch_source_telemetry": fetch,
        "aggregate_cycle": aggregate,
        "writeback": writeback,
    }


def coverage(observed=2, carried=0, resolved=2, unresolved=0):
    return {
        "expectedPairCount": 2,
        "observedPairCount": observed,
        "carriedPairCount": carried,
        "resolvedPairCount": resolved,
        "unresolvedPairCount": unresolved,
    }


def test_enabled_permissive_worker_publishes_fully_resolved_carried_values():
    context = make_context(coverage(observed=1, carried=1))

    result = process_cycle_work_item(ITEM, context, ENABLED_CONFIG)

    assert result["status"] == "sent"
    assert result["coverage"]["carriedPairCount"] == 1
    context["writeback"].run.assert_called_once()
    assert context["repo"].upsert_status.call_args.args[0]["status"] == "sent"


def test_worker_rejects_unresolved_pairs_without_writeback():
    context = make_context(coverage(observed=1, resolved=1, unresolved=1))

    with pytest.raises(IncompleteCycleError, match="resolved 1/2"):
        process_cycle_work_item(ITEM, context, ENABLED_CONFIG)

    context["writeback"].run.assert_not_called()


def test_strict_worker_rejects_carried_pair():
    context = make_context(coverage(observed=1, carried=1))

    with pytest.raises(IncompleteCycleError, match="observed 1/2"):
        process_cycle_work_item(
            ITEM, context, {"AGGREGATION_MODE": "strict", "WRITEBACK_MODE": "enabled"}
        )


def test_worker_skips_already_sent_cycle_without_external_calls():
    context = make_context(coverage())
    context["repo"].get_status.return_value = {"status": "sent"}

    result = process_cycle_work_item(ITEM, context, ENABLED_CONFIG)

    assert result["status"] == "duplicate"
    context["fetch_source_telemetry"].run.assert_not_called()


def test_worker_rejects_empty_writeback_as_unsent():
    context = make_context(coverage())
    context["writeback"].run.return_value = {"status": "skipped", "pointCount": 0}

    with pytest.raises(IncompleteCycleError, match="no publishable"):
        process_cycle_work_item(ITEM, context, ENABLED_CONFIG)


def test_dry_run_persists_audit_without_writeback_dependency():
    context = make_context(coverage())
    context.pop("writeback")
    context["aggregate_cycle"].run.return_value = {
        "results": {
            "production_today": {
                "value": 17,
                "unit": "kWh",
                "status": "ok",
                "expectedSourceCount": 2,
                "sourceCount": 2,
                "freshSourceCount": 2,
                "staleSourceCount": 0,
                "offlineSourceCount": 0,
                "carriedSourceCount": 0,
            }
        }
    }

    result = process_cycle_work_item(ITEM, context, DRY_RUN_CONFIG)

    assert result["status"] == "dry_run_completed"
    assert result["candidatePayload"]["trends"][0]["name"] == "production_today"
    audit = context["repo"].upsert_audit.call_args.args[0]
    assert audit["mode"] == "dry_run"
    assert audit["candidatePointCount"] == 1
    assert "production_today" in audit["candidatePayloadJson"]
    assert context["repo"].upsert_status.call_args.args[0]["status"] == "dry_run_completed"


def test_dry_run_completed_cycle_is_idempotent():
    context = make_context(coverage())
    context["repo"].get_status.return_value = {"status": "dry_run_completed"}

    result = process_cycle_work_item(ITEM, context, DRY_RUN_CONFIG)

    assert result["status"] == "duplicate"
    context["fetch_source_telemetry"].run.assert_not_called()
    context["repo"].upsert_audit.assert_not_called()