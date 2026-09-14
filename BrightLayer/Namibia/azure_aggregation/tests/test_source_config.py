import pytest

from src.shared.source_config import request_pairs_from_kpi_map


def test_request_pairs_are_derived_and_deduplicated():
    kpi_map = {
        "kpis": [
            {"sources": [{"deviceId": "d1", "traitId": "today"}]},
            {"sources": [
                {"deviceId": "d1", "traitId": "today"},
                {"deviceId": "d2", "traitId": "today"},
            ]},
        ]
    }

    assert request_pairs_from_kpi_map(kpi_map) == [
        {"deviceId": "d1", "tagTrait": "today"},
        {"deviceId": "d2", "tagTrait": "today"},
    ]


def test_request_pairs_reject_incomplete_source():
    with pytest.raises(ValueError, match="deviceId and traitId"):
        request_pairs_from_kpi_map({"kpis": [{"sources": [{"deviceId": "d1"}]}]})


def test_request_pairs_reject_empty_map():
    with pytest.raises(ValueError, match="at least one"):
        request_pairs_from_kpi_map({"kpis": []})