import os
from typing import Any, Dict

REQUIRED_ENV_KEYS = {
    "EXPECTED_PLC_COUNT": "int",
    "CYCLE_INTERVAL_MINUTES": "int",
    "CYCLE_SCHEDULE": "str",
    "CYCLE_QUEUE_NAME": "str",
    "CYCLE_GRACE_SECONDS": "int",
    "FETCH_OVERLAP_MINUTES": "int",
    "AGGREGATION_MODE": "str",
    "WRITEBACK_MODE": "str",
    "LAST_KNOWN_VALUE_POLICY": "str",
    "ZERO_FILL_DISABLED": "bool",
    "PLC_STALE_TIMEOUT_SECONDS": "int",
    "PLC_OFFLINE_TIMEOUT_SECONDS": "int",
    "MAX_RETRIES": "int",
    "RETRY_BASE_SECONDS": "int",
    "CYCLE_TABLE_STATUS": "str",
    "CYCLE_TABLE_SNAPSHOT": "str",
    "CYCLE_TABLE_AUDIT": "str",
    "CYCLE_TABLE_LATEST": "str",
    "RETENTION_HOURS": "int",
    "KEYVAULT_URI": "str",
}

REQUIRED_SECRET_KEYS = {
    "brightlayer-service-account-id": "str",
    "brightlayer-service-account-secret": "str",
    "brightlayer-api-prefix": "str",
    "brightlayer-aggregate-device-config": "json",
    "brightlayer-writeback-credentials": "json",
    "aggregation-kpi-map": "json",
}

READ_SECRET_KEYS = {
    "brightlayer-service-account-id": "str",
    "brightlayer-service-account-secret": "str",
    "brightlayer-api-prefix": "str",
    "aggregation-kpi-map": "json",
}

WRITEBACK_SECRET_KEYS = {
    "brightlayer-aggregate-device-config": "json",
    "brightlayer-writeback-credentials": "json",
}


def parse_int(value: Any, name: str) -> int:
    """Safely parse an integer environment value."""
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Configuration value '{name}' must be an integer.") from exc


def parse_bool(value: Any, name: str) -> bool:
    """Safely parse a boolean environment value."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return True
        if normalized in {"false", "0", "no", "n", "off"}:
            return False
    raise ValueError(f"Configuration value '{name}' must be a boolean.")


def validate_required_env() -> Dict[str, Any]:
    """Validate all required environment config keys are present."""
    missing = [key for key in REQUIRED_ENV_KEYS if not os.getenv(key)]
    if missing:
        raise ValueError(f"Missing required environment settings: {', '.join(sorted(missing))}")

    config: Dict[str, Any] = {}
    for key, expected_type in REQUIRED_ENV_KEYS.items():
        value = os.getenv(key)
        if expected_type == "int":
            config[key] = parse_int(value, key)
        elif expected_type == "bool":
            config[key] = parse_bool(value, key)
        else:
            config[key] = value
    if 60 % config["CYCLE_INTERVAL_MINUTES"] != 0:
        raise ValueError("CYCLE_INTERVAL_MINUTES must be a positive divisor of 60.")
    if config["FETCH_OVERLAP_MINUTES"] < config["CYCLE_INTERVAL_MINUTES"]:
        raise ValueError("FETCH_OVERLAP_MINUTES must cover at least one cycle interval.")
    if config["WRITEBACK_MODE"] not in {"dry_run", "enabled"}:
        raise ValueError("WRITEBACK_MODE must be 'dry_run' or 'enabled'.")
    return config


def get_required_secret_names() -> list[str]:
    """Return the required secret names for Key Vault configuration."""
    return list(REQUIRED_SECRET_KEYS.keys())
