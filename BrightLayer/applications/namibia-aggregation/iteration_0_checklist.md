# Iteration 0 Checklist - Bootstrap and Contracts

## Iteration Goal

Establish the minimum project skeleton, configuration contracts, and validation checks so later iterations can implement safely and consistently.

## Scope

- Project folder structure for Azure aggregation module
- Configuration loader contract
- Environment variable contract
- Queue message schema contract
- Logging envelope contract
- Basic validation command/script contract

## Done Criteria

1. Required folder structure exists.
2. Configuration contract is documented with required keys and types.
3. Validation routine for required settings exists and fails fast on missing keys.
4. Queue payload shapes are documented and validated.
5. Logging envelope fields are defined and used by stubs.
6. A gate report is produced with pass/fail.

## Task Checklist

- [x] Create module skeleton folders under Namibia/azure_aggregation (infra, src, modules, shared, tests).
- [x] Add placeholder files for function entry points and shared utilities.
- [x] Define required app settings list with types and defaults where applicable. (`shared/config.py` REQUIRED_ENV_KEYS; deployed live to the Flex Consumption Function App — see Namibia/azure_aggregation_architecture.md)
- [x] Define required Key Vault secret names. (`shared/config.py` REQUIRED_SECRET_KEYS — 9 secrets; existence in Key Vault not yet verified live)
- [ ] Define queue message schemas for fetch-cycle, aggregate-cycle, writeback-cycle. **NOT DONE** — `function_app.py` declares queue-triggered stubs but no formal schema/contract doc or validator exists yet. Carried forward to Iteration 6 (orchestration).
- [x] Define cycle key format and time boundary helper contract. (`modules/cycle_planner.py`: `floor_to_5_minutes`, `cycle_bounds`, `cycle_key` — implemented with real logic ahead of schedule, not just a stub, and covered by tests)
- [ ] Define standard log envelope fields (module, cycleKey, runId, attempt, status, timestamp). **PARTIAL** — `shared/observability.py` has `build_log_envelope(module, cycle_key, run_id, attempt, status)` but it is not yet wired into any module's actual logging calls.
- [x] Document the operational default for unstable PLC connectivity before the Function App iteration: permissive aggregation, carry-forward last known value, and explicit stale/offline metadata. (documented in iteration_memory.md)
- [x] Add a configuration validation script or function stub contract. (`shared/config.py` `validate_required_env`)
- [x] Add at least one positive config fixture and one negative fixture for missing-key failure. (`tests/test_config.py`)
- [x] Document how to execute Iteration 0 gate checks. (`azure_aggregation/README.md` "Validation commands")

## Gate Checks

- [x] Config validation passes with complete fixture.
- [x] Config validation fails with missing required keys.
- [ ] Queue schemas validate example payloads. **NOT DONE** — no schemas exist yet (see above).
- [x] Folder and file skeleton matches declared structure.
- [x] Gate report generated and stored (below).

## Quick Re-evaluation Rule

After implementation and gate execution, quickly re-evaluate this checklist and update:

- completed items that were skipped or partially done
- additional checks discovered during execution
- scope adjustments required for Iteration 1

This re-evaluation must happen before the next iteration begins.

## Gate Report Stub

- Iteration: 0
- Date: 2026-08-22
- Owner: Alexandra Cabral (with GitHub Copilot)
- Scope completed: project skeleton, config contract + validation, Key Vault secret names contract, cycle time-boundary helpers, app settings deployed live to Azure Flex Consumption Function App, Key Vault URI wired.
- Tests executed: `python -m pytest Namibia/azure_aggregation/tests -q` (at time of this gate: `test_config.py`, `test_cycle_planner.py` — all passing)
- Result: **PASS with carried-forward gaps** (queue message schemas and full log-envelope wiring deferred — see below)
- Missing items: queue payload schema contracts (fetch-cycle/aggregate-cycle/writeback-cycle) not defined; log envelope not wired into module logging calls; Key Vault secret *values* not yet verified to exist (only names/contract defined); Key Vault RBAC role assignment for the Function App's managed identity not confirmed in Bicep.
- Immediate follow-ups: address queue schemas when Iteration 6 (orchestration) begins; confirm Key Vault secrets + RBAC before Iteration 5 (writeback) can run live.
- Checklist changes applied: marked completed items above; queue schema and log-envelope-wiring items explicitly carried forward rather than marked done.
