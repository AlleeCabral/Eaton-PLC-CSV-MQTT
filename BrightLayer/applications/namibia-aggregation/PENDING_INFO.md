# Namibia Aggregation — Missing Information Tracker

Structured checklist of exactly what's still needed to run live tests, kept up to date as information arrives. See [azure_aggregation_architecture_v2.md](azure_aggregation_architecture_v2.md) for the implemented queue-based architecture.

## Current implementation state (2026-08-24)

- Azure function indexing is fixed. The live app indexed `cycle_planner_timer` and `cleanup_cycles` after the corrected Linux package deployment.
- `cycle_planner_timer` is intentionally disabled in Azure because the previous all-in-one timer failed every minute.
- The local implementation now uses a five-minute timer to enqueue completed cycles and a queue-triggered `aggregation_cycle_worker` for retryable processing.
- `WRITEBACK_MODE=dry_run` now prevents aggregate-secret reads and IoT client construction. Dry-run results are persisted to `CycleAudit` and summarized in Application Insights.
- Queue delivery is protected by atomic Table Storage cycle claims and sent-cycle deduplication.
- Brightlayer source pairs are derived from `aggregation-kpi-map`; separate source-device and source-trait secrets were removed.
- Missing current pairs use persisted latest observations with original timestamps and explicit carried/stale/offline metadata. Zero-fill remains forbidden.
- Current validation: 79 automated tests pass; FC1 Bicep compiles without diagnostics; deterministic package build passes.
- No redesigned package has been deployed. The scheduler must remain disabled until the live gates below pass.

## 1. Brightlayer organization identity

- **Organization Name**: `BorealEU-POC` — confirmed by user (screenshot from Brightlayer portal "Organization" page).
- **Organization Code**: `C95FF99D-421B-47D9-AD28-654B4760D7B3` — confirmed by user.
  - **UNCONFIRMED ASSUMPTION**: this is very likely the `organizationId` used in `GET /api/v1/dashboard/organization/{organizationId}/devices` (it's a GUID, matching the shape of the example `organizationId` in the official API doc: `723af19b-95d6-43e0-b629-a18d1efe9225`). Treat as the working value for `brightlayer-organization-id`, but **please confirm with Eaton/Brightlayer support that "Organization Code" = API `organizationId`** — it's possible the portal's "Organization Code" and the API's `organizationId` are different identifiers that happen to both be GUIDs.
- **Activation Code**: `BORE-541275` — confirmed by user. This looks like a device/org onboarding code (different format, not a GUID) — likely NOT the same as `organizationId`. Not currently needed by any secret contract, noted for reference only.

## 2. Aggregation KPIs (confirmed by user, 2026-08-23)

| Parameter | Total | Last 24h | Last month | Notes |
|---|---|---|---|---|
| Production | yes | yes | yes | total/monthly/daily/hourly values already calculated per PLC |
| Solar energy | yes | yes | yes | same |
| Grid energy | yes | yes | yes | same |
| CO2 emission (avoided, solar vs grid) | yes | yes | yes | same |

**CONFIRMED DECISION (2026-08-24)**: "last 24h" means the PLC/Brightlayer `Today` counter since its local midnight reset. It is not a rolling 24-hour calculation. New aggregate-device labels should say `Today` rather than `last24h` to avoid ambiguity.

### Draft canonical `aggregation-kpi-map` secret (per-device sources still need real Namibia device IDs — see §3)

This is now the single runtime source contract. Brightlayer API request pairs are derived and deduplicated from the KPI `sources` entries.

```json
{
  "kpis": [
    { "name": "production_total",     "operation": "sum", "sources": [ /* {"deviceId": "<TBD>", "traitId": "10549449"} per PLC */ ], "unit": "kWh", "precision": 2 },
    { "name": "production_today",     "operation": "sum", "sources": [ /* traitId 10549440 per PLC */ ], "unit": "kWh", "precision": 2 },
    { "name": "production_last_month","operation": "sum", "sources": [ /* traitId 10549447 per PLC */ ], "unit": "kWh", "precision": 2 },

    { "name": "solar_total",          "operation": "sum", "sources": [ /* traitId 10549432 per PLC */ ], "unit": "Kwh", "precision": 2 },
    { "name": "solar_today",          "operation": "sum", "sources": [ /* traitId 10549437 per PLC */ ], "unit": "Kwh", "precision": 2 },
    { "name": "solar_last_month",     "operation": "sum", "sources": [ /* traitId 10549438 per PLC */ ], "unit": "Kwh", "precision": 2 },

    { "name": "grid_total",           "operation": "sum", "sources": [ /* traitId 10549444 per PLC */ ], "unit": "Kwh", "precision": 2 },
    { "name": "grid_today",           "operation": "sum", "sources": [ /* traitId 10549442 per PLC */ ], "unit": "Kwh", "precision": 2 },
    { "name": "grid_last_month",      "operation": "sum", "sources": [ /* traitId 10549446 per PLC */ ], "unit": "Kwh", "precision": 2 },

    { "name": "co2_total",            "operation": "sum", "sources": [ /* traitId 10549389 per PLC */ ], "unit": "m3", "precision": 2 },
    { "name": "co2_today",            "operation": "sum", "sources": [ /* traitId 10549387 per PLC */ ], "unit": "m3", "precision": 2 },
    { "name": "co2_last_month",       "operation": "sum", "sources": [ /* traitId 10549382 per PLC */ ], "unit": "m3", "precision": 2 }
  ]
}
```

Ontology tagId source (from `water_filtration_Nam` ontology, `Machine`-level channels — same for every PLC of this model, only `deviceId` differs per physical site):

| KPI | keyValue | tagId |
|---|---|---|
| production_total | `_81_Output_Power_KWh_Total` | 10549449 |
| production_today | `_83_Output_Power_KWh_Today` | 10549440 |
| production_last_month | `_84_Output_Power_KWh_This_Month` | 10549447 |
| solar_total | `_73_Solar_Power_KWh_Total` | 10549432 |
| solar_today | `_75_Solar_Power_KWh_Today` | 10549437 |
| solar_last_month | `_76_Solar_Power_KWh_This_Month` | 10549438 |
| grid_total | `_77_Grid_Power_KWh_Total` | 10549444 |
| grid_today | `_79_Grid_Power_KWh_Today` | 10549442 |
| grid_last_month | `_80_Grid_Power_KWh_This_Month` | 10549446 |
| co2_total | `_142_CO2_Saving_Total` | 10549389 |
| co2_today | `_144_CO2_Saving_Today` | 10549387 |
| co2_last_month | `_145_CO2_Saving_This_Month` | 10549382 |

### Draft `brightlayer-aggregate-device-config` secret shape (KPI → Brightlayer tagId on the NEW `Aggregated_Namibia` device — still needs real tagIds once that device's ontology is created)

```json
{
  "kpiTagMap": {
    "production_total": "<TBD - new tagId on Aggregated_Namibia ontology>",
    "production_today": "<TBD>",
    "production_last_month": "<TBD>",
    "solar_total": "<TBD>",
    "solar_today": "<TBD>",
    "solar_last_month": "<TBD>",
    "grid_total": "<TBD>",
    "grid_today": "<TBD>",
    "grid_last_month": "<TBD>",
    "co2_total": "<TBD>",
    "co2_today": "<TBD>",
    "co2_last_month": "<TBD>"
  }
}
```

## 3. Still fully missing (blocking live tests)

- [ ] **Namibia PLC device IDs** (Brightlayer device GUIDs, one per physical site/PLC) — needed to fill in every `sources` list above. Can be retrieved via `GET /api/v1/dashboard/organization/{organizationId}/devices` once §1's org ID is confirmed and service account credentials (below) exist.
- [ ] `brightlayer-service-account-id` / `brightlayer-service-account-secret` / `brightlayer-api-prefix` — request from Eaton/Brightlayer.
- [ ] Read-only Brightlayer API characterization: test one PLC, then increasing sequential device/tag batches; record the supported request size and set `TIMESERIES_BATCH_SIZE` from evidence. The supplied API PDF does not document a maximum or rate limit.
- [ ] Resolve whether child `Nam5` has its own GUID. The temporary dry-run map uses parent `165_Evade` (`cb118f9e-3a25-4e1f-8f37-f9a37c48c1cb`) only as a candidate pending device-discovery/realtime evidence.
- [ ] Organization lookup currently returns `401` after successful token generation for candidate Organization Code `C95FF99D-421B-47D9-AD28-654B4760D7B3`. Confirm the API organization ID and whether the service account has device-list permission; direct device reads are tested independently.
- [x] Service-account token generation succeeds against the EMEA production API. Python clients require an explicit non-default `User-Agent` to pass the Azure Application Gateway.
- [x] Realtime request using parent `165_Evade` GUID and source tag `10549440` is authorized (`200`) but returns empty value/unit/timestamp. This indicates the source channel likely belongs to child `Nam5` and requires its child GUID.
- [ ] Obtain the Brightlayer/API device GUID for child `Nam5`, or grant device-list permission so it can be discovered. Do not treat the authorized-but-empty parent response as valid telemetry.
- [ ] Retest after correcting timeseries timestamps to whole-second UTC (`YYYY-MM-DDTHH:MM:SSZ`). The API rejected fractional seconds with `Start date and time is not in valid UTC format`. Latest parent-device attempt: token succeeded, realtime returned `200` with empty value/unit/timestamp, organization discovery returned `401`, and no writes were attempted.
- [x] Timeseries request format is now verified: whole-second UTC timestamps return `200`, and one 12-pair request is accepted. Brightlayer returned all 12 requested series for parent `165_Evade`, but every series had an empty `values` array in the 15-minute window.
- [ ] Run the next read-only probe with a 24-hour window and operational tag `10549434`. If both the operational realtime tag and all 24-hour KPI series remain empty, treat the parent GUID as the wrong telemetry identity or the MQTT pipeline as still not publishing into this Brightlayer device.
- [x] Brightlayer timeseries hard limit discovered from live API validation: device/tag/trait combinations cannot exceed 10 per request. Runtime configuration now enforces `TIMESERIES_BATCH_SIZE=1..10`, default `10`; the 12-KPI read uses two sequential requests.
- [ ] `Aggregated_Namibia` virtual device + ontology created in Brightlayer, with its own tagIds for the 12 KPIs above.
- [ ] `brightlayer-writeback-credentials` (IoT Hub connection string for `Aggregated_Namibia`) — available once the device above is provisioned.
- [ ] Confirm whether Namibia devices share the same IoT Hub instance as `125_Senegal` (`iot-etnblc-rm-ext-prd-weu-p01.azure-devices.net`) or use a different one.
- [ ] Reconcile Key Vault: the live app setting references nonexistent `kv-namibia-agg-dev-001`, while the resource group contains `brightlayerkvdev001`. Confirm `brightlayerkvdev001` is the intended vault, update `KEYVAULT_URI`, and verify **Key Vault Secrets User** for the Function managed identity.
- [ ] Create/verify Queue Storage `aggregation-cycles` and tables `CycleStatus`, `CycleDataSnapshot`, `CycleAudit`, and `LatestObservation` in the live storage account.
- [ ] Confirm `EXPECTED_PLC_COUNT=15` is still correct for Namibia's actual PLC count.
- [ ] Configure GitHub OIDC federation and least-privilege deployment access before using the CI deployment job.
- [ ] Deploy the deterministic queue-based package with the scheduler still disabled; verify three indexed functions and worker binding health.
- [ ] Run one read-only cycle, then one controlled 12-point writeback and duplicate-message replay before enabling continuous scheduling.

## Update log

- 2026-08-24: Replaced all-in-one timer design with Timer → Storage Queue → worker. Added atomic cycle claims, platform retry/poison behavior, persisted carry-forward, source-pair coverage, per-KPI quality counts, canonical KPI source contract, deterministic CI packaging, and FC1 Bicep. Confirmed Today-since-midnight semantics. Disabled the failing live scheduler pending integration gates.
- 2026-08-24: Added hard-isolated dry-run mode, `CycleAudit` persistence, a 12-KPI `Nam5` characterization map, and a credential-safe read-only API probe. Aggregate channel IDs and IoT Hub credentials are not required for this gate.
- 2026-08-23: Added organization info (name/code/activation code) and the 12-KPI aggregation list from user. Drafted `aggregation-kpi-map` and `brightlayer-aggregate-device-config` shapes using existing ontology tagIds. Flagged org-code-vs-organizationId and "last 24h" vs "Today" as open questions.
