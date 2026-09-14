from __future__ import annotations

from datetime import datetime, timedelta, timezone


def floor_to_interval(ts_utc: datetime, interval_minutes: int) -> datetime:
    """Round a UTC timestamp down to a configured minute boundary."""
    if interval_minutes <= 0 or 60 % interval_minutes != 0:
        raise ValueError("interval_minutes must be a positive divisor of 60")
    normalized = ts_utc.astimezone(timezone.utc)
    minute = (normalized.minute // interval_minutes) * interval_minutes
    return normalized.replace(minute=minute, second=0, microsecond=0)


def floor_to_5_minutes(ts_utc: datetime) -> datetime:
    """Round a UTC timestamp down to the nearest 5-minute boundary."""
    return floor_to_interval(ts_utc, 5)


def completed_cycle_bounds(now_utc: datetime, interval_minutes: int):
    """Return the start and end of the most recently completed interval."""
    cycle_end = floor_to_interval(now_utc, interval_minutes)
    cycle_start = cycle_end - timedelta(minutes=interval_minutes)
    return cycle_start, cycle_end


def cycle_bounds(now_utc: datetime, grace_seconds: int):
    """Return cycle start, end, and grace deadline timestamps."""
    cycle_start = floor_to_5_minutes(now_utc.astimezone(timezone.utc))
    cycle_end = cycle_start + timedelta(minutes=5)
    grace_deadline = cycle_end + timedelta(seconds=grace_seconds)
    return cycle_start, cycle_end, grace_deadline


def cycle_key(dt_utc: datetime) -> str:
    """Return the cycle key in the required ISO format."""
    floored = floor_to_5_minutes(dt_utc.astimezone(timezone.utc))
    return floored.strftime("%Y-%m-%dT%H:%M:00Z")


def determine_cycle_status(
    expected_count: int,
    received_count: int,
    now_utc: datetime,
    grace_deadline: datetime,
) -> str:
    """Decide whether a cycle is ready, expired, or still open for more data.

    Only covers the planner's own responsibility. 'processing'/'sent'/'failed'
    are set later by the aggregation and writeback iterations, not here.
    """
    if received_count >= expected_count:
        return "ready"
    if now_utc >= grace_deadline:
        return "expired"
    return "open"
