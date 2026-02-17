# ENZYME Report

**Total Score: 51/100**
(Total: 0.514)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.333
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.75

## Issues
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/1
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/0/params
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/1/params
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/3/params
- `UNKNOWN_ACTION_KIND` (warn): Unknown registry value: add at /protocol/steps/s9/params/action_kind
- `UNKNOWN_ACTION_KIND` (warn): Unknown registry value: elute at /protocol/steps/s12/params/action_kind
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'profile_name' for device_kind 'thermocycler'. at /protocol/steps/s13/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: cells at /protocol/steps/0/params/amount/unit
