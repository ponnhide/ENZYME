# ENZYME Report

**Total Score: 46/100**
(Total: 0.458)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.75

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'target_confluency', 'value': '80-90%'}, {'key': 'critical_step', 'value': 'true'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Warm aliquot of day 0 medium to room temperature'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'critical_step', 'value': 'Pre-warming medium increases cell survival'}] is not of type 'object' at /protocol/steps/4/annotations
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: cell_confluency at /protocol/steps/s1/params/features/cell_confluency
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s5/params/program
