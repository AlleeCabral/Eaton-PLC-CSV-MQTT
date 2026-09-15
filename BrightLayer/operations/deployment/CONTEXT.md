# Deployment Operations Context

## Purpose

This area contains the existing scripts used to deploy and verify Node-RED flows.

## Important locations

- `deploy_to_nodered.py` deploys flow content to a Node-RED endpoint.
- `verify_deploy.py` checks the resulting Node-RED deployment.
- Region-specific token helpers remain with their regional material where applicable.

## Constraints

- Confirm the target environment before any write operation.
- Prefer dry-run or local/test targets while reorganizing.
- Never print or commit tokens, SAS values, connection strings, or other credentials.
- Keep deployment scripts separate from diagnostic-only artifacts.
