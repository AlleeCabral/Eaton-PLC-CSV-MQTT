# Iteration 2 Checklist - Cycle Planner and State Persistence

## Iteration Goal

Make cycle state real: persist cycle status and snapshot rows to Azure Table Storage, and add the logic that decides a cycle's status (open/ready/expired) based on expected vs. received PLC counts and the grace deadline. Time-boundary helpers (`floor_to_5_minutes`, `cycle_bounds`, `cycle_key`) were already implemented ahead of schedule in Iteration 0 and are reused here unchanged.

## Scope

- Real Azure Table Storage integration in `shared/storage_cycle_repo.py` (using `azure-data-tables`, already in requirements.txt).
- Cycle status decision logic in `modules/cycle_planner.py`.
- Out of scope: full orchestration wiring into `function_app.py` timer/queue triggers (Iteration 6), retry/failure handling beyond basic status transitions (Iteration 7), telemetry snapshot writers being called from a real fetch flow (Iteration 3).

## Done Criteria

1. `StorageCycleRepo.ensure_tables()` actually creates the three tables (idempotent) via `TableServiceClient`.
2. `StorageCycleRepo.upsert_status()` / `get_status()` read and write real entities keyed by `PartitionKey=cycleStartUtc`, `RowKey="aggregate"`.
3. `StorageCycleRepo.upsert_snapshot()` writes entities keyed by `PartitionKey=cycleStartUtc`, `RowKey=sourceDeviceId+traitId`.
4. `determine_cycle_status()` implements the `open` → `ready` / `expired` transition per the blueprint's CycleStatus schema.
5. Unit tests cover all of the above without a real Azure Storage account (mocked `TableServiceClient`/`TableClient`).

## Task Checklist

- [x] Replace `shared/storage_cycle_repo.py` stub with real `StorageCycleRepo` backed by `azure.data.tables.TableServiceClient`.
- [x] `ensure_tables()` calls `create_table_if_not_exists` for `CycleStatus`, `CycleDataSnapshot`, `CycleAudit` table names (sourced from config).
- [x] `upsert_status(entity)` — merges/replaces a status row; requires `PartitionKey` + `RowKey` in the entity.
- [x] `get_status(cycle_start_key)` — reads back the aggregate status row for a cycle, returns `None` if not found.
- [x] `upsert_snapshot(entity)` — writes a snapshot row.
- [x] Add `determine_cycle_status(expected_count, received_count, now_utc, grace_deadline)` to `modules/cycle_planner.py` implementing: `ready` if `received_count >= expected_count`; `expired` if `now_utc >= grace_deadline` and not ready; otherwise `open`.
- [x] Add `tests/test_storage_cycle_repo.py` with a fake in-memory table client (no real Azure Storage account/connection needed).
- [x] Add tests for `determine_cycle_status` covering all three transitions.

## Gate Checks

- [x] `python -m pytest Namibia/azure_aggregation/tests -q` passes with new tests included.
- [x] No real Azure Storage account/connection required to run tests (fully mocked).
- [ ] Live smoke test against the real `AzureWebJobsStorage` / `DEPLOYMENT_STORAGE_CONNECTION_STRING` account to confirm `ensure_tables()` actually creates tables in the deployed environment. **NOT DONE** — deferred until Iteration 6 orchestration wiring, when the Function App will actually invoke this repo at runtime.

## Quick Re-evaluation Rule

- `determine_cycle_status` intentionally does NOT cover `processing`, `sent`, or `failed` states — those are set by the aggregation/writeback iterations (4 and 5) after they act on a `ready` cycle, and by retry handling (Iteration 7) on failure. Scope was narrowed to just the planner's own responsibility (deciding readiness), not the full state machine.
- Table Storage retry behavior currently relies on the SDK's own defaults, not `shared/retry_policy.py`. Revisit in Iteration 7 if transient failures need explicit backoff beyond what the SDK provides.

## Gate Report

- Iteration: 2
- Date: 2026-08-22
- Owner: Alexandra Cabral (with GitHub Copilot)
- Scope completed: real Table Storage-backed `StorageCycleRepo`, `determine_cycle_status` cycle readiness logic, full unit test coverage with mocked table clients.
- Tests executed: `python -m pytest Namibia/azure_aggregation/tests -q`
- Result: PASS (code + tests); live Table Storage verification pending (see gate checks).
- Missing items: live smoke test against deployed storage account; `processing`/`sent`/`failed` states deferred to later iterations by design.
- Immediate follow-ups: Iteration 3 (fetch source telemetry) can now be implemented using `BrightlayerClient` (Iteration 1) + `StorageCycleRepo.upsert_snapshot` (Iteration 2).
- Checklist changes applied: none yet — first pass.
