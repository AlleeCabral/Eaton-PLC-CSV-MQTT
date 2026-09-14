# Iteration 7 Checklist - Retry and Failure Handling

## Iteration Goal

Make cycle failures (aggregation or writeback exceptions) recoverable instead of just logged-and-dropped: track a retry count and last error on the CycleStatus row, retry on the next timer tick while a cycle is still within its grace window, and only mark a cycle `failed` once `MAX_RETRIES` is exhausted.

## Scope

- `run_cycle_pipeline()` catches exceptions from `aggregate_cycle.run()` / `writeback.run()` (previously these propagated uncaught, per Iteration 6's `test_run_cycle_pipeline_propagates_writeback_failure`, which is superseded here).
- On failure: read current `retryCount` from the CycleStatus row, increment it, and set status to `open` (eligible for retry on the next tick, since fetch/aggregate/writeback will simply run again) if under `MAX_RETRIES`, or `failed` (terminal) once the limit is reached. `lastError` is recorded either way.
- On success: `retryCount` and `lastError` are cleared.
- Out of scope: optimistic locking / concurrent-invocation protection (would require a distributed lock — noted as a risk, not implemented, since Azure Functions timer triggers don't overlap by default at the plan's current concurrency settings); cleanup/retention of old failed cycles (Iteration 8); alerting on repeated failures (Iteration 9).

## Done Criteria

1. A transient aggregate/writeback failure does not crash the function invocation — it's caught, recorded, and the cycle stays `open` for retry (as long as `retryCount < MAX_RETRIES`).
2. Once `retryCount >= MAX_RETRIES`, the cycle is marked `failed` (terminal) and will not be retried again (guarded by `plan_cycle`'s existing terminal-status check from Iteration 6).
3. A successful run after prior failures clears `retryCount` and `lastError`.
4. Unit tests cover: first failure (stays open, retryCount=1), repeated failures reaching the limit (becomes failed), and success clearing prior retry state.

## Task Checklist

- [x] Change `run_cycle_pipeline()` signature to accept `config` (needed to read `MAX_RETRIES`).
- [x] Wrap the aggregate+writeback block in try/except; on exception, upsert `{status, retryCount, lastError}` and return without raising.
- [x] On success, upsert `{status: "sent", retryCount: 0, lastError: ""}`.
- [x] Update `function_app.py`'s call to `run_cycle_pipeline` to pass `config`.
- [x] Replace the superseded Iteration 6 test (`test_run_cycle_pipeline_propagates_writeback_failure`) with tests for the new retry/failure behavior.

## Gate Checks

- [x] `python -m pytest Namibia/azure_aggregation/tests -q` passes with updated/new tests.
- [x] A cycle that fails once but succeeds on a later tick ends up `sent` with `retryCount` reset to 0, not stuck showing a stale error.
- [ ] Live smoke test: simulate a real transient Brightlayer/IoT Hub outage and confirm a cycle actually recovers on a later tick within its grace window. **NOT DONE** — blocked on all prior live-test gaps; also requires actually running the timer trigger multiple times against a real (or deliberately flaky) backend, which isn't practical without a deployed environment.

## Quick Re-evaluation Rule

- Optimistic locking (the blueprint's `lockOwner`/`lockExpiresUtc` fields) is explicitly NOT implemented this iteration. Risk: if a single invocation runs longer than the 1-minute timer interval, two overlapping invocations could process the same cycle concurrently. Flex Consumption's default behavior and typical invocation duration for this workload make this unlikely in practice, but it should be revisited if cycles start taking close to a minute to process.
- Retrying by reverting to `open` (rather than a dedicated `retrying` status) keeps the state machine simple but means `open` now means either "still accumulating data" or "recovering from a failure" — indistinguishable without checking `retryCount`/`lastError`. Acceptable for now; a dedicated status could be added later if this ambiguity causes confusion in monitoring.

## Gate Report

- Iteration: 7
- Date: 2026-08-23
- Owner: Alexandra Cabral (with GitHub Copilot)
- Scope completed: retry-count tracking, failure recording, retry-until-limit-then-fail behavior in `run_cycle_pipeline`.
- Tests executed: `python -m pytest Namibia/azure_aggregation/tests -q`
- Result: PASS (code + tests); live transient-failure recovery test not practical without a deployed environment.
- Missing items: optimistic locking (documented risk, not implemented); live failure-injection test.
- Immediate follow-ups: Iteration 8 (cleanup/retention) should also clean up old `failed` cycle rows, not just `sent`/`expired`.
- Checklist changes applied: none yet — first pass.
