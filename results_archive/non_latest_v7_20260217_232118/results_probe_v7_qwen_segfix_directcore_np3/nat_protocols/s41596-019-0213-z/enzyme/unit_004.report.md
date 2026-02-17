# ENZYME Report

**Total Score: 58/100**
(Total: 0.583)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.5
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Medium must be prewarmed to 37 °C to ensure matrix integrity.'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'observation', 'value': 'Sprouting vessels should appear after 1–3 days after embedding.'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'timing', 'value': 'Change medium after 3 days and then every other day.'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'next_step', 'value': 'On day 10, proceed to analyze blood vessel networks and/or grow and fix vascular organoid cultures.'}] is not of type 'object' at /protocol/steps/3/annotations
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/0/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/2/params/amount/unit
