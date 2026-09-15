# BrightLayer Project Guidelines

## Scope

These instructions apply to the BrightLayer workspace, especially the Namibia aggregation project in `applications/namibia-aggregation/azure_aggregation`.

## Safety

- Never print, persist, or commit Brightlayer secrets, bearer tokens, SAS tokens, connection strings, storage account keys, or Key Vault secret values.
- It is acceptable to list secret names, app setting names, resource names, and non-secret Azure metadata.
- Do not enable `AzureWebJobs.cycle_planner_timer.Disabled=false` unless the user explicitly approves scheduler enablement.
- Do not set `WRITEBACK_MODE=enabled` unless the user explicitly approves writeback.
- Keep dry-run validation separate from production writeback.

## Brightlayer Rules

- Use child device IDs for telemetry timeseries reads. Gateway IDs are relationship metadata.
- Use whole-second UTC timestamps ending in `Z` for Brightlayer API requests.
- Website timestamps with offsets must be converted to UTC by parsing the offset, not by manually subtracting hours.
- Trend channels use the `timeseries` endpoint, not `realtime`, unless explicitly doing diagnostics.
- Do not impose undocumented request-pair limits.

## Current Namibia State

- Project root: `applications/namibia-aggregation/azure_aggregation`.
- Deployment plan: `.azure/deployment-plan.md`.
- Current known child devices: Nam5, Nam1, and 164_Oluundje.
- Current characterization map: `applications/namibia-aggregation/azure_aggregation/config/nam5-single-device-kpi-map.json`.
- Current expected characterization shape: 12 KPIs and 36 unique device/tag source pairs.
- Production target: 15 machines and 180 unique source pairs.
- Five-minute cycles use `FETCH_OVERLAP_MINUTES=15` for delayed Brightlayer updates.
- Carry-forward preserves the original measurement timestamp and quality metadata. Zero-fill is forbidden.

## Azure Rules

- Target subscription: `47b9cfe5-6ca3-4ad4-a4ca-d870926688b0`.
- Target resource group: `rg-brightlayer-dev`.
- Function App: `brightlayer-func-dev-001`.
- Key Vault: `brightlayerkvdev001`.
- Storage account: `rgbrightlayerdevb112`.
- Required queue: `aggregation-cycles`.
- Required tables: `CycleStatus`, `CycleDataSnapshot`, `CycleAudit`, `LatestObservation`.
- Python Azure Functions Flex Consumption owns runtime via `functionAppConfig`; do not add `FUNCTIONS_WORKER_RUNTIME` to deployed app settings.

## Validation

Before deployment-related changes, prefer these checks from the workspace root:

```powershell
c:/Users/AlexandraCabral/Documents/Eaton_PLC/BrightLayer/.venv/Scripts/python.exe -m pytest applications/namibia-aggregation/azure_aggregation/tests -q
az bicep build --file applications/namibia-aggregation/azure_aggregation/infra/main.bicep --stdout
./applications/namibia-aggregation/azure_aggregation/scripts/build_function_package.ps1 -PythonPath c:/Users/AlexandraCabral/Documents/Eaton_PLC/BrightLayer/.venv/Scripts/python.exe
```

After Azure deployment, verify function indexing, safety settings, queue/table resources, and one dry-run cycle before any scheduler or writeback enablement.
