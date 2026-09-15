from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from scripts.probe_brightlayer_device import (
    DEVICE_REGISTRY_PATH,
    _format_api_utc,
    _get_timeseries,
    _load_test_device_registry,
    _registry_probe_inputs,
    _targeted_probe_inputs,
)


def test_format_api_utc_uses_whole_seconds_and_z_suffix():
    value = datetime(
        2026,
        8,
        31,
        10,
        15,
        42,
        123456,
        tzinfo=timezone(timedelta(hours=2)),
    )

    assert _format_api_utc(value) == "2026-08-31T08:15:42Z"


def test_device_registry_contains_confirmed_parent_and_traits():
    device = _load_test_device_registry(DEVICE_REGISTRY_PATH)

    assert device["organizationId"] == "8427fc24-b752-436a-8ac9-0c9318992fc3"
    assert device["organizationCode"] == "C95FF99D-421B-47D9-AD28-654B4760D7B3"
    assert device["gatewayId"] == "cb118f9e-3a25-4e1f-8f37-f9a37c48c1cb"
    assert device["gatewayName"] == "165_Evale"
    assert device["childDeviceName"] == "Nam5"
    assert device["childDeviceId"] == "8a7f416d-a452-2b11-0800-1e0d06362200"
    assert device["traitIds"] == ["10549363", "10549365", "10549432"]


def test_registry_quick_probe_uses_one_child_pair_and_fifteen_minute_window():
    device = _load_test_device_registry(DEVICE_REGISTRY_PATH)
    end = datetime(2026, 9, 3, 10, 30, tzinfo=timezone.utc)

    result = _registry_probe_inputs(device, quick_mode=True, end=end)

    assert result == (
        "8a7f416d-a452-2b11-0800-1e0d06362200",
        ["10549363"],
        "2026-09-03T10:15:00Z",
        "2026-09-03T10:30:00Z",
    )


def test_get_timeseries_sends_all_requested_pairs_in_one_call():
    client = MagicMock()
    client.get_timeseries.return_value = {
        "timeSeries": [{"tagTrait": str(index)} for index in range(12)]
    }
    pairs = [{"deviceId": "device", "tagTrait": str(index)} for index in range(12)]

    response = _get_timeseries(client, pairs, "start", "end")

    client.get_timeseries.assert_called_once_with(pairs, "start", "end")
    assert len(response["timeSeries"]) == 12


def test_targeted_probe_inputs_use_documented_numeric_traits_and_utc_window():
    result = _targeted_probe_inputs({
        "BRIGHTLAYER_PROBE_DEVICE_ID": "device-1",
        "BRIGHTLAYER_PROBE_TRAIT_IDS": "10549363, 10549365",
        "BRIGHTLAYER_PROBE_START_UTC": "2026-09-01T00:00:00Z",
        "BRIGHTLAYER_PROBE_END_UTC": "2026-09-01T12:00:00Z",
    })

    assert result == (
        "device-1",
        ["10549363", "10549365"],
        "2026-09-01T00:00:00Z",
        "2026-09-01T12:00:00Z",
    )


def test_targeted_probe_inputs_reject_partial_configuration():
    with pytest.raises(RuntimeError, match="Set BRIGHTLAYER_PROBE_DEVICE_ID"):
        _targeted_probe_inputs({"BRIGHTLAYER_PROBE_DEVICE_ID": "device-1"})