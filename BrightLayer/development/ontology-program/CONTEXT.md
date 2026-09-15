# Ontology Program Context

## Purpose

This area contains the existing ontology parsing, comparison, parameter-list, trend-generation, and generated flow material used to understand and produce Node-RED logic.

## Important locations

- `Ontology_program/` contains the existing scripts and generated JSON/JavaScript/CSV files.
- `Ontology_excel/` contains spreadsheet-oriented ontology/reference material.
- `reference/parameters/` contains related parameter lists that remain separate from the program files.

## Constraints

- Generated files are evidence of the current work and should not be treated as a new package or API without checking their source script.
- Preserve trait IDs and existing ontology data unless a task explicitly changes them.
- Do not put credentials or live deployment values into generated outputs.

## Validation

Run the smallest relevant script or comparison check for the file being changed. Compare generated output before and after when generation is involved.
