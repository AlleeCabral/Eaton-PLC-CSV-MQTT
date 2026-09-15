# Namibia Azure Aggregation - Fresh Conversation Handoff

**Updated:** 2026-09-03  
**Workspace:** `C:\Users\AlexandraCabral\Documents\Eaton_PLC\BrightLayer`  
**Project:** `applications/namibia-aggregation/azure_aggregation`
**Azure subscription:** `Boreal Light` (`47b9cfe5-6ca3-4ad4-a4ca-d870926688b0`)  
**Resource group:** `rg-brightlayer-dev`  
**Function App:** `brightlayer-func-dev-001`  
**Hosting:** Flex Consumption, Linux, Python 3.11

## Objective

Read Namibia PLC telemetry from Brightlayer, aggregate KPI values every five minutes, and publish aggregate trends to a separate Brightlayer virtual device through Azure IoT Hub MQTT.

## Brightlayer API Facts

- API prefix: `https://portal.machinery-monitoring.com`
- Token endpoint: `POST /api/v1/auth/serviceaccount/token`
- Telemetry endpoint: `POST /api/v1/dashboard/devices/timeseries`
- Discovery endpoint: `GET /api/v1/dashboard/organization/{organizationId}/devices`
- Trend channels use `timeseries`; do not use `realtime` for current test channels.

### Time Zone Rule

The web export contains offset timestamps, while the external API requires whole-second UTC timestamps ending in `Z`.

```text
Website CSV: 2026-09-01T15:10:23+02:00
API UTC:     2026-09-01T13:10:23Z
```

Convert timestamps with their given offset. Do not manually subtract two hours. Returned measurements depend on data available in the requested UTC interval. Eaton's documentation does not state a device/tag-pair request limit, so the project must not impose one.

## Current Trial Device

The canonical registry is [azure_aggregation/config/brightlayer-test-devices.json](azure_aggregation/config/brightlayer-test-devices.json). It is designed to grow to all 15 devices.

- API organization ID: `8427fc24-b752-436a-8ac9-0c9318992fc3`
- Organization code, not API input: `C95FF99D-421B-47D9-AD28-654B4760D7B3`
- Service account ID: `d6faf7fc-2ffb-4247-b1db-67349b3424d9`
- Gateway: `cb118f9e-3a25-4e1f-8f37-f9a37c48c1cb`, name `165_Evale`
- Child telemetry device: `8a7f416d-a452-2b11-0800-1e0d06362200`, name `Nam5`
- Ontology profile ID: `aa0af1a1-895c-4b99-8e44-e3fe82cc3385`
- Adopter ID: `861a306d-05d1-4963-fd52-bd55f143766f`
- Trial tags: `10549363` pH Input, `10549365` pH Output, `10549432` Solar Power KWh Total

The gateway is relationship metadata. Use the child device ID in API telemetry request pairs and aggregation KPI sources.

## Verified Live Results

Authentication and discovery with the IDs above succeeded. Discovery returned child `Nam5` / `8a7f416d-a452-2b11-0800-1e0d06362200`.

The local web-export interval:

```text
2026-09-01T14:00:00+02:00 to 2026-09-01T15:10:00+02:00
```

maps to API UTC:

```text
2026-09-01T12:00:00Z to 2026-09-01T13:10:00Z
```

The request for child/tag pair `8a7f416d-a452-2b11-0800-1e0d06362200` / `10549363` returned timestamped `0.0` values, including records from `2026-09-01T13:05:53Z` through `2026-09-01T13:10:23Z`. A later request starting at `14:00:00Z` was empty because that corresponds to local time after the web-exported measurements.

## Local API Test Workflow

Use [azure_aggregation/scripts/run_brightlayer_probe.ps1](azure_aggregation/scripts/run_brightlayer_probe.ps1). It converts local timestamps to UTC, prompts for the secret securely, prints the JSON report, can save it, and clears temporary credentials. The short probe command reference is in [azure_aggregation/docs/How_to_run_probe.txt](azure_aggregation/docs/How_to_run_probe.txt).

```powershell
.\Namibia\azure_aggregation\scripts\run_brightlayer_probe.ps1 `
  -DeviceId '8a7f416d-a452-2b11-0800-1e0d06362200' `
  -TraitIds '10549363' `
  -StartLocal '2026-09-01T14:00:00+02:00' `
  -EndLocal '2026-09-01T15:10:00+02:00' `
  -OutputPath '.\Namibia\azure_aggregation\reports\nam5-ph-input.json'
```

Saved measurements are at `timeseriesResponse.timeSeries[*].results.values`. Do not append `$env:...` assignments to the Python filename; the runner avoids this PowerShell error.

## Code Status

Implemented locally:

- Queue-based Function flow: timer planner -> Storage Queue -> aggregation worker.
- Table Storage cycle claims, snapshots, latest-value carry-forward, audit records, and idempotency.
- `WRITEBACK_MODE=dry_run` prevents Brightlayer writes and IoT client creation.
- Brightlayer client supports service-account token generation, timeseries, and device discovery.
- All 12 Nam5 KPI source pairs in [azure_aggregation/config/nam5-single-device-kpi-map.json](azure_aggregation/config/nam5-single-device-kpi-map.json) use child `8a7f416d-a452-2b11-0800-1e0d06362200`.
- No undocumented ten-pair cap exists in runtime config, Bicep, or request batching.

Key files:

- [azure_aggregation/src/function_app.py](azure_aggregation/src/function_app.py)
- [azure_aggregation/src/shared/brightlayer_client.py](azure_aggregation/src/shared/brightlayer_client.py)
- [azure_aggregation/src/modules/fetch_source_telemetry.py](azure_aggregation/src/modules/fetch_source_telemetry.py)
- [azure_aggregation/scripts/probe_brightlayer_device.py](azure_aggregation/scripts/probe_brightlayer_device.py)
- [azure_aggregation/scripts/run_brightlayer_probe.ps1](azure_aggregation/scripts/run_brightlayer_probe.ps1)
- [azure_aggregation/config/brightlayer-test-devices.json](azure_aggregation/config/brightlayer-test-devices.json)

## Validation Status

Latest complete local suite:

```text
91 passed in 3.07s
```

```powershell
.\.venv\Scripts\python.exe -m pytest Namibia\azure_aggregation\tests -q
```

Focused tests passed after the local-runner work: `12 passed`. PowerShell syntax validation, registry JSON parsing, Bicep compilation, and editor diagnostics were clean.

## Azure State and Remaining Work

The corrected Linux-compatible Function ZIP was built but the final package has not been deployed. Deploy only after reconciling Key Vault secrets and validating real source configuration.

1. Confirm Key Vault contains the secrets required by the selected `WRITEBACK_MODE`.
2. Deploy the current package and verify Azure indexes `cycle_planner_timer`, `aggregation_cycle_worker`, and `cleanup_cycles`.
3. Keep `WRITEBACK_MODE=dry_run` until read behavior and calculated KPI payloads are approved.
4. Only then provision/validate the aggregate device and enable writeback.

## Security

A service-account secret was exposed in a chat screenshot during testing. Treat it as compromised: revoke and rotate it in Brightlayer before any further live API test or deployment. Do not commit, print, or include the replacement secret in reports.

## Suggested First Prompt

```text
Read `applications/namibia-aggregation/FRESH_CONVERSATION_HANDOFF.md`, `applications/namibia-aggregation/azure_aggregation/README.md`, and `applications/namibia-aggregation/azure_aggregation/config/brightlayer-test-devices.json`. Continue the Brightlayer API integration from the recorded state. Preserve the UTC conversion rule, use child device IDs for telemetry, do not reintroduce an undocumented request-pair limit, and do not expose secrets.
```

Expected JSON contracts:

```json
{
  "connectionString": "HostName=...;DeviceId=...;SharedAccessKey=..."
}
```

```json
{
  "kpiTagMap": {
    "production_total": "<aggregate ontology tagId>"
  }
}
```

See `Namibia/PENDING_INFO.md` for the full drafts and missing values.

## Brightlayer organization information

- Organization Name: `BorealEU-POC`
- Organization Code: `C95FF99D-421B-47D9-AD28-654B4760D7B3`
- Activation Code: `BORE-541275`

Working assumption: Organization Code is likely the API `organizationId` because it is a GUID matching the documented API shape. This is not yet confirmed by Eaton/Brightlayer support.

## KPI scope

Twelve aggregate outputs:

- Production: total, today/last-24h assumption, month
- Solar energy: total, today/last-24h assumption, month
- Grid energy: total, today/last-24h assumption, month
- Avoided CO2: total, today/last-24h assumption, month

Source ontology tag IDs are documented in `Namibia/PENDING_INFO.md`.

Open business question: does "last 24h" mean the ontology's `Today` value or a rolling 24-hour window?

## Remaining live blockers after deployment is healthy

1. Confirm Function App managed identity has `Key Vault Secrets User` on `kv-namibia-agg-dev-001`.
2. Confirm storage access / connection string works for Table Storage.
3. Obtain Brightlayer service-account credentials.
4. Confirm Organization Code is the REST API `organizationId`.
5. Retrieve all Namibia PLC Brightlayer device IDs.
6. Confirm `EXPECTED_PLC_COUNT=15`.
7. Create `Aggregated_Namibia` virtual device and ontology in Brightlayer.
8. Obtain its IoT Hub device connection string.
9. Populate the aggregate device's KPI tag IDs.
10. Confirm `Today` versus rolling last-24-hours semantics.

## Security note

Storage account credentials and other live secrets were previously pasted into chat. Rotate any exposed keys before production and store all secrets only in Key Vault / Azure configuration.

## Suggested opening prompt for the new conversation

```text
Continue the Namibia Azure aggregation deployment using Namibia/FRESH_CONVERSATION_HANDOFF.md as the source of truth. First deploy the already-built Linux-compatible ZIP at %TEMP%\brightlayer_func_deploy.zip, verify the two timer functions are indexed, then diagnose only the next concrete Azure error. Keep Namibia/PENDING_INFO.md updated and do not broaden scope.
```
