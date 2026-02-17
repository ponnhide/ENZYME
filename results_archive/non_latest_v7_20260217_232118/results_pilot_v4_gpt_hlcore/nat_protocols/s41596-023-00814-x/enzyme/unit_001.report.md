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
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/containers/0
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/containers/1
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s3/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s7/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: cell attachment at /protocol/steps/s8/params/features/cell attachment
- `UNIT_PARSE_ERROR` (error): Invalid unit: drop at /protocol/steps/5/params/amount/unit
