import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.modules.writeback_to_brightlayer import WritebackToBrightlayer, build_trends_payload

AGGREGATES = {
    "total_flow": {"value": 15.33, "unit": "m3/h", "sourceCount": 2, "status": "ok"},
    "avg_pressure": {"value": 2.1, "unit": "bar", "sourceCount": 1, "status": "ok"},
    "total_energy": {"value": None, "unit": "kWh", "sourceCount": 0, "status": "no_data"},
}

KPI_TAG_MAP = {
    "total_flow": "10462371",
    "avg_pressure": "10462372",
    "total_energy": "10415480",
}


def test_build_trends_payload_includes_only_ok_kpis():
    now = datetime(2025, 7, 17, 8, 5, 0, tzinfo=timezone.utc)
    payload = build_trends_payload(AGGREGATES, KPI_TAG_MAP, now)

    assert len(payload["trends"]) == 2
    tag_ids = {point["c"] for point in payload["trends"]}
    assert tag_ids == {"10462371", "10462372"}


def test_build_trends_payload_uses_epoch_seconds():
    now = datetime(2025, 7, 17, 8, 5, 0, tzinfo=timezone.utc)
    payload = build_trends_payload(AGGREGATES, KPI_TAG_MAP, now)
    expected_epoch = int(now.timestamp())
    assert all(point["t"] == expected_epoch for point in payload["trends"])


def test_build_trends_payload_skips_kpi_missing_from_tag_map():
    aggregates = {"unmapped_kpi": {"value": 1.0, "unit": "x", "sourceCount": 1, "status": "ok"}}
    payload = build_trends_payload(aggregates, {}, datetime.now(timezone.utc))
    assert payload["trends"] == []


def test_run_publishes_message_and_disconnects():
    fake_client = MagicMock()
    factory = MagicMock(return_value=fake_client)

    writeback = WritebackToBrightlayer(factory, KPI_TAG_MAP, config={})
    result = writeback.run("2025-07-17T08:05:00Z", AGGREGATES)

    fake_client.connect.assert_called_once()
    fake_client.send_message.assert_called_once()
    fake_client.disconnect.assert_called_once()

    sent_message = fake_client.send_message.call_args.args[0]
    sent_payload = json.loads(sent_message.data)
    assert len(sent_payload["trends"]) == 2

    assert result["status"] == "sent"
    assert result["pointCount"] == 2


def test_run_skips_publish_when_no_ok_kpis():
    factory = MagicMock()
    all_no_data = {"total_energy": {"value": None, "unit": "kWh", "sourceCount": 0, "status": "no_data"}}

    writeback = WritebackToBrightlayer(factory, KPI_TAG_MAP, config={})
    result = writeback.run("2025-07-17T08:05:00Z", all_no_data)

    factory.assert_not_called()
    assert result["status"] == "skipped"
    assert result["reason"] == "no_ok_kpis"
