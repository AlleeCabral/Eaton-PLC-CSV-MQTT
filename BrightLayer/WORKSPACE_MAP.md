# BrightLayer Workspace Map

This repository contains several existing BrightLayer work areas. Open the smallest area that matches the task before loading more context.

## Applications

- `applications/namibia-aggregation/` is the Namibia Azure Functions aggregation project. Its source, tests, infrastructure, deployment notes, iteration history, and handoff material stay together.
- `applications/regional-node-red/` contains the regional Node-RED flow material. Regions are kept separate under `senegal-125/`, `peru-148/`, `gaza-146/`, `ukraine-159/`, and `cm12-peru/`.

## Development

- `development/ontology-program/` contains ontology parsing, comparison, trend-generation scripts, and their reference/generated files.
- `development/simulation/` contains the PLC/Node-RED simulation material and simulator flow-building work.

## Operations

- `operations/deployment/` contains Node-RED deployment and verification utilities.
- `operations/diagnostics/` contains diagnostic and troubleshooting material. Treat it as investigation support, not a production application.

## Reference

- `reference/parameters/` contains parameter lists and CSV reference data.
- `reference/ontology/` contains ontology reference data used to understand the existing model.

## Working rules

- Preserve existing runtime behavior unless the task explicitly asks for a behavior change.
- Keep secrets, tokens, SAS values, connection strings, and Key Vault values out of source and documentation.
- Namibia scheduler enablement and Brightlayer writeback require explicit approval.
- Historical files remain available, but do not treat diagnostics or experimental flow files as the supported production path without checking their local context.

## Choosing an entry point

- Namibia Azure behavior, tests, Bicep, deployment, or Brightlayer aggregation: start with `applications/namibia-aggregation/CONTEXT.md`.
- Regional Node-RED flow work: start with `applications/regional-node-red/CONTEXT.md`, then the relevant region.
- Ontology or trend generation: start with `development/ontology-program/CONTEXT.md`.
- Simulation: start with `development/simulation/CONTEXT.md`.
- Deployment or verification tooling: start with `operations/deployment/CONTEXT.md`.
- Troubleshooting artifacts: start with `operations/diagnostics/CONTEXT.md`.
