import os

import pytest

from src.shared.config import validate_required_env


def test_validate_required_env_accepts_core_settings(monkeypatch):
    for key, value in {
        "EXPECTED_PLC_COUNT": "15",
        "CYCLE_INTERVAL_MINUTES": "5",
        "CYCLE_SCHEDULE": "0 */5 * * * *",
        "CYCLE_QUEUE_NAME": "aggregation-cycles",
        "CYCLE_GRACE_SECONDS": "90",
        "FETCH_OVERLAP_MINUTES": "15",
        "AGGREGATION_MODE": "permissive",
        "WRITEBACK_MODE": "dry_run",
        "LAST_KNOWN_VALUE_POLICY": "carry_forward",
        "ZERO_FILL_DISABLED": "true",
        "PLC_STALE_TIMEOUT_SECONDS": "300",
        "PLC_OFFLINE_TIMEOUT_SECONDS": "600",
        "MAX_RETRIES": "3",
        "RETRY_BASE_SECONDS": "10",
        "CYCLE_TABLE_STATUS": "CycleStatus",
        "CYCLE_TABLE_SNAPSHOT": "CycleDataSnapshot",
        "CYCLE_TABLE_AUDIT": "CycleAudit",
        "CYCLE_TABLE_LATEST": "LatestObservation",
        "RETENTION_HOURS": "48",
        "KEYVAULT_URI": "https://example.vault.azure.net/",
    }.items():
        monkeypatch.setenv(key, value)

    config = validate_required_env()
    assert config["EXPECTED_PLC_COUNT"] == 15
    assert config["CYCLE_GRACE_SECONDS"] == 90
    assert config["AGGREGATION_MODE"] == "permissive"
    assert config["ZERO_FILL_DISABLED"] is True


def test_validate_required_env_raises_for_missing_settings(monkeypatch):
    for key in [
        "EXPECTED_PLC_COUNT",
        "CYCLE_INTERVAL_MINUTES",
        "CYCLE_SCHEDULE",
        "CYCLE_QUEUE_NAME",
        "CYCLE_GRACE_SECONDS",
        "FETCH_OVERLAP_MINUTES",
        "AGGREGATION_MODE",
        "WRITEBACK_MODE",
        "LAST_KNOWN_VALUE_POLICY",
        "ZERO_FILL_DISABLED",
        "PLC_STALE_TIMEOUT_SECONDS",
        "PLC_OFFLINE_TIMEOUT_SECONDS",
        "MAX_RETRIES",
        "RETRY_BASE_SECONDS",
        "CYCLE_TABLE_STATUS",
        "CYCLE_TABLE_SNAPSHOT",
        "CYCLE_TABLE_AUDIT",
        "CYCLE_TABLE_LATEST",
        "RETENTION_HOURS",
        "KEYVAULT_URI",
    ]:
        monkeypatch.delenv(key, raising=False)

    try:
        validate_required_env()
        assert False, "Expected ValueError for missing environment settings"
    except ValueError:
        pass


