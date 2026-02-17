# ENZYME Report

**Total Score: 48/100**
(Total: 0.478)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 0.867
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s5/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s9/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s17/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: cells at /protocol/steps/15/params/amount/unit
