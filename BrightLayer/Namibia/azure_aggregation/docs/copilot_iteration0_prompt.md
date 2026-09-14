# Copilot Prompt: Azure Iteration 0 Implementation for Namibia Brightlayer Aggregation

Use this prompt in Copilot Chat in VS Code.

---

Copy and paste the following:

Create a complete Azure Functions project skeleton for the Namibia Brightlayer aggregation solution based on the blueprint and iteration checklist.

Project goal:
- Build the first implementation iteration for Azure-native orchestration and state management.
- Do not implement the actual production aggregation logic yet.
- Focus on project structure, configuration contract, validation, queue message contracts, logging contract, and Azure service skeleton.
- Keep the solution aligned with the blueprint in the project documentation.

Important references to follow:
- Use the requirements discussed in the Azure blueprint for Namibia.
- Follow the gate rules from the iteration checklist.
- Keep the design consistent with Azure Functions, Azure Storage Tables, Key Vault, and Application Insights.
- Use Python 3.11 runtime with Azure Functions (Node.js is not required here; Python is the better fit for the blueprint examples).

Create the following folder and file structure inside the workspace under:

Namibia/azure_aggregation/

Structure:

Namibia/
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
        __init__.py
        config.py
        brightlayer_client.py
        storage_cycle_repo.py
        telemetry_normalizer.py
        aggregations.py
        retry_policy.py
        observability.py
      modules/
        __init__.py
        cycle_planner.py
        fetch_source_telemetry.py
        aggregate_cycle.py
        writeback_to_brightlayer.py
        cleanup_cycles.py
    tests/
      test_config_validation.py
      test_cycle_semantics.py
      test_idempotency.py

Required app settings to define:
- EXPECTED_PLC_COUNT = 15
- CYCLE_INTERVAL_MINUTES = 5
- CYCLE_GRACE_SECONDS = 90
- AGGREGATION_MODE = strict
- MAX_RETRIES = 3
- RETRY_BASE_SECONDS = 10
- CYCLE_TABLE_STATUS = CycleStatus
- CYCLE_TABLE_SNAPSHOT = CycleDataSnapshot
- CYCLE_TABLE_AUDIT = CycleAudit
- RETENTION_HOURS = 12
- KEYVAULT_URI = https://<your-kv>.vault.azure.net/

Required Key Vault secrets to define:
- brightlayer-service-account-id
- brightlayer-service-account-secret
- brightlayer-api-prefix
- brightlayer-organization-id
- brightlayer-source-device-list
- brightlayer-source-trait-list
- brightlayer-aggregate-device-config
- brightlayer-writeback-credentials
- aggregation-kpi-map

Required Azure tables:
- CycleStatus
- CycleDataSnapshot
- CycleAudit

Required log envelope fields for every module:
- module
- cycleKey
- runId
- attempt
- status
- timestamp

Required queue payload contracts:
1. fetch-cycle
   {
     "cycleKey": "2026-07-30T10:15:00Z",
     "cycleStartUtc": "2026-07-30T10:15:00Z",
     "cycleEndUtc": "2026-07-30T10:20:00Z"
   }

2. aggregate-cycle
   {
     "cycleKey": "2026-07-30T10:15:00Z",
     "attempt": 1
   }

3. writeback-cycle
   {
     "cycleKey": "2026-07-30T10:15:00Z",
     "pointCount": 3,
     "quality": "complete"
   }

Required contract behavior:
- All timestamps in UTC.
- Cycle key format should be ISO string with 5-minute floor, example: 2026-07-30T10:15:00Z.
- Validation must fail fast when required config keys are missing.
- Config validation must pass for a valid fixture and fail for a missing-key fixture.
- The project should contain stubs, not production-ready logic.
- Keep the Azure logic cleanly separated by module and shared utility.

Please generate the following:

1. infra/main.bicep
   - Resource group is not created here; only resource definitions for: storage account, Key Vault, Application Insights, function app plan, function app.
   - Use managed identity.
   - Disable public access on storage.
   - Set TLS minimum 1.2.
   - Enable Application Insights integration.
   - Use RBAC authorization for Key Vault.
   - Set AzureWebJobsStorage appropriately for dev environment.

2. infra/parameters.dev.json
   - Provide a realistic dev environment parameter file.

3. infra/parameters.prod.json
   - Provide a realistic prod environment parameter file.

4. src/host.json
   - Include proper Azure Functions host settings.
   - Include Application Insights logging configuration.

5. src/requirements.txt
   - Include realistic Python packages for Azure Functions, Key Vault, Table Storage, requests, and retry logic.

6. src/local.settings.example.json
   - Include the required app settings but do not include secrets.

7. src/function_app.py
   - Create a basic Azure Functions v2 app with timer trigger and queue triggers as entry points.
   - Use placeholder functions for:
     - cycle_planner_timer
     - fetch_source_telemetry
     - aggregate_cycle
     - writeback_to_brightlayer
     - cleanup_cycles
   - These should be stubbed but should include docstrings and log calls.

8. src/shared/config.py
   - Define required environment variables and secret names.
   - Implement a validation routine that raises a ValueError if required config is missing.
   - Add a function that parses integer config values safely.
   - Add a function that loads all required config as a dictionary.

9. src/shared/brightlayer_client.py
   - Create a minimal Brightlayer client stub.
   - Add methods for token retrieval and a generic request method.
   - Do not hardcode secrets.
   - Use dependency injection and config values.

10. src/shared/storage_cycle_repo.py
   - Create a minimal storage repo stub for table operations.
   - Include methods for creating tables and writing status snapshot rows.
   - Use table names from config.

11. src/shared/telemetry_normalizer.py
   - Create a basic normalization stub for source telemetry records.
   - Include a function to normalize timeseries records into snapshot rows.

12. src/shared/aggregations.py
   - Create a stub for aggregation logic.
   - Include functions for sum, avg, min, and max.
   - Include precision handling.

13. src/shared/retry_policy.py
   - Add a simple retry helper with exponential backoff.

14. src/shared/observability.py
   - Add a standard log-envelope helper.
   - Include a function to build a structured log payload.

15. src/modules/cycle_planner.py
   - Create a cycle planner stub.
   - Include the cycle key generation and time boundary helper logic.

16. src/modules/fetch_source_telemetry.py
   - Create a module stub that loads config and calls the Brightlayer client in a placeholder way.

17. src/modules/aggregate_cycle.py
   - Create a stub for cycle aggregation and lock logic.
   - Include a placeholder comment for optimistic locking.

18. src/modules/writeback_to_brightlayer.py
   - Create a stub for writeback payload creation and call to Brightlayer ingestion method.

19. src/modules/cleanup_cycles.py
   - Create a stub for retention cleanup logic.

20. tests/test_config_validation.py
   - Add tests for:
     - valid config passes
     - missing required key raises ValueError
   - Use Python unittest or pytest.

21. tests/test_cycle_semantics.py
   - Add a simple test for cycle key formatting and time floor logic.

22. tests/test_idempotency.py
   - Add tests that conceptually validate idempotency and duplicate handling requirements.

Also create a concise project README in:

Namibia/azure_aggregation/README.md

The README should include:
- purpose of the project
- folder structure
- required Azure services
- required app settings
- required Key Vault secrets
- validation commands
- iteration gate summary
- instructions for next step: implement Iteration 1 (Brightlayer auth and read client)

Finally, produce a short gate report markdown file in:

Namibia/azure_aggregation/gate_iteration_0.md

The gate report should include:
- Iteration: 0
- Date: <YYYY-MM-DD>
- Owner: <name>
- Scope completed:
- Tests executed:
- Result: PASS | FAIL
- Missing items:
- Immediate follow-ups:
- Checklist changes applied:

Please keep the code clean, readable, and aligned with the blueprint and checklist. Use Python best practices, docstrings, and clear naming.

Then run the relevant Python tests for the config validation and cycle semantics tests and report the outcome. If any test fails, fix it and re-run until the validation passes.

End with a short summary of what was created and the next recommended Azure step after this iteration.

---

Optional second prompt if needed:

Now create the next Azure implementation step: Iteration 1, which focuses only on Brightlayer authentication and read client logic. Keep it isolated and do not touch the aggregation engine or writeback logic yet.

----

This is the minimal first iteration prompt to run in Copilot.
