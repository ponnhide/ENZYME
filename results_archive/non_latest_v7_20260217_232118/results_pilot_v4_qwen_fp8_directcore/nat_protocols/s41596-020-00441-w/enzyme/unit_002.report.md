# ENZYME Report

**Total Score: 43/100**
(Total: 0.433)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.6

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Warm mTeSR1 at room temperature (15–25 °C)'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Confirm that the plated cells are healthy and are growing at a uniformly high density'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Aspirate old mTeSR1 with 10 μM Y-27632'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'volume_per_well', 'value': '500 μl'}, {'key': 'description', 'value': 'Add fresh mTeSR1 without Y-27632'}] is not of type 'object' at /protocol/steps/3/annotations
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: cell health at /protocol/steps/s2/params/features/cell health
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: cell density at /protocol/steps/s2/params/features/cell density
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s5/params/program
