# Iteration 5 Checklist - Brightlayer Writeback Adapter (Azure IoT Hub MQTT)

## Iteration Goal

Publish computed aggregate KPIs (Iteration 4 output) to Brightlayer via the same mechanism the PLCs use: an Azure IoT Hub device-to-cloud MQTT message, targeting the `Aggregated_Namibia` virtual device's own device identity. Confirmed in [Namibia/azure_aggregation_architecture.md](../azure_aggregation_architecture.md) — there is no REST endpoint for telemetry writeback, only MQTT.

## Scope

- Build a `Trends` payload (`{"trends": [{"c": tagId, "t": epoch, "v": value}, ...]}`) from `AggregateCycle.run()` output, mapped to Brightlayer tagIds via a `kpi_tag_map`.
- Publish that payload as an IoT Hub device-to-cloud message using the official `azure-iot-device` SDK (connect → send → disconnect per cycle, since Function Apps are not long-running processes).
- Out of scope: the one-time `DeviceTree` registration message for `Aggregated_Namibia` (a manual/setup-time operation, not a per-cycle one — tracked as a prerequisite, not part of this iteration's per-cycle code path); full orchestration wiring (Iteration 6); retry/failure handling beyond what the SDK itself provides (Iteration 7).

## Done Criteria

1. `build_trends_payload()` converts `AggregateCycle` results into the documented `{"trends": [...]}` shape, using each KPI's `sourceField`/name → `tagId` mapping.
2. KPIs with `status != "ok"` (i.e. `no_data` this cycle) are excluded from the payload rather than fabricated — consistent with "no zero-fill" policy from earlier iterations. Brightlayer simply doesn't receive an update for that KPI this cycle.
3. `WritebackToBrightlayer.run()` builds the payload and publishes it via an injected IoT Hub client (real SDK in production, a fake/mock in tests) — connect, send one message, disconnect.
4. Unit tests cover: payload construction (including exclusion of `no_data` KPIs), and the publish flow with a mocked IoT Hub client (no real device connection needed).

## Task Checklist

- [x] Add `azure-iot-device` to `src/requirements.txt` and install it in the dev venv.
- [x] Rewrite `modules/writeback_to_brightlayer.py`:
  - [x] `build_trends_payload(aggregates, kpi_tag_map, now_utc)` — maps each `ok` KPI to `{"c": tagId, "t": epoch, "v": value}`; skips `no_data` KPIs.
  - [x] `WritebackToBrightlayer(iot_client_factory, kpi_tag_map, config)` — takes a factory function so the real `IoTHubDeviceClient.create_from_connection_string(...)` (or a test double) can be injected without this module depending on Key Vault directly.
  - [x] `run(cycle_key, aggregates)` — builds the payload, connects the IoT Hub client, sends one `Message`, disconnects, returns a result summary.
- [x] Add `tests/test_writeback_to_brightlayer.py` covering payload construction (ok + no_data KPIs) and the connect/send/disconnect publish flow with a fake IoT client.

## Gate Checks

- [x] `python -m pytest Namibia/azure_aggregation/tests -q` passes with new tests included.
- [x] No real IoT Hub connection required to run tests (fully mocked client).
- [ ] Live smoke test: register `Aggregated_Namibia` in Brightlayer (DeviceTree message, one-time), then confirm a real Trends message appears as fresh data on its dashboard. **NOT DONE** — blocked on: (a) `Aggregated_Namibia` device/ontology not yet created in Brightlayer, (b) `brightlayer-writeback-credentials` Key Vault secret not yet populated with its IoT Hub connection string, (c) `brightlayer-aggregate-device-config`/KPI-to-tagId map not yet defined for the real KPIs.

## Quick Re-evaluation Rule

- The one-time `DeviceTree` registration message (device + ontology profile GUIDs) is intentionally NOT implemented as part of this iteration's per-cycle `run()` — it's a setup-time operation that should happen once when `Aggregated_Namibia` is provisioned, not on every cycle. If we need it in code (rather than a manual Node-RED-style one-off script), it belongs in a separate provisioning script, not the recurring writeback path.
- `kpi_tag_map` (KPI name → Brightlayer tagId) is a new, separate contract from Iteration 4's `kpi_map` (KPI name → source device/trait + operation). Both will ultimately be populated from `brightlayer-aggregate-device-config` / `aggregation-kpi-map` Key Vault secrets, but the exact secret JSON shape mapping to both is not yet confirmed against a real Brightlayer ontology for `Aggregated_Namibia`.

## Gate Report

- Iteration: 5
- Date: 2026-08-22
- Owner: Alexandra Cabral (with GitHub Copilot)
- Scope completed: real Trends payload builder, real `WritebackToBrightlayer.run()` using injected `azure-iot-device` client, full unit test coverage.
- Tests executed: `python -m pytest Namibia/azure_aggregation/tests -q`
- Result: PASS (code + tests); live verification blocked on Brightlayer-side prerequisites (device/ontology + credentials + tag map), not on this code.
- Missing items: `Aggregated_Namibia` device/ontology creation in Brightlayer; `brightlayer-writeback-credentials` secret; `brightlayer-aggregate-device-config` KPI-to-tagId map; one-time DeviceTree provisioning script.
- Immediate follow-ups: Iteration 6 (orchestration) can now wire Iterations 1-5 together into the actual timer/queue triggers.
- Checklist changes applied: none yet — first pass.
