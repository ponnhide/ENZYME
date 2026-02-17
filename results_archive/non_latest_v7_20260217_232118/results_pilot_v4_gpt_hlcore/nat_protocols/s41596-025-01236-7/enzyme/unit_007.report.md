# ENZYME Report

**Total Score: 50/100**
(Total: 0.500)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.5
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.5

## Issues
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/1
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/2
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/0/params
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: cell count at /protocol/steps/s2/params/features/cell count
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: attachment at /protocol/steps/s6/params/features/attachment
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: confluence at /protocol/steps/s8/params/features/confluence
- `UNIT_PARSE_ERROR` (error): Invalid unit: cells at /protocol/steps/2/params/amount/unit
