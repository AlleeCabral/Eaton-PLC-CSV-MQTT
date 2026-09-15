import logging

from src.shared.observability import build_log_envelope


def test_log_envelope_uses_non_reserved_component_field(caplog):
    envelope = build_log_envelope("cycle_planner", "cycle-1", "run-1", 1, "error")

    with caplog.at_level(logging.ERROR):
        logging.error("cycle failed", extra=envelope)

    record = caplog.records[-1]
    assert record.component == "cycle_planner"
    assert record.cycleKey == "cycle-1"