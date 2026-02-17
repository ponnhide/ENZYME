# ENZYME Report

**Total Score: 38/100**
(Total: 0.375)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 0.25
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/containers/0
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/containers/1
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): [{'key': 'amount', 'value': 'unspecified'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'amount', 'value': 'unspecified'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'duration', 'value': '16 h'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'wash_times', 'value': '2'}, {'key': 'wash_solution', 'value': 'm3'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'amount', 'value': 'unspecified'}] is not of type 'object' at /protocol/steps/4/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s3/params/program
