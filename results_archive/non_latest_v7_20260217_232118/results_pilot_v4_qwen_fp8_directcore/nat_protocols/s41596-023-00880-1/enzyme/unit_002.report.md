# ENZYME Report

**Total Score: 58/100**
(Total: 0.583)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.5
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'induction_condition', 'value': '6 µM CHIR99021 for 5 days'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'cell_count', 'value': '250,000 differentiated metanephric progenitors (day 13)'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'media_compartment', 'value': 'basolateral'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'pulse_condition', 'value': '5 µM CHIR99021 for 1 hour'}] is not of type 'object' at /protocol/steps/5/annotations
- `SCHEMA_INVALID` (error): [{'key': 'fixation', 'value': '4% PFA'}, {'key': 'staining', 'value': 'for nephron specification'}] is not of type 'object' at /protocol/steps/7/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s2/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s4/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s7/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: mL/well at /protocol/steps/0/params/amount/unit
