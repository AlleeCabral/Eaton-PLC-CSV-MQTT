from src.shared.aggregations import aggregate_kpis

KPI_MAP = {
    "kpis": [
        {
            "name": "total_flow",
            "operation": "sum",
            "sources": [
                {"deviceId": "device-1", "traitId": "flow"},
                {"deviceId": "device-2", "traitId": "flow"},
            ],
            "unit": "m3/h",
            "precision": 2,
        },
        {
            "name": "avg_pressure",
            "operation": "avg",
            "sources": [{"deviceId": "device-1", "traitId": "pressure"}],
            "unit": "bar",
            "precision": 1,
        },
    ]
}


def test_aggregate_kpis_sums_across_multiple_devices():
    rows = [
        {"deviceId": "device-1", "traitId": "flow", "value": "10.111"},
        {"deviceId": "device-2", "traitId": "flow", "value": "5.222"},
    ]
    results = aggregate_kpis(rows, KPI_MAP)
    assert results["total_flow"]["value"] == 15.33
    assert results["total_flow"]["sourceCount"] == 2
    assert results["total_flow"]["status"] == "ok"


def test_aggregate_kpis_computes_avg_with_precision():
    rows = [{"deviceId": "device-1", "traitId": "pressure", "value": "2.06"}]
    results = aggregate_kpis(rows, KPI_MAP)
    assert results["avg_pressure"]["value"] == 2.1


def test_aggregate_kpis_skips_none_values_not_zero_filled():
    rows = [
        {"deviceId": "device-1", "traitId": "flow", "value": None},
        {"deviceId": "device-2", "traitId": "flow", "value": "5.0"},
    ]
    results = aggregate_kpis(rows, KPI_MAP)
    assert results["total_flow"]["value"] == 5.0
    assert results["total_flow"]["sourceCount"] == 1


def test_aggregate_kpis_reports_no_data_when_no_matching_rows():
    results = aggregate_kpis([], KPI_MAP)
    assert results["total_flow"]["status"] == "no_data"
    assert results["total_flow"]["value"] is None
    assert results["total_flow"]["sourceCount"] == 0
    assert results["total_flow"]["expectedSourceCount"] == 2


def test_aggregate_kpis_ignores_unparseable_values():
    rows = [
        {"deviceId": "device-1", "traitId": "flow", "value": "not-a-number"},
        {"deviceId": "device-2", "traitId": "flow", "value": "5.0"},
    ]
    results = aggregate_kpis(rows, KPI_MAP)
    assert results["total_flow"]["value"] == 5.0
    assert results["total_flow"]["sourceCount"] == 1


def test_aggregate_kpis_reports_quality_and_carry_forward_counts():
    rows = [
        {
            "deviceId": "device-1",
            "traitId": "flow",
            "value": "10",
            "quality": "online",
            "carriedForward": False,
        },
        {
            "deviceId": "device-2",
            "traitId": "flow",
            "value": "5",
            "quality": "stale",
            "carriedForward": True,
        },
    ]

    result = aggregate_kpis(rows, KPI_MAP)["total_flow"]

    assert result["expectedSourceCount"] == 2
    assert result["freshSourceCount"] == 1
    assert result["staleSourceCount"] == 1
    assert result["offlineSourceCount"] == 0
    assert result["carriedSourceCount"] == 1
