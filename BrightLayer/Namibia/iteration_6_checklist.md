# Iteration 6 Checklist - End-to-End Cycle Orchestration

## Iteration Goal

Wire Iterations 1-5 together into an actual running pipeline: a timer-driven orchestrator that plans each 5-minute cycle, fetches telemetry, aggregates when ready, and publishes to Brightlayer — replacing the Iteration 0 `function_app.py` stubs that only logged.

## Scope decision: single-timer synchronous pipeline instead of queue fan-out

Iteration 0's skeleton declared queue-triggered stub functions (`fetch-cycle`, `aggregate-cycle`, `writeback-cycle`) implying a fan-out design. This iteration instead adopts a **simpler synchronous pipeline driven entirely by the existing 1-minute timer trigger**: each tick plans the current cycle, fetches telemetry, and — only once the cycle is `ready` — aggregates and writes back, all in one function invocation. The unused queue-triggered stubs are removed as dead code rather than left half-wired and misleading. Revisit a queue-based fan-out design if/when scale requires processing multiple cycles or sites concurrently.

## Scope

- `modules/orchestrator.py`: `plan_cycle()` (create/refresh the CycleStatus row for the current cycle) and `run_cycle_pipeline()` (fetch → conditionally aggregate + writeback → update status).
- `shared/dependency_factory.py`: build real runtime dependencies (Brightlayer client, Table Storage repo, IoT Hub client factory, KPI maps, device list) from config + Key Vault secrets.
- Wire `function_app.py`'s `cycle_planner_timer` to use both of the above, with structured logging via `shared/observability.build_log_envelope` (closes the Iteration 0 gap where the log envelope existed but was never used).
- Out of scope: retry/failure-specific handling beyond what individual clients already do (Iteration 7), cleanup/retention (Iteration 8 — `cleanup_cycles` remains a stub), observability/alerting hardening beyond basic structured logs (Iteration 9), production readiness/rollout (Iteration 10).

## Done Criteria

1. `plan_cycle(now_utc, config, repo)` creates a CycleStatus row on first tick of a cycle and refreshes its status (open/ready/expired) on later ticks, without duplicating rows.
2. `run_cycle_pipeline()` always fetches telemetry for the current cycle; only aggregates and publishes once the cycle status is `ready`; updates status to `processing` → `sent`/`failed` accordingly; is a no-op (aggregation/writeback skipped) for `open`/`expired` cycles.
3. `dependency_factory.build_runtime_context(config)` assembles a `BrightlayerClient`, `StorageCycleRepo`, IoT Hub client factory, and parsed KPI maps/device list from Key Vault secrets + `AzureWebJobsStorage`.
4. `function_app.py`'s timer trigger calls the above and logs via the standard envelope; unused queue-triggered stubs removed.
5. Unit tests cover `plan_cycle` (new + existing cycle), `run_cycle_pipeline` (open/ready/expired paths, failure path), and `dependency_factory` (with mocked Key Vault/Table/IoT clients).

## Task Checklist

- [x] Add `modules/orchestrator.py` with `plan_cycle()` and `run_cycle_pipeline()`.
- [x] Add `shared/dependency_factory.py` with `build_runtime_context(config)`.
- [x] Rewrite `function_app.py`: real `cycle_planner_timer`, removed unused queue-triggered stubs, `cleanup_cycles` left as-is (Iteration 8).
- [x] Add `tests/test_orchestrator.py`.
- [x] Add `tests/test_dependency_factory.py`.

## Gate Checks

- [x] `python -m pytest Namibia/azure_aggregation/tests -q` passes with new tests included.
- [x] `run_cycle_pipeline` never calls aggregate/writeback for a cycle that isn't `ready`.
- [x] A cycle already `sent`/`failed`/`expired` is not silently re-processed on the next tick (guarded in the timer wiring, not just the pipeline function).
- [ ] Live smoke test: deploy and observe one real 5-minute cycle go `open` → `ready` → `sent` in Application Insights / Table Storage. **NOT DONE** — blocked on ALL prior iterations' live gaps (Key Vault secrets, Brightlayer aggregate device, Table Storage RBAC) plus this iteration's own dependency wiring being exercised live for the first time.

## Quick Re-evaluation Rule

- `run_cycle_pipeline` re-fetches telemetry on every tick within an open cycle (idempotent upserts), which is intentional — it lets partial data accumulate across the 5-minute window. Once a cycle reaches `sent`/`failed`/`expired`, the timer wiring must skip calling `run_cycle_pipeline` again for that cycle key (implemented as a guard in `function_app.py`, not in `orchestrator.py` itself, so the pipeline function stays simple and testable in isolation).
- `dependency_factory` is the first place secrets are actually read from Key Vault at runtime — if any `REQUIRED_SECRET_KEYS` are missing, this is where it will fail first, at cycle-planning time rather than deploy time. This is expected and acceptable, but means "deployed" and "working" are still two different claims.

## Gate Report

- Iteration: 6
- Date: 2026-08-22
- Owner: Alexandra Cabral (with GitHub Copilot)
- Scope completed: real orchestrator (plan + pipeline), dependency factory, function_app.py wired to a real, structurally-logged synchronous pipeline; unused queue stubs removed.
- Tests executed: `python -m pytest Namibia/azure_aggregation/tests -q`
- Result: PASS (code + tests); live end-to-end run still blocked on all prior iterations' Key Vault/Brightlayer prerequisites.
- Missing items: live 5-minute cycle observation; all Key Vault secrets from Iterations 1/3/4/5; Table Storage RBAC verification; `Aggregated_Namibia` device/ontology.
- Immediate follow-ups: Iteration 7 (retry/failure handling) can build on `run_cycle_pipeline`'s status transitions; Iteration 8 (cleanup) can now target real CycleStatus/Snapshot rows this iteration produces.
- Checklist changes applied: none yet — first pass.
