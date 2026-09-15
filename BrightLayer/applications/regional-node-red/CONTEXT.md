# Regional Node-RED Context

## Purpose

This area contains the existing regional Node-RED flow material that sends PLC and water-filtration telemetry toward Brightlayer through the regional deployment pattern.

## Regions

- `senegal-125/`
- `peru-148/`
- `gaza-146/`
- `ukraine-159/`
- `cm12-peru/`

The Peru-148 folder contains the existing `148_flow.json`, `full_program_nodered`, and `route_fix_nodes.json` files. Their contents have been preserved during the move.

## Constraints

- Treat each region as a separate flow/deployment context.
- Do not assume a flow is production-ready solely because it is present here; check its local files and history.
- Do not commit credentials, connection strings, SAS values, or tokens embedded in flow configuration.
- Ontology and trend-generation material is maintained in `development/ontology-program/`.

## Validation

At minimum, parse changed JSON flow files and inspect the target region before deployment. Use `operations/deployment/` only with an explicitly selected non-production or approved target.
