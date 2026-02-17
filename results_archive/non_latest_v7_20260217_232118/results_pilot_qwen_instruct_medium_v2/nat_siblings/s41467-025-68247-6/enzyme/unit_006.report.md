# ENZYME Report

**Total Score: 51/100**
(Total: 0.506)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.036
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/1
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s2/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'cell_counter'. at /protocol/steps/s6/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s8/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: volume_unit_unknown at /protocol/steps/3/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: volume_unit_unknown at /protocol/steps/4/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: cells/µL at /protocol/steps/6/params/concentration/unit
