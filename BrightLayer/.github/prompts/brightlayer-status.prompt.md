---
name: "BrightLayer Status"
description: "Summarize the current BrightLayer Namibia Azure aggregation state, blockers, and next safe action."
agent: "BrightLayer Azure"
tools: [execute, read, search, azure-mcp/search]
argument-hint: "Optional focus area, such as Key Vault, dry-run, deployment, or devices"
---

Summarize the current BrightLayer Namibia Azure aggregation state.

Use these sources first:

1. `.azure/deployment-plan.md`
2. `Namibia/FRESH_CONVERSATION_HANDOFF.md`
3. `Namibia/azure_aggregation/README.md`
4. `Namibia/azure_aggregation/config/brightlayer-test-devices.json`
5. `Namibia/azure_aggregation/config/nam5-single-device-kpi-map.json`

Include:

- current gate;
- deployed Azure state if relevant;
- known blockers;
- next safe action;
- whether scheduler and writeback are disabled.

Do not print secret values.
