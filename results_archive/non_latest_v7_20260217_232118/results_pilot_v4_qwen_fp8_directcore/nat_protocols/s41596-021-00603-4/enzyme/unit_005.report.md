# ENZYME Report

**Total Score: 58/100**
(Total: 0.583)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.5
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'solution', 'value': 'PBS'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'solution', 'value': '0.25 µM 194cisplatin/PBS'}] is not of type 'object' at /protocol/steps/1/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s3/params/program
