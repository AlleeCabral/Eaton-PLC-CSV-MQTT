from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.modules import cleanup_cycles

CONFIG = {"RETENTION_HOURS": 48}


def test_run_computes_cutoff_and_delegates_to_repo():
    repo = MagicMock()
    repo.delete_old_cycles.return_value = {"CycleStatus": 3, "CycleDataSnapshot": 12}

    now = datetime(2025, 6, 3, 0, 0, 0, tzinfo=timezone.utc)
    result = cleanup_cycles.run(now, CONFIG, repo)

    repo.delete_old_cycles.assert_called_once_with("2025-06-01T00:00:00Z")
    assert result["deletedCounts"] == {"CycleStatus": 3, "CycleDataSnapshot": 12}
