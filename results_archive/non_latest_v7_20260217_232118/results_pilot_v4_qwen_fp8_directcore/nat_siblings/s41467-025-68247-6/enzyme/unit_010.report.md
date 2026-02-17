# ENZYME Report

**Total Score: 45/100**
(Total: 0.450)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.2
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.5

## Issues
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/0/params
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s3/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: fluorescence at /protocol/steps/s4/params/features/fluorescence
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: DIC at /protocol/steps/s4/params/features/DIC
