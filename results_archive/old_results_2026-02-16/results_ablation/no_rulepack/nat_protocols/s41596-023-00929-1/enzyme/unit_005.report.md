# ENZYME Report

**Total Score: 38/100**
(Total: 0.382)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 0.625
- **S_structural**: 0.0
- **S_vocab**: 0.667

## Issues
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/containers/0
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/containers/1
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/containers/2
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/1
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/10/params
- `UNKNOWN_ACTION_KIND` (warn): Unknown registry value: discard at /protocol/steps/s1/params/action_kind
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s8/params/program
- `UNKNOWN_ACTION_KIND` (warn): Unknown registry value: discard at /protocol/steps/s9/params/action_kind
- `UNKNOWN_ACTION_KIND` (warn): Unknown registry value: seal at /protocol/steps/s13/params/action_kind
