# Namibia Aggregation Context

## Purpose

This is the Namibia Azure Functions application that reads Brightlayer telemetry, aggregates KPI values on five-minute cycles, stores cycle state, and prepares or performs controlled Brightlayer writeback.

## Important locations

- Function project: `azure_aggregation/`
- Source: `azure_aggregation/src/`
- Tests: `azure_aggregation/tests/`
- Infrastructure: `azure_aggregation/infra/`
- Configuration: `azure_aggregation/config/`
- Package and probe scripts: `azure_aggregation/scripts/`
- Deployment plan: repository `.azure/deployment-plan.md`
- Iteration history and handoff notes: this folder

## Current behavior and constraints

- The cycle planner, queue worker, cleanup timer, storage repositories, telemetry normalization, aggregation, and writeback adapter are implemented.
- Timeseries reads use child device IDs and whole-second UTC timestamps.
- Missing values use carry-forward metadata; zero-fill is forbidden.
- Keep the planner disabled and `WRITEBACK_MODE=dry_run` unless explicitly approved.
- Never print or commit secrets, bearer tokens, SAS tokens, connection strings, or Key Vault values.

## Validation

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest applications\namibia-aggregation\azure_aggregation\tests -q
az bicep build --file applications\namibia-aggregation\azure_aggregation\infra\main.bicep --stdout
.\applications\namibia-aggregation\azure_aggregation\scripts\build_function_package.ps1 -PythonPath .\.venv\Scripts\python.exe
```

## Start here

Read `.azure/deployment-plan.md`, `FRESH_CONVERSATION_HANDOFF.md`, and `azure_aggregation/README.md` only as needed for the task.
