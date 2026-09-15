from __future__ import annotations

from typing import Any, Dict, Iterable, List


def sum_values(values: Iterable[float]) -> float:
    """Calculate the sum of a numeric sequence."""
    return float(sum(values))


def avg_values(values: Iterable[float]) -> float:
    """Calculate the mean of a numeric sequence."""
    values = list(values)
    if not values:
        raise ValueError("Cannot calculate average of empty sequence.")
    return float(sum(values) / len(values))


def min_values(values: Iterable[float]) -> float:
    """Calculate the minimum value of a numeric sequence."""
    values = list(values)
    if not values:
        raise ValueError("Cannot calculate minimum of empty sequence.")
    return float(min(values))


def max_values(values: Iterable[float]) -> float:
    """Calculate the maximum value of a numeric sequence."""
    values = list(values)
    if not values:
        raise ValueError("Cannot calculate maximum of empty sequence.")
    return float(max(values))


def apply_precision(value: float, precision: int = 3) -> float:
    """Round a numeric value to the configured precision."""
    return round(float(value), precision)


_OPERATIONS = {
    "sum": sum_values,
    "avg": avg_values,
    "min": min_values,
    "max": max_values,
}


def aggregate_kpis(snapshot_rows: Iterable[Dict[str, Any]], kpi_map: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Compute one aggregate value per configured KPI from a cycle's snapshot rows.

    Aggregates whatever value is present regardless of `quality` (online/stale/offline) —
    Iteration 3's normalizer already carries forward the last known value and never
    zero-fills, so this naturally implements the permissive/carry-forward policy.
    Rows with a missing (None) value are skipped rather than treated as zero.
    """
    rows_by_key: Dict[str, List[Dict[str, Any]]] = {}
    for row in snapshot_rows:
        key = f"{row.get('deviceId')}_{row.get('traitId')}"
        rows_by_key.setdefault(key, []).append(row)

    results: Dict[str, Dict[str, Any]] = {}
    for kpi in kpi_map.get("kpis", []):
        name = kpi["name"]
        operation = _OPERATIONS[kpi["operation"]]
        precision = kpi.get("precision", 3)
        source_values: List[float] = []
        selected_rows: List[Dict[str, Any]] = []
        for source in kpi.get("sources", []):
            key = f"{source.get('deviceId')}_{source.get('traitId')}"
            for row in rows_by_key.get(key, []):
                if row.get("value") is None:
                    continue
                try:
                    source_values.append(float(row["value"]))
                    selected_rows.append(row)
                except (TypeError, ValueError):
                    continue

        quality_counts = {
            "expectedSourceCount": len(kpi.get("sources", [])),
            "sourceCount": len(source_values),
            "freshSourceCount": sum(1 for row in selected_rows if row.get("quality") == "online"),
            "staleSourceCount": sum(1 for row in selected_rows if row.get("quality") == "stale"),
            "offlineSourceCount": sum(1 for row in selected_rows if row.get("quality") == "offline"),
            "carriedSourceCount": sum(1 for row in selected_rows if row.get("carriedForward") is True),
        }

        if not source_values:
            results[name] = {"value": None, "unit": kpi.get("unit"), "status": "no_data", **quality_counts}
            continue

        results[name] = {
            "value": apply_precision(operation(source_values), precision),
            "unit": kpi.get("unit"),
            "status": "ok",
            **quality_counts,
        }
    return results
