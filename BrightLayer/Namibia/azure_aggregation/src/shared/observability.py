from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict


def build_log_envelope(module: str, cycle_key: str, run_id: str, attempt: int, status: str) -> Dict[str, Any]:
    """Create a standard structured log object for lifecycle events."""
    return {
        "component": module,
        "cycleKey": cycle_key,
        "runId": run_id,
        "attempt": attempt,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def log_cycle_alert(module: str, cycle_key: str, run_id: str, status: str, detail: str) -> None:
    """Log a cycle failure as a distinct, alert-filterable ERROR-level event."""
    envelope = build_log_envelope(module, cycle_key, run_id, 1, status)
    envelope["alert"] = True
    envelope["detail"] = detail
    logging.error("cycle_alert: %s", detail, extra=envelope)
