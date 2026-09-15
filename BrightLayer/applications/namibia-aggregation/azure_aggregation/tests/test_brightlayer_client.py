import requests
from unittest.mock import MagicMock

import pytest

from src.shared.brightlayer_client import BrightlayerAuthError, BrightlayerClient


def make_response(status_code=200, json_data=None, text=""):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.json.return_value = json_data or {}
    response.raise_for_status = MagicMock()
    if status_code >= 400:
        response.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return response


def make_client(session):
    return BrightlayerClient(
        api_prefix="https://portal.machinery-monitoring.com",
        service_account_id="sa-id",
        service_account_secret="sa-secret",
        max_retries=1,
        retry_base_seconds=0,
        session=session,
    )


def test_get_token_success_and_caching():
    session = MagicMock()
    session.post.return_value = make_response(200, {"token": "abc123"})

    client = make_client(session)
    assert client.get_token() == "abc123"
    assert client.get_token() == "abc123"
    # Cached after first call - only one POST to the token endpoint.
    assert session.post.call_count == 1


def test_client_sets_headers_required_by_application_gateway():
    session = requests.Session()

    make_client(session)

    assert session.headers["Accept"] == "application/json"
    assert session.headers["User-Agent"] == "BrightlayerAggregation/1.0"


def test_get_token_raises_on_missing_token_field():
    session = MagicMock()
    session.post.return_value = make_response(200, {})

    client = make_client(session)
    with pytest.raises(BrightlayerAuthError):
        client.get_token()


def test_get_token_raises_on_non_200():
    session = MagicMock()
    session.post.return_value = make_response(401, text="unauthorized")

    client = make_client(session)
    with pytest.raises(BrightlayerAuthError):
        client.get_token()


def test_get_realtime_returns_parsed_json():
    session = MagicMock()
    session.post.return_value = make_response(200, {"token": "abc123"})
    session.request.return_value = make_response(
        200, {"v": {"unit": "bar", "value": "1.23"}, "dt": "2025-07-17T08:00:44Z"}
    )

    client = make_client(session)
    result = client.get_realtime("device-1", "10549349")

    assert result["v"]["value"] == "1.23"
    called_url = session.request.call_args.args[1]
    assert "device-1" in called_url
    assert session.request.call_args.kwargs["json"] == {"tagId": "10549349"}


def test_get_timeseries_builds_expected_body():
    session = MagicMock()
    session.post.return_value = make_response(200, {"token": "abc123"})
    session.request.return_value = make_response(200, {"timeSeries": []})

    client = make_client(session)
    devices = [{"deviceId": "device-1", "tagTrait": "10549349"}]
    result = client.get_timeseries(devices, "2025-07-15T00:00:00Z", None)

    assert result == {"timeSeries": []}
    body = session.request.call_args.kwargs["json"]
    assert body["devices"] == devices
    assert body["startDateTime"] == "2025-07-15T00:00:00Z"
    assert body["endDateTime"] is None


def test_get_devices_returns_parsed_json():
    session = MagicMock()
    session.post.return_value = make_response(200, {"token": "abc123"})
    session.request.return_value = make_response(
        200, {"id": "org-1", "devices": [{"id": "d1", "name": "P0001-S0001-01"}]}
    )

    client = make_client(session)
    result = client.get_devices("org-1")

    assert result["devices"][0]["name"] == "P0001-S0001-01"
    called_url = session.request.call_args.args[1]
    assert "org-1" in called_url


def test_authorized_request_refreshes_token_on_401():
    session = MagicMock()
    session.post.side_effect = [
        make_response(200, {"token": "expired-token"}),
        make_response(200, {"token": "fresh-token"}),
    ]
    session.request.side_effect = [
        make_response(401, text="expired"),
        make_response(200, {"v": {"unit": "bar", "value": "9"}, "dt": "now"}),
    ]

    client = make_client(session)
    result = client.get_realtime("device-1", "tag-1")

    assert result["v"]["value"] == "9"
    assert session.post.call_count == 2
    assert session.request.call_count == 2
