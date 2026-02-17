# ENZYME Report

**Total Score: 50/100**
(Total: 0.500)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'dissociate anterior or posterior gut cells to single cells by incubation with TrypLE Express'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'add warm DMEM/F12 to each well to sufficiently dilute the TrypLE'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'centrifuge cells'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'resuspend pellet in day 7 medium'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'plate anterior or posterior gut cell suspensions in 96-well round-bottom ultra-low attachment plates at 10,000 cells per well'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'incubate to form spheroids'}] is not of type 'object' at /protocol/steps/5/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'prepare the same number of anterior and posterior spheroids'}] is not of type 'object' at /protocol/steps/6/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s1/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s3/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s6/params/program
