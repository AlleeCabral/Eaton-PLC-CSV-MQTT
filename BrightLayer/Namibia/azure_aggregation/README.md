# Namibia Brightlayer Aggregation

Azure Functions application that aggregates 12 Today/month/total KPIs across Namibia PLC devices and publishes them to the `Aggregated_Namibia` Brightlayer virtual device.

See [../azure_aggregation_architecture_v2.md](../azure_aggregation_architecture_v2.md) for the complete runtime and deployment diagram.

## Project layout

- `src/` - Azure Functions entry point, runtime modules, and shared services.
- `infra/` - Bicep templates and environment parameters.
- `config/` - Brightlayer device registry and KPI source maps.
- `scripts/` - package builder and executable API probe scripts.
- `tests/` - automated tests; captured network fixtures are in `tests/fixtures/`.
- `docs/` - setup notes and development prompts.
- `reports/` - saved, secret-free probe reports.
- `artifacts/` - generated deployment packages.

## Execution model

- `cycle_planner_timer`: every five minutes, atomically claims the last completed interval and writes a versioned work item to Queue Storage.
- `aggregation_cycle_worker`: reads Brightlayer telemetry, applies persisted carry-forward and completeness policy, aggregates KPIs, and publishes one IoT Hub Trends payload.
- `cleanup_cycles`: removes expired cycle and snapshot state.

Queue delivery is at least once. Table Storage owns cycle and writeback idempotency. Repeated worker failures move to the queue's poison queue.

## Required app settings

```text
EXPECTED_PLC_COUNT=15
CYCLE_INTERVAL_MINUTES=5
CYCLE_SCHEDULE=0 */5 * * * *
CYCLE_QUEUE_NAME=aggregation-cycles
CYCLE_GRACE_SECONDS=90
FETCH_OVERLAP_MINUTES=15
AGGREGATION_MODE=permissive
WRITEBACK_MODE=dry_run
LAST_KNOWN_VALUE_POLICY=carry_forward
ZERO_FILL_DISABLED=true
PLC_STALE_TIMEOUT_SECONDS=300
PLC_OFFLINE_TIMEOUT_SECONDS=600
MAX_RETRIES=3
RETRY_BASE_SECONDS=10
CYCLE_TABLE_STATUS=CycleStatus
CYCLE_TABLE_SNAPSHOT=CycleDataSnapshot
CYCLE_TABLE_AUDIT=CycleAudit
CYCLE_TABLE_LATEST=LatestObservation
RETENTION_HOURS=48
KEYVAULT_URI=https://<vault>.vault.azure.net/
```

Flex Consumption owns the Python runtime through `functionAppConfig.runtime`; do not add `FUNCTIONS_WORKER_RUNTIME`. Keep `AzureWebJobs.cycle_planner_timer.Disabled=true` until the live integration gate passes.

## Runtime Key Vault secrets

Always required for read and dry-run processing:

- `brightlayer-service-account-id`
- `brightlayer-service-account-secret`
- `brightlayer-api-prefix`
- `aggregation-kpi-map`

Required only when `WRITEBACK_MODE=enabled`:

- `brightlayer-aggregate-device-config`
- `brightlayer-writeback-credentials`

Organization ID is an onboarding/device-discovery input, not a per-cycle runtime dependency. API request pairs are derived from `aggregation-kpi-map`; separate source device and trait list secrets are no longer used.

With `WRITEBACK_MODE=dry_run`, the worker does not read aggregate-device secrets, create an IoT client, or send telemetry. It persists coverage, calculated KPI results, and the candidate KPI payload to `CycleAudit` and emits a secret-free Application Insights summary.

## Nam5 read-only characterization

The temporary one-device map is [config/nam5-single-device-kpi-map.json](config/nam5-single-device-kpi-map.json). Gateway `165_Evale` (`cb118f9e-3a25-4e1f-8f37-f9a37c48c1cb`) is relationship metadata; timeseries requests use child `Nam5` (`8a7f416d-a452-2b11-0800-1e0d06362200`).

The API expects whole-second UTC timestamps ending in `Z`. Website exports use timestamps with an offset, so convert them before querying: `2026-09-01T14:00:00+02:00` is `2026-09-01T12:00:00Z`. Use the supplied PowerShell runner for this conversion; do not manually subtract hours.

For a direct, saved API report, use [scripts/run_brightlayer_probe.ps1](scripts/run_brightlayer_probe.ps1). It prompts for the secret without echoing it, converts local offset timestamps to UTC, runs the Python probe as a separate command, prints the JSON report, and saves it when `-OutputPath` is supplied:

```powershell
.\Namibia\azure_aggregation\scripts\run_brightlayer_probe.ps1 `
	-DeviceId '8a7f416d-a452-2b11-0800-1e0d06362200' `
	-TraitIds '10549363' `
	-StartLocal '2026-09-01T14:00:00+02:00' `
	-EndLocal '2026-09-01T15:10:00+02:00' `
	-OutputPath '.\Namibia\azure_aggregation\reports\nam5-ph-input.json'
```

The request sent by this example is `2026-09-01T12:00:00Z` through `2026-09-01T13:10:00Z`. The saved report contains the measurements at `timeseriesResponse.timeSeries[*].results.values`.

Set credentials directly in your local terminal process; do not put them in files or command history maintained by automation. Then run:

```powershell
$env:BRIGHTLAYER_SERVICE_ACCOUNT_ID = Read-Host "Brightlayer service account ID"
$env:BRIGHTLAYER_SERVICE_ACCOUNT_SECRET = Read-Host "Brightlayer service account secret"
c:/Users/AlexandraCabral/Documents/Eaton_PLC/BrightLayer/.venv/Scripts/python.exe Namibia/azure_aggregation/scripts/probe_brightlayer_device.py
Remove-Item Env:BRIGHTLAYER_SERVICE_ACCOUNT_ID, Env:BRIGHTLAYER_SERVICE_ACCOUNT_SECRET
```

The default probe performs device discovery and one three-pair timeseries read. Trend channels do not use the realtime endpoint. It performs no writes and never prints credentials or the bearer token.

For the fastest connectivity check, set `BRIGHTLAYER_PROBE_QUICK=1`. Quick mode skips discovery and realtime, then requests only the first registered tag from the child device over a 15-minute timeseries window.

To test an exact device and interval using Eaton's documented API contract, set all four targeted inputs before running the same script:

```powershell
$env:BRIGHTLAYER_PROBE_DEVICE_ID = "8a7f416d-a452-2b11-0800-1e0d06362200"
$env:BRIGHTLAYER_PROBE_TRAIT_IDS = "10549363,10549365"
$env:BRIGHTLAYER_PROBE_START_UTC = "2026-09-01T00:00:00Z"
$env:BRIGHTLAYER_PROBE_END_UTC = "2026-09-01T12:00:00Z"
c:/Users/AlexandraCabral/Documents/Eaton_PLC/BrightLayer/.venv/Scripts/python.exe Namibia/azure_aggregation/scripts/probe_brightlayer_device.py
Remove-Item Env:BRIGHTLAYER_PROBE_DEVICE_ID, Env:BRIGHTLAYER_PROBE_TRAIT_IDS, Env:BRIGHTLAYER_PROBE_START_UTC, Env:BRIGHTLAYER_PROBE_END_UTC
```

`BRIGHTLAYER_PROBE_TRAIT_IDS` must contain numeric ontology `tagId` values. Do not substitute the channel UUIDs used by the browser dashboard's internal BSS API.

## Validation

From the workspace root:

```powershell
c:/Users/AlexandraCabral/Documents/Eaton_PLC/BrightLayer/.venv/Scripts/python.exe -m pytest Namibia/azure_aggregation/tests -q
az bicep build --file Namibia/azure_aggregation/infra/main.bicep --stdout
./Namibia/azure_aggregation/scripts/build_function_package.ps1 -PythonPath c:/Users/AlexandraCabral/Documents/Eaton_PLC/BrightLayer/.venv/Scripts/python.exe
```

## Deployment

The GitHub Actions workflow at `/.github/workflows/namibia-aggregation.yml` tests and builds one deterministic artifact. Development deployment is manual through `workflow_dispatch` with `deploy=true` and the client ID of a GitHub OIDC federated Azure application.

Do not deploy temporary hand-built ZIPs. Do not enable the scheduler until Key Vault, source IDs, aggregate-device mapping, read-only Brightlayer characterization, and controlled writeback tests pass.
