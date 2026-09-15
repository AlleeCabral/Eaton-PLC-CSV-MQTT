from datetime import datetime, timezone

import pytest

from src.modules.cycle_planner import (
    completed_cycle_bounds,
    cycle_bounds,
    cycle_key,
    floor_to_5_minutes,
    floor_to_interval,
)


def test_floor_to_5_minutes_rounds_down():
    ts = datetime(2025, 6, 1, 10, 17, 42, 500000, tzinfo=timezone.utc)
    result = floor_to_5_minutes(ts)
    assert result == datetime(2025, 6, 1, 10, 15, 0, 0, tzinfo=timezone.utc)


def test_cycle_bounds_include_grace_deadline():
    ts = datetime(2025, 6, 1, 10, 17, 42, 500000, tzinfo=timezone.utc)
    start, end, grace = cycle_bounds(ts, grace_seconds=90)
    assert start == datetime(2025, 6, 1, 10, 15, 0, 0, tzinfo=timezone.utc)
    assert end == datetime(2025, 6, 1, 10, 20, 0, 0, tzinfo=timezone.utc)
    assert grace == datetime(2025, 6, 1, 10, 21, 30, 0, tzinfo=timezone.utc)


def test_cycle_key_uses_utc_iso_format():
    ts = datetime(2025, 6, 1, 10, 17, 42, 500000, tzinfo=timezone.utc)
    assert cycle_key(ts) == "2025-06-01T10:15:00Z"


def test_completed_cycle_bounds_returns_previous_full_interval():
    now = datetime(2025, 6, 1, 10, 17, 42, tzinfo=timezone.utc)

    start, end = completed_cycle_bounds(now, interval_minutes=5)

    assert start == datetime(2025, 6, 1, 10, 10, tzinfo=timezone.utc)
    assert end == datetime(2025, 6, 1, 10, 15, tzinfo=timezone.utc)


def test_completed_cycle_bounds_at_boundary_does_not_schedule_current_interval():
    now = datetime(2025, 6, 1, 10, 15, tzinfo=timezone.utc)

    start, end = completed_cycle_bounds(now, interval_minutes=5)

    assert start == datetime(2025, 6, 1, 10, 10, tzinfo=timezone.utc)
    assert end == now


def test_floor_to_interval_rejects_invalid_interval():
    with pytest.raises(ValueError, match="positive divisor of 60"):
        floor_to_interval(datetime.now(timezone.utc), interval_minutes=7)
