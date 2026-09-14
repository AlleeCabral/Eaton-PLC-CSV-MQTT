from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from azure.iot.device import Message


def build_trends_payload(
    aggregates: Dict[str, Dict[str, Any]],
    kpi_tag_map: Dict[str, str],
    now_utc: Optional[datetime] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """Build the Brightlayer 'Trends' MQTT payload from aggregate KPI results.

    Only KPIs with status "ok" are included — a KPI with no source data this cycle
    is omitted rather than sent as a fabricated/zero value (see Iteration 4 policy).
    """
    now_utc = now_utc or datetime.now(timezone.utc)
    epoch_seconds = int(now_utc.timestamp())

    trends: List[Dict[str, Any]] = []
    for name, result in aggregates.items():
        if result.get("status") != "ok":
            continue
        tag_id = kpi_tag_map.get(name)
        if tag_id is None:
            continue
        trends.append({"c": str(tag_id), "t": epoch_seconds, "v": result["value"]})

    return {"trends": trends}


class WritebackToBrightlayer:
    """Publishes aggregate KPI trends to Brightlayer via an Azure IoT Hub D2C message.

    `iot_client_factory` is a zero-arg callable returning an object with connect(),
    send_message(msg), and disconnect() — normally
    `IoTHubDeviceClient.create_from_connection_string(conn_str)`, injected so this
    module doesn't need to know how the connection string is obtained (Key Vault, etc).
    """

    def __init__(
        self,
        iot_client_factory: Callable[[], Any],
        kpi_tag_map: Dict[str, str],
        config: Dict[str, Any],
    ):
        self.iot_client_factory = iot_client_factory
        self.kpi_tag_map = kpi_tag_map
        self.config = config

    def build_payload(self, cycle_key: str, aggregates: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Construct the payload to be sent to the Brightlayer aggregate virtual device."""
        return build_trends_payload(aggregates, self.kpi_tag_map)

    def run(self, cycle_key: str, aggregates: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Publish one Trends message for the cycle's aggregate KPIs over MQTT/IoT Hub."""
        payload = self.build_payload(cycle_key, aggregates)

        if not payload["trends"]:
            return {"cycleKey": cycle_key, "status": "skipped", "reason": "no_ok_kpis", "payload": payload}

        client = self.iot_client_factory()
        client.connect()
        try:
            client.send_message(Message(json.dumps(payload)))
        finally:
            client.disconnect()

        return {
            "cycleKey": cycle_key,
            "status": "sent",
            "pointCount": len(payload["trends"]),
            "publishedAtUtc": datetime.fromtimestamp(int(time.time()), tz=timezone.utc).isoformat(),
        }
