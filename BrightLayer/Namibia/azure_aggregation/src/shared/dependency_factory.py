from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, Optional

from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential
from azure.iot.device import IoTHubDeviceClient
from azure.keyvault.secrets import SecretClient

try:
    from src.modules.aggregate_cycle import AggregateCycle
    from src.modules.fetch_source_telemetry import FetchSourceTelemetry
    from src.modules.writeback_to_brightlayer import WritebackToBrightlayer
    from src.shared.brightlayer_client import BrightlayerClient
    from src.shared.config import READ_SECRET_KEYS, REQUIRED_SECRET_KEYS, WRITEBACK_SECRET_KEYS
    from src.shared.source_config import request_pairs_from_kpi_map
    from src.shared.storage_cycle_repo import StorageCycleRepo
except ModuleNotFoundError:
    from modules.aggregate_cycle import AggregateCycle
    from modules.fetch_source_telemetry import FetchSourceTelemetry
    from modules.writeback_to_brightlayer import WritebackToBrightlayer
    from shared.brightlayer_client import BrightlayerClient
    from shared.config import READ_SECRET_KEYS, REQUIRED_SECRET_KEYS, WRITEBACK_SECRET_KEYS
    from shared.source_config import request_pairs_from_kpi_map
    from shared.storage_cycle_repo import StorageCycleRepo

# Secrets whose value is JSON and must be parsed rather than used as a raw string.
_JSON_SECRETS = {name for name, kind in REQUIRED_SECRET_KEYS.items() if kind == "json"}


def load_secrets(
    secret_client: Any,
    secret_keys: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Fetch and parse only the explicitly required Key Vault secrets."""
    secret_keys = secret_keys or REQUIRED_SECRET_KEYS
    secrets: Dict[str, Any] = {}
    for name in secret_keys:
        value = secret_client.get_secret(name).value
        secrets[name] = json.loads(value) if name in _JSON_SECRETS else value
    return secrets


def build_storage_repo(
    config: Dict[str, Any],
    table_service_client: Optional[Any] = None,
) -> StorageCycleRepo:
    """Build the storage-only repository used by scheduler and cleanup functions."""
    table_service_client = table_service_client or TableServiceClient.from_connection_string(
        os.environ["AzureWebJobsStorage"]
    )
    repo = StorageCycleRepo(table_service_client, config)
    repo.ensure_tables()
    return repo


def build_runtime_context(
    config: Dict[str, Any],
    secret_client: Optional[Any] = None,
    table_service_client: Optional[Any] = None,
    iot_client_factory_builder: Optional[Callable[[str], Callable[[], Any]]] = None,
) -> Dict[str, Any]:
    """Assemble the real dependencies needed to run one cycle: Brightlayer client,
    Table Storage repo, source device list, KPI maps, and an IoT Hub client factory.

    Optional client params allow tests to inject fakes without touching Azure.
    """
    secret_client = secret_client or SecretClient(
        vault_url=config["KEYVAULT_URI"], credential=DefaultAzureCredential()
    )
    secret_keys = dict(READ_SECRET_KEYS)
    if config["WRITEBACK_MODE"] == "enabled":
        secret_keys.update(WRITEBACK_SECRET_KEYS)
    secrets = load_secrets(secret_client, secret_keys)

    brightlayer_client = BrightlayerClient(
        api_prefix=secrets["brightlayer-api-prefix"],
        service_account_id=secrets["brightlayer-service-account-id"],
        service_account_secret=secrets["brightlayer-service-account-secret"],
        max_retries=config["MAX_RETRIES"],
        retry_base_seconds=config["RETRY_BASE_SECONDS"],
    )

    repo = build_storage_repo(config, table_service_client)

    kpi_map = secrets["aggregation-kpi-map"]
    devices = request_pairs_from_kpi_map(kpi_map)
    context = {
        "brightlayer_client": brightlayer_client,
        "repo": repo,
        "devices": devices,
        "fetch_source_telemetry": FetchSourceTelemetry(brightlayer_client, repo, config),
        "aggregate_cycle": AggregateCycle(repo, kpi_map, config),
    }
    if config["WRITEBACK_MODE"] == "enabled":
        kpi_tag_map = secrets["brightlayer-aggregate-device-config"]["kpiTagMap"]
        writeback_connection_string = secrets["brightlayer-writeback-credentials"]["connectionString"]
        if iot_client_factory_builder is None:
            def iot_client_factory_builder(connection_string: str) -> Callable[[], Any]:
                return lambda: IoTHubDeviceClient.create_from_connection_string(connection_string)
        context["writeback"] = WritebackToBrightlayer(
            iot_client_factory_builder(writeback_connection_string), kpi_tag_map, config
        )
    return context
