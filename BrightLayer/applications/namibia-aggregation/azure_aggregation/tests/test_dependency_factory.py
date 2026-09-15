import json
import os
from unittest.mock import MagicMock

from src.shared.dependency_factory import build_runtime_context, build_storage_repo, load_secrets

CONFIG = {
    "KEYVAULT_URI": "https://kv-namibia-agg-dev-001.vault.azure.net/",
    "MAX_RETRIES": 3,
    "RETRY_BASE_SECONDS": 10,
    "CYCLE_TABLE_STATUS": "CycleStatus",
    "CYCLE_TABLE_SNAPSHOT": "CycleDataSnapshot",
    "CYCLE_TABLE_AUDIT": "CycleAudit",
    "WRITEBACK_MODE": "enabled",
}

SECRET_VALUES = {
    "brightlayer-service-account-id": "sa-id",
    "brightlayer-service-account-secret": "sa-secret",
    "brightlayer-api-prefix": "https://portal.machinery-monitoring.com",
    "brightlayer-aggregate-device-config": json.dumps({"kpiTagMap": {"total_flow": "10462371"}}),
    "brightlayer-writeback-credentials": json.dumps({"connectionString": "HostName=x;DeviceId=y;SharedAccessKey=z"}),
    "aggregation-kpi-map": json.dumps({"kpis": [{"name": "total_flow", "operation": "sum", "sources": [{"deviceId": "device-1", "traitId": "10549349"}], "unit": "m3/h"}]}),
}


def make_fake_secret_client():
    client = MagicMock()

    def get_secret(name):
        secret = MagicMock()
        secret.value = SECRET_VALUES[name]
        return secret

    client.get_secret.side_effect = get_secret
    return client


def test_load_secrets_parses_json_secrets_only():
    client = make_fake_secret_client()
    secrets = load_secrets(client)

    assert secrets["brightlayer-service-account-id"] == "sa-id"
    assert isinstance(secrets["aggregation-kpi-map"], dict)


def test_build_runtime_context_assembles_all_dependencies(monkeypatch):
    monkeypatch.setenv("AzureWebJobsStorage", "UseDevelopmentStorage=true")

    secret_client = make_fake_secret_client()
    fake_table_service_client = MagicMock()
    captured_connection_strings = []

    def factory_builder(connection_string):
        captured_connection_strings.append(connection_string)
        return MagicMock(name="iot_client_factory")

    context = build_runtime_context(
        CONFIG,
        secret_client=secret_client,
        table_service_client=fake_table_service_client,
        iot_client_factory_builder=factory_builder,
    )

    assert context["brightlayer_client"].api_prefix == "https://portal.machinery-monitoring.com"
    assert context["devices"][0]["deviceId"] == "device-1"
    assert captured_connection_strings == ["HostName=x;DeviceId=y;SharedAccessKey=z"]
    fake_table_service_client.create_table_if_not_exists.assert_called()
    assert context["writeback"].kpi_tag_map == {"total_flow": "10462371"}


def test_build_storage_repo_does_not_load_key_vault_secrets():
    fake_table_service_client = MagicMock()

    repo = build_storage_repo(CONFIG, fake_table_service_client)

    assert repo.table_service_client is fake_table_service_client
    fake_table_service_client.create_table_if_not_exists.assert_called()


def test_dry_run_context_does_not_read_writeback_secrets_or_build_iot_client(monkeypatch):
    monkeypatch.setenv("AzureWebJobsStorage", "UseDevelopmentStorage=true")
    secret_client = make_fake_secret_client()
    fake_table_service_client = MagicMock()
    factory_builder = MagicMock()

    context = build_runtime_context(
        {**CONFIG, "WRITEBACK_MODE": "dry_run"},
        secret_client=secret_client,
        table_service_client=fake_table_service_client,
        iot_client_factory_builder=factory_builder,
    )

    requested_names = [call.args[0] for call in secret_client.get_secret.call_args_list]
    assert "brightlayer-aggregate-device-config" not in requested_names
    assert "brightlayer-writeback-credentials" not in requested_names
    assert "writeback" not in context
    factory_builder.assert_not_called()
