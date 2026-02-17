# ENZYME Report

**Total Score: 45/100**
(Total: 0.450)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.1
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.6

## Issues
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/0/params
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'profile_name' for device_kind 'thermocycler'. at /protocol/steps/s2/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: Illumina NextSeq 550 sequencing at /protocol/steps/s4/params/features/Illumina NextSeq 550 sequencing
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: read depth 450-1000x at /protocol/steps/s4/params/features/read depth 450-1000x
