# ENZYME Report

**Total Score: 43/100**
(Total: 0.430)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 0.8
- **S_structural**: 0.0
- **S_vocab**: 0.778

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Wait for aggregates to settle by gravitation. Do not discard 6-well plate.'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'May take 15–20 min.'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Carefully aspirate medium.'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'volume', 'value': '3 mL per well'}, {'key': 'medium', 'value': 'N2B27 medium + 12 µM CHIR99021 + 30 ng/mL BMP-4'}, {'key': 'tool', 'value': 'e1'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Transfer aggregates back to low-attachment plate.'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'duration', 'value': '3 days'}, {'key': 'purpose', 'value': 'Induce mesodermal differentiation'}] is not of type 'object' at /protocol/steps/5/annotations
- `SCHEMA_INVALID` (error): [{'key': 'frequency', 'value': 'once per day'}, {'key': 'tool', 'value': 'e2'}, {'key': 'note', 'value': 'To avoid excessive fusion of aggregates.'}] is not of type 'object' at /protocol/steps/6/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Day 3: transfer aggregates to 15-mL Falcon tube. Do not discard 6-well plate.'}] is not of type 'object' at /protocol/steps/7/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Wait for aggregates to settle by gravitation.'}] is not of type 'object' at /protocol/steps/8/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Carefully aspirate medium.'}] is not of type 'object' at /protocol/steps/9/annotations
- `SCHEMA_INVALID` (error): [{'key': 'volume', 'value': '3 mL per well'}, {'key': 'medium', 'value': 'N2B27 medium + 100 ng/mL VEGF-A + 2 µM forskolin'}, {'key': 'tool', 'value': 'e1'}] is not of type 'object' at /protocol/steps/10/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Transfer aggregates back to low-attachment plate.'}] is not of type 'object' at /protocol/steps/11/annotations
- `SCHEMA_INVALID` (error): [{'key': 'duration', 'value': '2 days'}, {'key': 'reference', 'value': 'Fig. 2c'}] is not of type 'object' at /protocol/steps/12/annotations
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: aggregates settled at bottom at /protocol/steps/s2/params/features/aggregates settled at bottom
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s6/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: aggregates settled at bottom at /protocol/steps/s9/params/features/aggregates settled at bottom
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s13/params/program
