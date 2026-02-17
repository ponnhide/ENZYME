# ENZYME Report

**Total Score: 45/100**
(Total: 0.454)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.727

## Issues
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: organoid dissociation integrity at /protocol/steps/s7/params/features/organoid dissociation integrity
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: organoid dissociation integrity at /protocol/steps/s10/params/features/organoid dissociation integrity
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s14/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: cell viability at /protocol/steps/s17/params/features/cell viability
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'profile_name' for device_kind 'thermocycler'. at /protocol/steps/s21/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'profile_name' for device_kind 'thermocycler'. at /protocol/steps/s23/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: organoids at /protocol/steps/0/params/amount/unit
