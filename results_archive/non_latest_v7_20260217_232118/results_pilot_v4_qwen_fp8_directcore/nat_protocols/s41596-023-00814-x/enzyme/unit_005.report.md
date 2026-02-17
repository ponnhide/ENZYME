# ENZYME Report

**Total Score: 46/100**
(Total: 0.463)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.778

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Collect three to five OVB organoids of day 60'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Collect darkly pigmented aggregates'}] is not of type 'object' at /protocol/steps/8/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Within the next 2 weeks'}] is not of type 'object' at /protocol/steps/13/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'To subculture the RPE cells and obtain a pure RPE culture, one can optionally pick pigmented colonies and transfer small aggregates to a new laminin-coated TC-treated dish.'}] is not of type 'object' at /protocol/steps/14/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s4/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s7/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s10/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s13/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: expanding colonies of pigmented cells at /protocol/steps/s14/params/features/expanding colonies of pigmented cells
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: adherent monolayer sheets at /protocol/steps/s14/params/features/adherent monolayer sheets
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/0/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/1/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/8/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/11/params/amount/unit
