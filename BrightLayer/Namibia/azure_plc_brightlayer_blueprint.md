# Azure Aggregation and Brightlayer Writeback Implementation Blueprint

## Purpose

This document is the implementation plan for Namibia aggregated KPIs.

Confirmed production flow:

1. PLC/Codesys runtime publishes device telemetry to Brightlayer over MQTT.
2. Azure services fetch source telemetry from Brightlayer.
3. Azure computes fleet-level aggregate KPIs every 5 minutes.
4. Azure publishes aggregate KPI values back to Brightlayer using the same ingestion method used for device telemetry, but targeting a dedicated aggregate virtual device.
5. Brightlayer shows historical trends for the aggregate virtual device.

This blueprint defines what to build and how to deploy it. It does not implement code.

## Scope and Boundaries

In scope:

- Azure retrieval, orchestration, aggregation, and writeback pipeline.
- Brightlayer aggregate virtual device setup and ontology mapping requirements.
- Reliability, retry, security, and observability controls.

Out of scope:

- Changing PLC/Codesys runtime telemetry behavior.
- Redesigning existing source device ontology.
- Implementing control-channel commands.

## Confirmed API and Integration Constraints

Brightlayer APIs confirmed from the provided documentation:

- Token: POST /api/v1/auth/serviceaccount/token
- Realtime read: POST /api/v1/dashboard/devices/{deviceId}/realtime
- Timeseries read: POST /api/v1/dashboard/devices/timeseries
- Device lookup: GET /api/v1/dashboard/organization/{organizationId}/devices

Writeback method confirmed by project decision:

- Use the same Brightlayer ingestion method used for device-related telemetry.
- Create a dedicated aggregate virtual device, for example Aggregated_Namibia.
- Map aggregated KPI channels in that device ontology and publish values to those mapped traits.

## Target Architecture

### Logical components

- Brightlayer source devices
  - Existing PLC/Codesys-fed devices with per-site telemetry traits.
- Brightlayer aggregate virtual device
  - Dedicated telemetry destination for computed KPIs.
- Azure Function App
  - Fetch, orchestrate, aggregate, and publish.
- Azure Storage Account (Table Storage)
  - Short-lived cycle and execution state.
- Azure Key Vault
  - Secrets and static config values.
- Application Insights
  - Logs, traces, metrics, and alerting.

### High-level data flow

1. Timer trigger starts cycle processing every minute.
2. Function determines which 5-minute cycles are eligible for processing.
3. Function reads required source traits for cycle time window from Brightlayer.
4. Function verifies completeness policy (strict or partial).
5. Function computes configured KPIs.
6. Function publishes aggregate KPI points to aggregate virtual device via Brightlayer ingestion path.
7. Function marks cycle status and stores audit metadata.
8. Cleanup function removes stale temporary state.

## Brightlayer Device and Ontology Design

### Aggregate virtual device

Create one device for fleet aggregates, for example:

- Device name: Aggregated_Namibia
- Device identity: unique GUID/device identifier
- Credentials: unique credentials/token inputs matching your Brightlayer ingestion mechanism

### Ontology mapping requirements

For each aggregate KPI, define and freeze:

- KPI name
- Brightlayer trait/tag identifier
- Unit
- Data type (number, boolean, integer)
- Precision and rounding policy
- Nullable behavior

Example mapping artifact:

```json
{
  "aggregateDeviceName": "Aggregated_Namibia",
  "kpis": [
    {
      "name": "total_flow",
      "sourceField": "flow",
      "operation": "sum",
      "brightlayerTagId": "10462371",
      "unit": "m3/h",
      "precision": 2
    },
    {
      "name": "avg_pressure",
      "sourceField": "pressure",
      "operation": "avg",
      "brightlayerTagId": "10462372",
      "unit": "bar",
      "precision": 2
    },
    {
      "name": "total_energy",
      "sourceField": "energy",
      "operation": "sum",
      "brightlayerTagId": "10415480",
      "unit": "kWh",
      "precision": 3
    }
  ]
}
```

## Azure Services and Configuration

### 1. Resource group

- Name example: rg-namibia-aggregation-prod
- Keep all services in one region.

### 2. Storage account and tables

Create one general-purpose v2 account with public access disabled.

Tables:

- CycleStatus
- CycleDataSnapshot
- CycleAudit (optional but recommended)

CycleStatus schema:

- PartitionKey: cycleStartUtc
- RowKey: aggregate
- expectedCount
- receivedCount
- status: open, ready, processing, sent, failed, expired
- graceDeadlineUtc
- retryCount
- lockOwner
- lockExpiresUtc
- lastError
- lastUpdatedUtc

CycleDataSnapshot schema (ephemeral normalized source values):

- PartitionKey: cycleStartUtc
- RowKey: sourceDeviceId + traitId
- value
- unit
- timestampUtc
- quality

CycleAudit schema:

- PartitionKey: cycleDate (YYYY-MM-DD)
- RowKey: cycleStartUtc + runId
- durationMs
- sourcePointsRead
- aggregatePointsWritten
- outcome
- errorSummary

### 3. Key Vault

Store:

- brightlayer-service-account-id
- brightlayer-service-account-secret
- brightlayer-api-prefix
- brightlayer-organization-id
- brightlayer-source-device-list (JSON)
- brightlayer-source-trait-list (JSON)
- brightlayer-aggregate-device-config (JSON)
- brightlayer-writeback-credentials (or references required by your ingestion method)
- aggregation-kpi-map (JSON)

Grant Function managed identity:

- Key Vault Secrets User

### 4. Function App

Recommended:

- Runtime: Python 3.11 or Node.js 20 LTS
- Hosting: Consumption plan
- Managed identity: enabled
- Application Insights: enabled

Suggested app settings:

- EXPECTED_PLC_COUNT=15
- CYCLE_INTERVAL_MINUTES=5
- CYCLE_GRACE_SECONDS=90
- AGGREGATION_MODE=strict
- MAX_RETRIES=3
- RETRY_BASE_SECONDS=10
- CYCLE_TABLE_STATUS=CycleStatus
- CYCLE_TABLE_SNAPSHOT=CycleDataSnapshot
- CYCLE_TABLE_AUDIT=CycleAudit
- RETENTION_HOURS=12

## Functional Modules

### Module A: cyclePlannerTimer

Trigger:

- Every minute

Responsibility:

- Determine candidate cycle keys.
- Create/open CycleStatus rows if missing.
- Dispatch candidate cycles to processing.

### Module B: fetchSourceTelemetry

Trigger:

- Internal call from cycle planner or queue

Responsibility:

1. Authenticate using service account token.
2. Resolve source devices from config and optional device lookup API.
3. Pull required traits from Brightlayer using timeseries API for cycle window.
4. Normalize payload into CycleDataSnapshot.
5. Update receivedCount and cycle readiness.

Notes:

- Prefer timeseries API for aligned cycle windows.
- Use realtime API only for diagnostics or fallback.

### Module C: aggregateCycle

Trigger:

- Internal call once cycle is ready or grace deadline has passed

Responsibility:

1. Acquire optimistic lock using ETag or equivalent concurrency guard.
2. Enforce strict or partial mode.
3. Compute KPI formulas from snapshot data.
4. Apply unit checks and precision policy.
5. Emit aggregate payload for writeback.

### Module D: writebackToBrightlayer

Trigger:

- Internal call from aggregateCycle

Responsibility:

1. Build telemetry payload in the same format/path used for normal Brightlayer device ingestion.
2. Target aggregate virtual device identity and mapped ontology traits.
3. Publish data points with cycle-aligned timestamp.
4. Confirm publish acknowledgment where available.
5. Mark cycle sent on success.

### Module E: retryAndDeadLetter

Trigger:

- Internal policy during failures

Responsibility:

- Retry transient errors up to MAX_RETRIES with exponential backoff.
- Persist terminal failure in CycleStatus and CycleAudit.
- Raise alert for repeated failures.

### Module F: cleanupTimer

Trigger:

- Every 6 hours

Responsibility:

- Delete CycleDataSnapshot and CycleStatus older than retention.
- Keep only minimal audit records needed for troubleshooting.

## Cycle and Time Semantics

- All timestamps in UTC.
- Cycle boundary is exact 5-minute floor.
- Preferred cycle key format: YYYY-MM-DDTHH:mm:00Z.
- Writeback timestamp equals cycleStartUtc or cycleEndUtc, selected once and kept consistent.

Recommended helper definitions:

- cycleStartUtc = floor(nowUtc, 5 minutes)
- cycleEndUtc = cycleStartUtc + 5 minutes
- graceDeadlineUtc = cycleEndUtc + CYCLE_GRACE_SECONDS

## Aggregation Rules and Data Quality

### Strict mode (default)

- Require all expected source PLC/device contributions before send.
- If incomplete at grace deadline, mark expired or failed and do not publish.

### Partial mode

- Publish with available values after deadline.
- Attach quality metadata in CycleAudit.
- Optionally publish completeness percentage as a separate trait.

### Validation

- Reject non-numeric values for numeric KPIs.
- Track missing trait counts per cycle.
- Guard division by zero for averages.
- Enforce allowed ranges if known.

## Idempotency and Concurrency

Controls required:

- One active processor per cycle via optimistic lock.
- Deterministic runId per cycle attempt.
- Safe re-run behavior: duplicate execution must not create duplicate trend points for same cycle and trait.
- Status transitions must be monotonic:
  - open -> ready -> processing -> sent
  - open/ready/processing -> failed/expired

## Security and Access

- Managed identity for Key Vault reads.
- No secrets in code or repo files.
- Rotate service-account secret and writeback credentials.
- TLS-only outbound calls.
- Restrict Function outbound networking if enterprise policy requires it.

## Observability and Alerting

Track per cycle:

- cycleStartUtc
- sourcePointsRead
- missingPoints
- aggregationDurationMs
- writebackDurationMs
- retryCount
- terminal status

Recommended alerts:

- Consecutive failed cycles >= 3
- No sent cycles in 30 minutes
- Token failures spike
- Completeness below threshold in partial mode

## Deployment Plan (No Code Implementation Yet)

### Phase 1: Design freeze

1. Freeze KPI list, units, precision, and mapping.
2. Freeze aggregate virtual device ontology traits.
3. Freeze cycle policy (strict or partial).

### Phase 2: Platform provisioning

1. Create Azure resource group.
2. Create Storage account and tables.
3. Create Key Vault and populate secrets/config.
4. Create Function App and enable managed identity.
5. Wire Application Insights and alert rules.

### Phase 3: Brightlayer setup

1. Create aggregate virtual device (Aggregated_Namibia).
2. Configure unique identity/credentials for ingestion path.
3. Map ontology traits for all aggregate KPIs.
4. Validate manual test publish to one trait.

### Phase 4: Pipeline implementation readiness

1. Prepare function/module skeletons per this blueprint.
2. Define config files and secret references.
3. Define test vectors for normal and failure cycles.

### Phase 5: End-to-end validation

1. Simulate one full 15-device cycle.
2. Verify aggregate values are correct.
3. Verify historical trend points appear on aggregate device.
4. Verify retry behavior and alerting.

### Phase 6: Production rollout

1. Deploy to dev.
2. Run soak test for at least 48 hours.
3. Promote to prod with same config structure.
4. Keep rollback plan ready.

## Python-style Pseudocode (Blueprint Only)

These snippets are intentionally non-runnable and serve as implementation guidance only.

### Shared helpers

```python
from datetime import datetime, timedelta, timezone

def floor_to_5min(ts_utc: datetime) -> datetime:
  minute = (ts_utc.minute // 5) * 5
  return ts_utc.replace(minute=minute, second=0, microsecond=0)

def cycle_bounds(now_utc: datetime, grace_seconds: int):
  cycle_start = floor_to_5min(now_utc)
  cycle_end = cycle_start + timedelta(minutes=5)
  grace_deadline = cycle_end + timedelta(seconds=grace_seconds)
  return cycle_start, cycle_end, grace_deadline

def cycle_key(dt_utc: datetime) -> str:
  return dt_utc.strftime("%Y-%m-%dT%H:%M:00Z")
```

### Module A: cyclePlannerTimer

```python
def cycle_planner_timer(now_utc):
  cycle_start, cycle_end, grace_deadline = cycle_bounds(now_utc, CYCLE_GRACE_SECONDS)
  key = cycle_key(cycle_start)

  status = get_or_create_cycle_status(key)
  status.expectedCount = EXPECTED_PLC_COUNT
  status.graceDeadlineUtc = grace_deadline.isoformat().replace("+00:00", "Z")
  status.lastUpdatedUtc = now_utc.isoformat().replace("+00:00", "Z")
  save_status(status)

  dispatch_fetch_for_cycle(key, cycle_start, cycle_end)
```

### Module B: fetchSourceTelemetry

```python
def fetch_source_telemetry(cycle_key, cycle_start, cycle_end):
  token = get_brightlayer_token()
  source_devices = load_source_device_config()  # list of device IDs
  source_traits = load_source_trait_config()    # list of tag traits per KPI input

  records = query_brightlayer_timeseries(
    token=token,
    devices=source_devices,
    traits=source_traits,
    start_utc=cycle_start,
    end_utc=cycle_end,
  )

  snapshot_rows = normalize_timeseries_records(records, cycle_key)
  upsert_cycle_snapshot_rows(snapshot_rows)

  status = get_cycle_status(cycle_key)
  status.receivedCount = count_distinct_source_contributors(cycle_key)
  status.status = "ready" if status.receivedCount >= status.expectedCount else "open"
  status.lastUpdatedUtc = utcnow_iso()
  save_status(status)
```

### Module C: aggregateCycle

```python
def aggregate_cycle(cycle_key, now_utc):
  status = get_cycle_status(cycle_key)
  if not try_acquire_cycle_lock(status):
    return

  is_complete = status.receivedCount >= status.expectedCount
  is_past_deadline = now_utc >= parse_utc(status.graceDeadlineUtc)

  if AGGREGATION_MODE == "strict" and (not is_complete) and is_past_deadline:
    mark_cycle_expired(cycle_key, reason="incomplete_strict_mode")
    release_cycle_lock(cycle_key)
    return

  if (not is_complete) and (not is_past_deadline):
    release_cycle_lock(cycle_key)
    return

  rows = list_cycle_snapshot_rows(cycle_key)
  kpi_map = load_kpi_map()

  aggregates = []
  for kpi in kpi_map["kpis"]:
    values = extract_numeric_values(rows, kpi["sourceField"])
    value = compute_operation(values, kpi["operation"])  # sum, avg, min, max
    value = apply_precision(value, kpi.get("precision", 3))
    aggregates.append({
      "name": kpi["name"],
      "tagId": kpi["brightlayerTagId"],
      "value": value,
      "unit": kpi["unit"],
    })

  dispatch_writeback(cycle_key, aggregates)
```

### Module D: writebackToBrightlayer

```python
def writeback_to_brightlayer(cycle_key, aggregates):
  token = get_brightlayer_token()
  aggregate_device = load_aggregate_device_config()

  # Use same ingestion pattern as normal Brightlayer device telemetry,
  # but target the aggregate virtual device and mapped traits.
  payload = build_aggregate_ingestion_payload(
    device_id=aggregate_device["deviceId"],
    cycle_key=cycle_key,
    points=aggregates,
  )

  send_to_brightlayer_ingestion(token=token, payload=payload)

  mark_cycle_sent(cycle_key)
  write_cycle_audit(cycle_key, outcome="sent", aggregate_points=len(aggregates))
```

### Module E: retryAndDeadLetter

```python
def with_retry(cycle_key, action_name, fn):
  for attempt in range(1, MAX_RETRIES + 1):
    try:
      return fn()
    except TransientError as ex:
      if attempt == MAX_RETRIES:
        break
      backoff_seconds = RETRY_BASE_SECONDS * (2 ** (attempt - 1))
      schedule_retry(cycle_key, action_name, delay_seconds=backoff_seconds)

  mark_cycle_failed(cycle_key, last_error=f"{action_name}_failed_after_retries")
  write_cycle_audit(cycle_key, outcome="failed", error_summary=action_name)
  emit_alert("cycle_failed", cycle_key)
```

### Module F: cleanupTimer

```python
def cleanup_timer(now_utc):
  cutoff = now_utc - timedelta(hours=RETENTION_HOURS)
  delete_snapshot_older_than(cutoff)
  delete_status_older_than(cutoff, terminal_states=["sent", "failed", "expired"])
  trim_audit_older_than(cutoff)
```

## Azure-specific Service Configuration and Code Scaffolding

This section defines concrete Azure configuration and code scaffolding templates to use during implementation. These are templates only.

### Recommended repo structure for Azure implementation

```text
Namibia/
  azure_plc_brightlayer_blueprint.md
  azure_aggregation/
    infra/
      main.bicep
      parameters.dev.json
      parameters.prod.json
    src/
      function_app.py
      host.json
      local.settings.example.json
      requirements.txt
      shared/
        config.py
        brightlayer_client.py
        storage_cycle_repo.py
        telemetry_normalizer.py
        aggregations.py
        retry_policy.py
        observability.py
      modules/
        cycle_planner.py
        fetch_source_telemetry.py
        aggregate_cycle.py
        writeback_to_brightlayer.py
        cleanup_cycles.py
    tests/
      test_aggregations.py
      test_cycle_semantics.py
      test_idempotency.py
```

### Infrastructure as Code template (Bicep)

```bicep
param location string = resourceGroup().location
param environment string
param storageName string
param functionAppName string
param appInsightsName string
param keyVaultName string
param planName string

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
  }
}

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  kind: 'functionapp'
}

resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      appSettings: [
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'AzureWebJobsStorage'
          value: 'Use managed identity or connection setting during deployment'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
      ]
    }
  }
}
```

### Required Table Storage initialization

Create these tables during provisioning or first-run bootstrap:

- CycleStatus
- CycleDataSnapshot
- CycleAudit

Example bootstrap pseudocode:

```python
def ensure_tables(table_service_client):
  for name in ["CycleStatus", "CycleDataSnapshot", "CycleAudit"]:
    table_service_client.create_table_if_not_exists(name)
```

### Function runtime configuration templates

host.json template:

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  },
  "functionTimeout": "00:10:00"
}
```

local.settings.example.json template (do not commit secrets):

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "EXPECTED_PLC_COUNT": "15",
    "CYCLE_INTERVAL_MINUTES": "5",
    "CYCLE_GRACE_SECONDS": "90",
    "AGGREGATION_MODE": "strict",
    "MAX_RETRIES": "3",
    "RETRY_BASE_SECONDS": "10",
    "CYCLE_TABLE_STATUS": "CycleStatus",
    "CYCLE_TABLE_SNAPSHOT": "CycleDataSnapshot",
    "CYCLE_TABLE_AUDIT": "CycleAudit",
    "RETENTION_HOURS": "12",
    "KEYVAULT_URI": "https://<your-kv>.vault.azure.net/"
  }
}
```

requirements.txt template:

```text
azure-functions
azure-identity
azure-keyvault-secrets
azure-data-tables
requests
pydantic
tenacity
```

### Suggested Function App entry points (Python v2 model)

```python
import azure.functions as func

app = func.FunctionApp()

@app.timer_trigger(schedule="0 */1 * * * *", arg_name="timer")
def cycle_planner_timer(timer: func.TimerRequest) -> None:
  pass

@app.queue_trigger(arg_name="msg", queue_name="fetch-cycle")
def fetch_source_telemetry(msg: func.QueueMessage) -> None:
  pass

@app.queue_trigger(arg_name="msg", queue_name="aggregate-cycle")
def aggregate_cycle(msg: func.QueueMessage) -> None:
  pass

@app.queue_trigger(arg_name="msg", queue_name="writeback-cycle")
def writeback_to_brightlayer(msg: func.QueueMessage) -> None:
  pass

@app.timer_trigger(schedule="0 0 */6 * * *", arg_name="timer")
def cleanup_cycles(timer: func.TimerRequest) -> None:
  pass
```

### Key Vault secret naming contract

Use stable names to avoid environment-specific code branching:

- brightlayer-service-account-id
- brightlayer-service-account-secret
- brightlayer-api-prefix
- brightlayer-organization-id
- brightlayer-source-device-list
- brightlayer-source-trait-list
- brightlayer-aggregate-device-config
- brightlayer-writeback-credentials
- aggregation-kpi-map

### App settings contract and parsing rules

- Parse all numeric settings as integers at startup.
- Fail fast when required settings are missing.
- Log effective non-secret configuration at startup.
- Cache Key Vault secrets with TTL to reduce round trips.

Example loader pseudocode:

```python
def load_runtime_config(env):
  return {
    "expected_count": int(env["EXPECTED_PLC_COUNT"]),
    "cycle_interval_minutes": int(env["CYCLE_INTERVAL_MINUTES"]),
    "grace_seconds": int(env["CYCLE_GRACE_SECONDS"]),
    "mode": env["AGGREGATION_MODE"],
    "max_retries": int(env["MAX_RETRIES"]),
    "retry_base_seconds": int(env["RETRY_BASE_SECONDS"]),
  }
```

### Storage concurrency and lock update template

Use ETag-based conditional updates for lock-safe status transitions.

```python
def try_mark_processing(entity):
  if entity["status"] not in ["open", "ready"]:
    return False

  entity["status"] = "processing"
  entity["lockOwner"] = current_worker_id()
  entity["lockExpiresUtc"] = utcnow_plus_minutes(3)

  # if_match must use the current ETag from the prior read
  update_entity_with_if_match(entity)
  return True
```

### Queue contracts between modules

fetch-cycle message:

```json
{
  "cycleKey": "2026-07-30T10:15:00Z",
  "cycleStartUtc": "2026-07-30T10:15:00Z",
  "cycleEndUtc": "2026-07-30T10:20:00Z"
}
```

aggregate-cycle message:

```json
{
  "cycleKey": "2026-07-30T10:15:00Z",
  "attempt": 1
}
```

writeback-cycle message:

```json
{
  "cycleKey": "2026-07-30T10:15:00Z",
  "pointCount": 3,
  "quality": "complete"
}
```

### Observability implementation templates

Log envelope for every module:

```json
{
  "module": "aggregate_cycle",
  "cycleKey": "2026-07-30T10:15:00Z",
  "runId": "<guid>",
  "attempt": 1,
  "status": "processing"
}
```

Suggested custom metrics:

- cycle.duration.ms
- cycle.source.points.read
- cycle.aggregate.points.written
- cycle.missing.points
- cycle.retry.count

### CI/CD pipeline requirements

Minimum deployment pipeline stages:

1. Lint and unit tests.
2. Package Function App artifact.
3. Deploy Bicep to target environment.
4. Deploy Function App package.
5. Run smoke test for one synthetic cycle.

Minimum gates:

- Block production if smoke test fails.
- Block production if required Key Vault secrets are missing.
- Block production if table initialization check fails.

### Azure RBAC matrix

- Function managed identity -> Key Vault Secrets User
- Function managed identity -> Storage Table Data Contributor
- Deployment principal -> Contributor on resource group
- Monitoring operator group -> Monitoring Reader

## Acceptance Criteria

The implementation is considered functional when all conditions are true:

1. Azure processes each 5-minute cycle deterministically.
2. Aggregated KPI values are published to aggregate virtual device using the confirmed ingestion method.
3. Brightlayer displays the aggregate KPI history in trend widgets.
4. Duplicate execution does not corrupt historical points.
5. Failures are visible in Application Insights and alerts fire correctly.
6. Temporary Azure orchestration state is cleaned up within configured retention.

## Implementation Checklist

- [ ] KPI and ontology mapping approved
- [ ] Aggregate virtual device created and reachable
- [ ] Secrets loaded in Key Vault
- [ ] Storage tables created
- [ ] Function App configured with managed identity
- [ ] Cycle planner, fetch, aggregate, writeback, cleanup modules defined
- [ ] Retry and lock logic defined
- [ ] Monitoring and alerts configured
- [ ] End-to-end validation plan approved
- [ ] Go-live checklist approved

## Notes for Developers

- Keep Brightlayer integration behind a single adapter layer, for example send_to_brightlayer_ingestion(), so credential or payload changes remain isolated.
- Keep formula definitions in configuration, not hardcoded in fetch/writeback logic.
- Always log cycle ID, device count, and trait count for each run.
