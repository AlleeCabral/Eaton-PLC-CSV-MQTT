# Simulation Context

## Purpose

This area contains the existing PLC and Node-RED simulation material used for development and testing. It is not the production regional flow.

## Important locations

- `Simulation/` contains the simulation flow artifact.
- Related flow-building or simulator scripts are kept with this development area where they were moved.
- Peru-specific production flow material remains under `applications/regional-node-red/peru-148/`.

## Constraints

- Use test or local Node-RED targets only unless a deployment is explicitly approved.
- Keep simulator assumptions separate from production device configuration.
- Preserve existing generated flow behavior while reorganizing.
