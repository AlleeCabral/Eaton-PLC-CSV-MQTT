# Iteration Memory and Gate Rules

## Purpose

This file tracks incremental delivery rules for the Brightlayer-Azure aggregation implementation.

## Iteration Sequence (Summary)

1. Iteration 0: Bootstrap and contracts
2. Iteration 1: Brightlayer auth and read client
3. Iteration 2: Cycle planner and state persistence
4. Iteration 3: Telemetry normalization and snapshot storage
5. Iteration 4: Aggregation engine
6. Iteration 5: Brightlayer writeback adapter
7. Iteration 6: End-to-end cycle orchestration
8. Iteration 7: Retry and failure handling
9. Iteration 8: Cleanup and retention
10. Iteration 9: Observability and alerting hardening
11. Iteration 10: Production readiness and rollout

## Gate Rules

1. Only one iteration can be in progress at a time.
2. No new iteration starts until the current iteration gate is green.
3. Each iteration must have explicit pass/fail criteria before implementation starts.
4. Each iteration must produce a short gate report with:
   - scope completed
   - tests run
   - pass/fail result
   - known risks
5. Idempotency and replay behavior must be re-checked when an iteration touches state, orchestration, retries, or writeback.
6. Manual Brightlayer UI verification is mandatory after writeback-related iterations.
7. Failed gates block promotion and require a corrective mini-iteration.
8. Configuration and secret contracts are treated as gate blockers when missing or invalid.

## Operational Defaults for Unstable PLC Connectivity

This rule applies to all Function App and aggregation-related iterations.

1. Default aggregation mode for field PLC environments is permissive, not strict.
2. When a PLC is temporarily offline, the app must carry forward the last valid value instead of replacing it with zero or blank data.
3. Stale values must be explicitly tagged with status metadata such as online, stale, or offline.
4. Each PLC reading must carry freshness metadata including last_updated_utc, stale_since_utc, and quality status.
5. Grace seconds exist to absorb short jitter and reconnect delays, but they do not mean the value is fresh if no new update arrives.
6. A value that is not refreshed should be shown operationally as stale, not as a current value. The UI must indicate that it is not updated or the PLC is offline.
7. Zero-fill and silent defaulting are forbidden for PLC telemetry because 0 can be a valid reading and hides the difference between real data and stale data.
8. Strict mode remains available for high-integrity KPI validation, but it must be used intentionally and only after the business rules are reviewed.
9. The function app implementation must preserve the last known value and a clear offline signal while connectivity is restored.

## Gate Discipline

1. Run only the tests required for the current iteration plus smoke checks for affected prior iterations.
2. Keep fixtures deterministic and versioned for repeatable gate outcomes.
3. Record decision notes when scope is reduced or deferred.
4. Re-evaluate iteration checklists quickly based on implementation results before starting the next iteration.

## Gate Report Template

- Iteration: <number>
- Date: <YYYY-MM-DD>
- Owner: <name>
- Scope:
- Tests executed:
- Result: PASS | FAIL
- Defects found:
- Fix plan (if fail):
- Risks carried forward:
- Checklist updates made:
