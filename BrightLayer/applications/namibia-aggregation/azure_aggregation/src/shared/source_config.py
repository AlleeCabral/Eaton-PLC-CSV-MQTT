from __future__ import annotations

from typing import Any, Dict, List, Tuple


def request_pairs_from_kpi_map(kpi_map: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build unique Brightlayer request pairs from the canonical KPI source map."""
    pairs: List[Dict[str, str]] = []
    seen: set[Tuple[str, str]] = set()
    for kpi in kpi_map.get("kpis", []):
        for source in kpi.get("sources", []):
            device_id = str(source.get("deviceId") or "").strip()
            trait_id = str(source.get("traitId") or "").strip()
            if not device_id or not trait_id:
                raise ValueError("Every KPI source requires deviceId and traitId")
            key = (device_id, trait_id)
            if key in seen:
                continue
            seen.add(key)
            pairs.append({"deviceId": device_id, "tagTrait": trait_id})
    if not pairs:
        raise ValueError("aggregation-kpi-map must define at least one KPI source")
    return pairs