# ENZYME Report

**Total Score: 40/100**
(Total: 0.400)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.4

## Issues
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/0/params
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'imager'. at /protocol/steps/s2/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: magnification at /protocol/steps/s3/params/features/magnification
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: objective at /protocol/steps/s3/params/features/objective
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: pixel_size at /protocol/steps/s3/params/features/pixel_size
