# ENZYME Report

**Total Score: 55/100**
(Total: 0.549)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.294
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/0/params
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/1/params
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/5/params
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/7/params
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/9/params
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s4/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: cells at /protocol/steps/2/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unspecified at /protocol/steps/6/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unspecified at /protocol/steps/10/params/amount/unit
