# Iteration 1 Checklist - Brightlayer Authentication and Read Client

## Iteration Goal

Implement a real, tested client for the Brightlayer REST API's read surface (service account token, realtime read, timeseries read, organization device lookup), replacing the Iteration 0 stub. This client is a dependency for Iteration 3 (fetch source telemetry) and Iteration 2 (cycle planner needs no direct dependency but benefits from the same retry policy).

## Scope

- Real `POST /api/v1/auth/serviceaccount/token` call with caching and 401-triggered refresh.
- Real `POST /api/v1/dashboard/devices/{deviceId}/realtime` call.
- Real `POST /api/v1/dashboard/devices/timeseries` call.
- Real `GET /api/v1/dashboard/organization/{organizationId}/devices` call.
- Retry policy wiring (`shared/retry_policy.py`) for all authorized requests.
- Out of scope: writeback/MQTT (Iteration 5), telemetry normalization (Iteration 3), and querying with real Namibia credentials against the live Brightlayer environment (secrets not yet confirmed present in Key Vault).

## Done Criteria

1. `BrightlayerClient` implements token/realtime/timeseries/devices against the documented API shapes.
2. Token is cached and only refreshed on 401 or explicit `force_refresh`.
3. All authorized requests go through `with_retry` using `MAX_RETRIES` / `RETRY_BASE_SECONDS`.
4. Unit tests cover success and failure paths without making real network calls.
5. A real bug found in Iteration 0's stub (`retry_policy.with_retry` never actually slept) is fixed.

## Task Checklist

- [x] Replace stub `get_token()` / `request()` in `shared/brightlayer_client.py` with a real `BrightlayerClient` class.
- [x] Implement `get_token(force_refresh=False)` — POST to `/api/v1/auth/serviceaccount/token`, cache result, raise `BrightlayerAuthError` on non-200 or missing `token` field.
- [x] Implement `get_realtime(device_id, tag_id)` — POST to `/api/v1/dashboard/devices/{deviceId}/realtime`.
- [x] Implement `get_timeseries(devices, start_date_time, end_date_time)` — POST to `/api/v1/dashboard/devices/timeseries`.
- [x] Implement `get_devices(organization_id)` — GET to `/api/v1/dashboard/organization/{organizationId}/devices`.
- [x] Wrap all authorized calls in `_authorized_request` with automatic 401 → token refresh → retry-once behavior.
- [x] Wire `with_retry` (from `shared/retry_policy.py`) into token fetch and authorized requests.
- [x] Fix `retry_policy.with_retry` — computed backoff `delay` was discarded instead of sleeping; added `time.sleep(delay)`.
- [x] Add `tests/test_brightlayer_client.py` covering: token success + caching, token failure (missing field), token failure (non-200), realtime parsing, timeseries body construction, devices parsing, 401 → refresh → retry flow.

## Gate Checks

- [x] `python -m pytest Namibia/azure_aggregation/tests -q` passes (12/12 at time of this gate, including 7 new Brightlayer client tests).
- [x] No real network calls made in tests (all `requests.Session` calls mocked).
- [ ] Live smoke test against the real Brightlayer API with real `brightlayer-service-account-id` / `brightlayer-service-account-secret` / `brightlayer-api-prefix` from Key Vault. **NOT DONE** — blocked on confirming these secrets exist in `kv-namibia-agg-dev-001` (tracked in Iteration 2+ Key Vault verification step).

## Quick Re-evaluation Rule

Re-evaluated after implementation:
- The client is code-complete and unit-tested but has never been exercised against the live Brightlayer environment. Treat as "implemented, not yet verified live" until the Key Vault secrets are confirmed and a manual smoke test is run.
- No queue/orchestration wiring yet — this client is currently unused by any running module (that happens in Iteration 3).

## Gate Report

- Iteration: 1
- Date: 2026-08-22
- Owner: Alexandra Cabral (with GitHub Copilot)
- Scope completed: real `BrightlayerClient` (token/realtime/timeseries/devices), retry policy bug fix, full unit test coverage.
- Tests executed: `python -m pytest Namibia/azure_aggregation/tests -q` → 12 passed.
- Result: **PASS** (code + tests); **live verification pending** (see gate checks above).
- Missing items: live smoke test against real Brightlayer API; confirmation that Key Vault secrets `brightlayer-service-account-id`, `brightlayer-service-account-secret`, `brightlayer-api-prefix` exist and are correct.
- Immediate follow-ups: verify Key Vault secrets before treating Iteration 3 (fetch source telemetry) as testable end-to-end.
- Checklist changes applied: added explicit "live verification pending" gate item since Iteration 0/1 templates didn't originally distinguish unit-tested vs. live-verified.
