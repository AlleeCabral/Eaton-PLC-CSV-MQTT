# Iteration 4 Checklist - Aggregation Engine

## Iteration Goal

Compute per-cycle KPI values from the snapshot rows written by Iteration 3, using the arithmetic primitives already implemented in Iteration 0 (`sum_values`, `avg_values`, `min_values`, `max_values`, `apply_precision`), driven by a KPI map contract analogous to the `aggregation-kpi-map` Key Vault secret.

## Scope

- Add a way to read back all snapshot rows for a cycle (`StorageCycleRepo.list_snapshots`) — this was missing from Iteration 2, which only wrote rows.
- Add `aggregate_kpis(snapshot_rows, kpi_map)` combining rows into KPI values per the configured operation and precision.
- Wire `modules/aggregate_cycle.py` `AggregateCycle.run(cycle_key)` to read snapshots, aggregate, and return results (ready for Iteration 5 writeback).
- Out of scope: writeback to Brightlayer (Iteration 5), full timer/queue orchestration (Iteration 6), optimistic locking / concurrent-run protection (Iteration 7), reading the real `aggregation-kpi-map` secret from Key Vault (Iteration 6 wiring).

## Done Criteria

1. `StorageCycleRepo.list_snapshots(cycle_key)` returns all snapshot rows for a cycle via a PartitionKey query.
2. `aggregate_kpis()` groups snapshot rows by KPI (via explicit `{deviceId, traitId}` source lists in the KPI map), applies the configured operation (sum/avg/min/max), and rounds to the configured precision.
3. Aggregation is consistent with the "permissive mode + carry-forward" operational rule: it aggregates whatever value is present in the snapshot row regardless of `quality` (online/stale/offline) — since Iteration 3 already carries forward the last known value and never zero-fills, the aggregation engine doesn't need its own stale-handling branch; it naturally reflects carried-forward values, and only skips rows with a genuinely missing (`None`) value.
4. `AggregateCycle.run(cycle_key)` produces a structured result per KPI, including how many source rows contributed (useful for later partial-data auditing).
5. Unit tests cover: multi-device sum, single-device avg, precision rounding, missing source row handling, and the end-to-end `run()` flow with a mocked repo.

## Task Checklist

- [x] Add `StorageCycleRepo.list_snapshots(cycle_key)` using `query_entities` filtered by `PartitionKey`.
- [x] Add `aggregate_kpis(snapshot_rows, kpi_map)` to `shared/aggregations.py`.
- [x] Rewrite `modules/aggregate_cycle.py` `AggregateCycle` to take `(repo, kpi_map, config)` and implement `run(cycle_key)` for real.
- [x] Add `tests/test_aggregations.py` for `aggregate_kpis` (sum/avg, precision, missing source rows).
- [x] Add `tests/test_aggregate_cycle.py` for the end-to-end `run()` flow with a mocked repo.

## Gate Checks

- [x] `python -m pytest Namibia/azure_aggregation/tests -q` passes with new tests included.
- [x] Aggregation never crashes on a missing/None source value — it's excluded from the operation, not treated as zero.
- [ ] Live smoke test using real snapshot rows written by a live Iteration 3 run and a real `aggregation-kpi-map` secret. **NOT DONE** — blocked on Key Vault secret population and on Iteration 3's own live pending item (real Brightlayer source data).

## Quick Re-evaluation Rule

- The KPI map shape used here (`{"name", "operation", "sources": [{"deviceId","traitId"}], "unit", "precision"}`) is an adaptation of the blueprint's conceptual example (which used `sourceField` names) to match how snapshot rows are actually keyed (`deviceId_traitId`). This should be treated as the working contract for `aggregation-kpi-map` going forward unless the real Brightlayer aggregate device ontology requires a different shape once it's defined.
- `AggregateCycle.run()` does not yet set `CycleStatus` to `processing`/`sent`/`failed` — that state-machine wiring belongs to Iteration 6 (orchestration), which will call this after `determine_cycle_status` (Iteration 2) reports `ready`.

## Gate Report

- Iteration: 4
- Date: 2026-08-22
- Owner: Alexandra Cabral (with GitHub Copilot)
- Scope completed: snapshot read-back (`list_snapshots`), KPI aggregation engine (`aggregate_kpis`), real `AggregateCycle.run()`.
- Tests executed: `python -m pytest Namibia/azure_aggregation/tests -q`
- Result: PASS (code + tests); live verification pending (see gate checks).
- Missing items: live smoke test (needs real snapshot data + real KPI map secret); KPI map shape not yet confirmed against a real Brightlayer aggregate device ontology.
- Immediate follow-ups: Iteration 5 (writeback adapter) can now consume `AggregateCycle.run()` output.
- Checklist changes applied: none yet — first pass.
