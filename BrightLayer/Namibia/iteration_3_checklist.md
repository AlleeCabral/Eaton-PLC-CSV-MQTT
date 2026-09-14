# Iteration 3 Checklist - Telemetry Normalization and Snapshot Storage

## Iteration Goal

Turn raw Brightlayer timeseries responses into freshness-aware snapshot rows and persist them, per the operational rules in `iteration_memory.md` (permissive mode, carry-forward last known value, explicit stale/offline metadata, no zero-fill).

## Scope

- Flatten a raw `/dashboard/devices/timeseries` response into one record per device/trait (latest value in the window).
- Normalize each record into a snapshot row with explicit `quality` (online/stale/offline) and freshness timestamps, using `PLC_STALE_TIMEOUT_SECONDS` / `PLC_OFFLINE_TIMEOUT_SECONDS` from config.
- Wire `modules/fetch_source_telemetry.py` to call `BrightlayerClient.get_timeseries()` (Iteration 1), normalize the response, and persist rows via `StorageCycleRepo.upsert_snapshot()` (Iteration 2).
- Out of scope: aggregation math (Iteration 4), MQTT writeback (Iteration 5), full orchestration/timer-to-queue wiring (Iteration 6), retry-specific handling beyond what `BrightlayerClient` already does (Iteration 7).

## Done Criteria

1. `flatten_brightlayer_timeseries_response()` correctly extracts the most recent value per device/trait from the documented response shape.
2. `normalize_timeseries_records()` classifies each record as `online`/`stale`/`offline` based on age vs. the two configured timeout thresholds, and never substitutes a zero or blank value for a missing/late one.
3. `FetchSourceTelemetry.run()` fetches, normalizes, and persists snapshot rows for a given cycle window and device/trait list, returning a summary including `receivedCount` (feeds Iteration 2's `determine_cycle_status`).
4. Unit tests cover: response flattening, all three quality classifications, missing-timestamp handling, and the end-to-end `run()` flow with mocked client + repo.

## Task Checklist

- [x] Add `flatten_brightlayer_timeseries_response(response)` to `shared/telemetry_normalizer.py`.
- [x] Rewrite `normalize_timeseries_records(records, now_utc, stale_timeout_seconds, offline_timeout_seconds)` to add `quality`, `lastUpdatedUtc`, `staleSinceUtc` fields instead of the Iteration 0 passthrough (which defaulted quality to `"good"` unconditionally — that violated the "no silent defaulting" rule and is now removed).
- [x] Rewrite `modules/fetch_source_telemetry.py` `FetchSourceTelemetry` to take a `storage_repo` dependency and implement `run(cycle_key, cycle_start_utc, cycle_end_utc, devices)` for real.
- [x] Add `tests/test_telemetry_normalizer.py` covering flattening and all quality classifications (online/stale/offline/missing-timestamp).
- [x] Add `tests/test_fetch_source_telemetry.py` covering the end-to-end `run()` flow with mocked `BrightlayerClient` and `StorageCycleRepo`.

## Gate Checks

- [x] `python -m pytest Namibia/azure_aggregation/tests -q` passes with new tests included.
- [x] No zero-fill: a record with a missing/unparseable timestamp is classified `offline`, never given a fabricated value.
- [ ] Live smoke test against real Brightlayer timeseries data for at least one Namibia source device. **NOT DONE** — blocked on Key Vault secrets (`brightlayer-source-device-list`, `brightlayer-source-trait-list`) not yet confirmed populated.

## Quick Re-evaluation Rule

- `FetchSourceTelemetry.run()` currently takes `devices` as an explicit parameter rather than reading `brightlayer-source-device-list`/`brightlayer-source-trait-list` from Key Vault itself — that wiring belongs to Iteration 6 (orchestration), where the timer trigger will assemble the device list from config and call this module.
- Quality thresholds assume `PLC_STALE_TIMEOUT_SECONDS < PLC_OFFLINE_TIMEOUT_SECONDS` (300 < 600 in current config) — not defensively validated here; would be worth a config-time assertion in a hardening pass.

## Gate Report

- Iteration: 3
- Date: 2026-08-22
- Owner: Alexandra Cabral (with GitHub Copilot)
- Scope completed: real timeseries response flattening, freshness-aware normalization (online/stale/offline), real `FetchSourceTelemetry.run()` wired to Iteration 1 client + Iteration 2 repo.
- Tests executed: `python -m pytest Namibia/azure_aggregation/tests -q`
- Result: PASS (code + tests); live Brightlayer smoke test still pending.
- Missing items: live smoke test; device/trait list still passed explicitly rather than sourced from Key Vault (deferred to Iteration 6).
- Immediate follow-ups: Iteration 4 (aggregation engine) can now consume snapshot rows written by this iteration.
- Checklist changes applied: none yet — first pass.
