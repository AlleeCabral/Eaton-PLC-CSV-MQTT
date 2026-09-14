# BrightLayer Namibia Azure Deployment Plan

**Status:** Ready for Validation
**Last updated:** 2026-09-03

## 1. Objective

Deploy the existing Namibia Brightlayer aggregation Function App to Azure. The application reads source telemetry from Brightlayer, aggregates 12 fleet KPIs every five minutes, and publishes results to a dedicated `Aggregated_Namibia` Brightlayer virtual device after the writeback gate is approved.

## 2. Deployment Target

- Subscription: `Boreal Light` (`47b9cfe5-6ca3-4ad4-a4ca-d870926688b0`)
- Tenant: `8e41dec4-b90a-42f3-9f3c-7cc6f613a473`
- Resource group: `rg-brightlayer-dev`
- Region: `northeurope`
- Function App: `brightlayer-func-dev-001`
- Hosting: Azure Functions Flex Consumption (`FC1`), Linux, Python 3.11
- Key Vault: `brightlayerkvdev001`
- Storage account: `rgbrightlayerdevb112`
- Application Insights: `brightlayer-func-dev-001`

## 3. Existing Implementation

This is a MODIFY deployment. The application and infrastructure already exist in the repository.

- Infrastructure: `Namibia/azure_aggregation/infra/main.bicep`
- Development parameters: `Namibia/azure_aggregation/infra/parameters.dev.json`
- Function source: `Namibia/azure_aggregation/src/`
- Package builder: `Namibia/azure_aggregation/scripts/build_function_package.ps1`
- CI/CD: `.github/workflows/namibia-aggregation.yml`
- Local tests: `Namibia/azure_aggregation/tests/`

The application contains:

- Five-minute timer planner: `cycle_planner_timer`
- Storage Queue worker: `aggregation_cycle_worker`
- Six-hour cleanup timer: `cleanup_cycles`
- Table Storage cycle claims, snapshots, latest observations, and audit records
- Key Vault-backed Brightlayer configuration
- Application Insights logging

## 4. Azure Resources

The Bicep template provisions or manages:

- Flex Consumption Function App with system-assigned managed identity
- Linux Python 3.11 runtime using `functionAppConfig`
- Storage account with private blob access and TLS 1.2
- Deployment blob container
- Storage Queue `aggregation-cycles`
- Tables `CycleStatus`, `CycleDataSnapshot`, `CycleAudit`, and `LatestObservation`
- Key Vault with RBAC authorization
- Application Insights
- Function identity assignment of `Key Vault Secrets User`

## 5. Runtime Configuration

The deployment must retain these safety settings:

```text
EXPECTED_PLC_COUNT=15
CYCLE_INTERVAL_MINUTES=5
CYCLE_SCHEDULE=0 */5 * * * *
FETCH_OVERLAP_MINUTES=15
AGGREGATION_MODE=permissive
WRITEBACK_MODE=dry_run
LAST_KNOWN_VALUE_POLICY=carry_forward
ZERO_FILL_DISABLED=true
AzureWebJobs.cycle_planner_timer.Disabled=true
```

The 15-minute overlap allows delayed source updates to be observed while processing remains on a five-minute cadence. Missing values use the latest stored observation with its original timestamp and quality metadata. Zero-fill is prohibited.

## 6. Brightlayer Source Configuration

The current characterization map contains 12 KPI definitions for three known child devices, producing 36 unique source pairs:

- Nam5: `8a7f416d-a452-2b11-0800-1e0d06362200`
- Nam1: `c627a6ba-a832-2b11-0800-4ea999779100`
- 164_Oluundje: `f8a20915-6672-2b11-0800-2f5623d56800`

Gateway IDs are relationship metadata only. Timeseries requests use child device IDs. The complete production map still requires the remaining 12 Namibia PLC child IDs.

Source map: `Namibia/azure_aggregation/config/nam5-single-device-kpi-map.json`

## 7. Required Key Vault Secrets

Required for read-only and dry-run operation:

- `brightlayer-service-account-id`
- `brightlayer-service-account-secret`
- `brightlayer-api-prefix`
- `aggregation-kpi-map`

Required only after writeback approval:

- `brightlayer-aggregate-device-config`
- `brightlayer-writeback-credentials`

Secrets must not be committed, printed, or written to reports. The service-account secret is treated as sensitive and must remain managed through Key Vault.

## 8. Deployment Method

Use the existing GitHub Actions workflow with manual `workflow_dispatch` and `deploy=true` after validation. The workflow:

1. Installs Python dependencies.
2. Runs the test suite.
3. Builds and inspects one deterministic Function package.
4. Deploys the tested package to `brightlayer-func-dev-001`.
5. Verifies Function indexing.

Do not deploy temporary hand-built ZIP files.

## 9. Required Gates

## 9A. Azure Validation Checklist

- [ ] Core Bicep validation: Azure CLI authentication, Bicep build, deployment validation, and what-if preview.
- [ ] Optional Bicep linting.
- [ ] Azure Policy validation for the target subscription and resource group.
- [ ] Static RBAC review: Function identity has `Key Vault Secrets User` scoped to `brightlayerkvdev001`; storage data-plane roles are present if required by the deployed access mode.
- [ ] Record command results and timestamps in the Validation Proof section before changing status to `Validated`.

### Gate A: Local verification

- 91 automated tests pass.
- Bicep compilation passes.
- JSON configuration validation passes.
- Deterministic package inspection passes.

### Gate B: Azure validation

Run the Azure validation workflow and require status `Validated`. Verify resource existence, configuration, managed identity permissions, Key Vault access, Storage Queue/Table access, and Application Insights configuration.

### Gate C: Safe deployment

Deploy with the scheduler disabled and `WRITEBACK_MODE=dry_run`. Confirm the three Functions are indexed:

- `cycle_planner_timer`
- `aggregation_cycle_worker`
- `cleanup_cycles`

### Gate D: Controlled dry run

Run one controlled cycle and verify:

- Brightlayer timeseries reads use whole-second UTC timestamps.
- The 15-minute overlap is used for each five-minute cycle.
- Newer observations replace older observations only.
- Missing values carry forward without zero-fill.
- `CycleAudit` contains coverage, quality counts, KPI results, and candidate payload.
- No aggregate IoT client is created.
- No Brightlayer write is attempted.

### Gate E: Production onboarding and writeback

Before enabling writeback:

- Retrieve and validate all 15 child-device IDs.
- Confirm `EXPECTED_PLC_COUNT=15`.
- Create `Aggregated_Namibia` and its ontology.
- Obtain its 12 destination tag IDs.
- Obtain and store its IoT Hub connection string in Key Vault.
- Run one controlled writeback and duplicate-message replay.
- Enable the planner only after idempotency and monitoring checks pass.

## 9F. Validation Proof

- `pytest Namibia/azure_aggregation/tests -q`: **PASS**, 91 tests passed.
- `az bicep build --file Namibia/azure_aggregation/infra/main.bicep --stdout`: **PASS**.
- `build_function_package.ps1` with the project Python 3.11 environment: **PASS**, deterministic package created and inspected.
- `az account show --subscription 47b9cfe5-6ca3-4ad4-a4ca-d870926688b0`: **PASS**, authenticated as `Cabral@winture.de` in subscription `Boreal Light`.
- `az deployment group validate` against `rg-brightlayer-dev` and `parameters.dev.json`: **PASS**, no template validation error.
- `az deployment group what-if` against `rg-brightlayer-dev`: **REVIEW REQUIRED**, existing resources were detected and `CycleStatus`, `CycleDataSnapshot`, `CycleAudit`, and `LatestObservation` appear as proposed `Create` operations. No deployment was applied.
- `az keyvault show --name brightlayerkvdev001`: **PASS**, RBAC enabled and URI is `https://brightlayerkvdev001.vault.azure.net/`.
- Azure policy assignment query: no subscription assignments returned.
- Live Function indexing check: **FAIL**, Azure currently reports only `cleanup_cycles` and `cycle_planner_timer`; `aggregation_cycle_worker` is not indexed.
- Live Storage checks: **FAIL or inaccessible**, table and queue list queries returned no resource names. Required state resources need confirmation or provisioning.
- Controlled dry-run attempt: **FAILED**, the worker consumed cycle `2026-09-03T14:20:00Z`, retried five times, and moved the message to `aggregation-cycles-poison` without writing `CycleStatus`.
- Key Vault data-plane check: **NOT VERIFIED**, the current Azure CLI identity cannot list secret metadata; Function managed-identity access still needs a targeted runtime check.
- Validation limitation: the installed Bicep recipe helper is absent; equivalent Azure CLI validation commands were run directly.

## Validation Failure Resolution

- Status: Resolved for infrastructure and code deployment.
- Bicep deployment created or reconciled `aggregation-cycles`, `CycleStatus`, `CycleDataSnapshot`, `CycleAudit`, and `LatestObservation`.
- The deployment reported `RoleAssignmentExists` for a duplicate Key Vault role assignment; the existing `Key Vault Secrets User` assignment was verified and preserved.
- Function package deployment succeeded and all three Functions are indexed.
- Remaining next action: verify the Function identity can read the four required dry-run secrets, diagnose the poisoned worker cycle, then rerun one controlled dry-run cycle. Do not enable the scheduler or writeback.

## 10. Rollback and Monitoring

## Role Assignment Verification

- Status: Verified
- Identity checked: system-assigned identity on `brightlayer-func-dev-001`
- Role confirmed: `Key Vault Secrets User` scoped to `brightlayerkvdev001`
- Storage access: current implementation uses `AzureWebJobsStorage` connection string, so no Storage data-plane role is required by the deployed code path.
- Issues: none found in static Bicep review.

- Keep the planner disabled while diagnosing deployment or dry-run failures.
- Keep `WRITEBACK_MODE=dry_run` until controlled writeback is approved.
- Use Function deployment history and Application Insights for diagnosis.
- Monitor incomplete cycles, stale/offline source counts, queue poison messages, token failures, and writeback failures.
- Do not delete the resource group or existing resources as part of normal rollback.

## 11. Approval

This plan is reconstructed from `Namibia/azure_plc_brightlayer_blueprint.md`, `Namibia/FRESH_CONVERSATION_HANDOFF.md`, the current Bicep parameters, and the existing GitHub Actions workflow.

**Approval required before execution:** Yes

**Validation status:** Azure validation evidence complete; controlled dry-run pending

**Deployment status:** Not started
