# ENZYME Report

**Total Score: 63/100**
(Total: 0.628)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 1.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.769

## Issues
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/1
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/2
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/0/params
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s5/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: organoid integrity at /protocol/steps/s6/params/features/organoid integrity
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s8/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: organoid integrity at /protocol/steps/s9/params/features/organoid integrity
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s11/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s14/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: cell count at /protocol/steps/s16/params/features/cell count
