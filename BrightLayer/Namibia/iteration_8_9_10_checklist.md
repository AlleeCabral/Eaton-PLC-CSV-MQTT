# Iterations 8-10 Checklist (combined) - Cleanup/Retention, Observability, Production Readiness

Combined into one pass (per user request to conserve credits — see session notes). Scope kept intentionally lean: implement real logic only where it branches meaningfully; skip individual gate-report ceremony per iteration.

## Iteration 8 - Cleanup and Retention

**Goal:** Purge CycleStatus/CycleDataSnapshot rows older than `RETENTION_HOURS` so tables don't grow unbounded.

- [x] `StorageCycleRepo.delete_old_cycles(cutoff_iso)` — queries both tables for `PartitionKey lt '{cutoff_iso}'` (safe because cycle keys are ISO-8601 strings, which sort lexically) and deletes matches; returns count deleted per table.
- [x] `modules/cleanup_cycles.py` — `run(now_utc, config, repo)` computes the cutoff from `RETENTION_HOURS` and calls the repo method for both tables.
- [x] Wired `function_app.py`'s existing `cleanup_cycles` timer (was a stub since Iteration 0) to call this for real, using the same `build_runtime_context` dependency wiring as `cycle_planner_timer`.
- Tests: cleanup logic has real branching (which rows are old enough to delete) — covered. Not tested: the timer wiring itself (same reasoning as Iteration 6/7 — Azure Functions bindings aren't unit-testable without the runtime).

## Iteration 9 - Observability and Alerting Hardening

**Goal:** Make failed/expired cycles visible in Application Insights as a distinct, filterable signal — not just a generic log line.

- [x] `shared/observability.py`: added `log_cycle_alert(logger, module, cycle_key, run_id, status, detail)` — logs at `ERROR` level with a structured envelope plus an explicit `"alert": true` field, so Application Insights queries/alert rules can filter on it distinctly from normal `INFO` cycle logs.
- [x] Wired into `function_app.py`: when `run_cycle_pipeline` returns `status == "failed"`, call `log_cycle_alert` instead of a plain `logging.info`.
- Not implemented (deliberately out of scope, needs live Azure resources to configure): an actual Azure Monitor **Action Group** / alert rule subscribed to this log pattern. The code now emits a distinctly-queryable signal; wiring an alert rule on top of it is an Azure Portal/Bicep configuration task for whoever operates the deployed resource, not application code.
- No new tests — this is a single log-call wrapper with no branching logic worth a dedicated unit test beyond what's already implied by `test_orchestrator.py`'s failure-path tests.

## Iteration 10 - Production Readiness and Rollout

**Goal:** A single source of truth for "is this safe to actually turn on in production", consolidating every gap tracked across Iterations 0-9.

- [x] No new code — this iteration is a checklist/documentation pass by nature (per `iteration_memory.md`'s own definition: "Production readiness and rollout").
- [x] Rollout checklist below supersedes needing to cross-reference all 9 prior iteration_N_checklist.md files individually for a go/no-go decision.

### Go-live checklist (must all be true before enabling the timer trigger in production)

- [ ] All secrets in `REQUIRED_SECRET_KEYS` exist and are correct in `kv-namibia-agg-dev-001` (see [PENDING_INFO.md](PENDING_INFO.md))
- [ ] Function App managed identity has **Key Vault Secrets User** on the vault
- [ ] Function App managed identity has Table Storage data-plane access (or `AzureWebJobsStorage` connection string is valid and scoped correctly)
- [ ] `Aggregated_Namibia` device + ontology created in Brightlayer, with tagIds for all 12 KPIs
- [ ] `brightlayer-aggregate-device-config` populated with the real `kpiTagMap`
- [ ] `brightlayer-writeback-credentials` populated with the real IoT Hub connection string
- [ ] `brightlayer-source-device-list` populated with real Namibia PLC device IDs
- [ ] `EXPECTED_PLC_COUNT` confirmed correct for the real fleet size
- [ ] At least one full cycle observed going `open` → `ready` → `sent` in Application Insights / Table Storage (the live smoke test every prior iteration deferred)
- [ ] Confirm Bicep/infra source-of-truth decision (Iteration 0/1 gap: Bicep still models Y1 Consumption, live resource is Flex Consumption) — either fix Bicep or formally accept CLI/portal as the source of truth going forward
- [ ] Confirm the "last 24h" vs "Today" ontology-field assumption in PENDING_INFO.md with the business owner

## Full-suite gate

- [x] `python -m pytest Namibia/azure_aggregation/tests -q` passes with the Iteration 8 cleanup tests included.
- Result: PASS (code + tests). Live cleanup/alerting behavior still unverified against real Azure resources — same underlying blocker as every prior iteration (see PENDING_INFO.md).
