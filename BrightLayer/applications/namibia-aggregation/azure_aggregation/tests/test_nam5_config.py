import json
from pathlib import Path

from src.shared.source_config import request_pairs_from_kpi_map


def test_namibia_characterization_map_contains_twelve_kpis_for_three_devices():
    path = Path(__file__).parents[1] / "config" / "nam5-single-device-kpi-map.json"
    kpi_map = json.loads(path.read_text(encoding="utf-8"))

    pairs = request_pairs_from_kpi_map(kpi_map)

    assert len(kpi_map["kpis"]) == 12
    assert len(pairs) == 36
    assert {pair["deviceId"] for pair in pairs} == {
        "8a7f416d-a452-2b11-0800-1e0d06362200",
        "c627a6ba-a832-2b11-0800-4ea999779100",
        "f8a20915-6672-2b11-0800-2f5623d56800",
    }
    assert {kpi["name"] for kpi in kpi_map["kpis"]} >= {
        "production_today",
        "solar_today",
        "grid_today",
        "co2_today",
    }