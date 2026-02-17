# ENZYME Report

**Total Score: 53/100**
(Total: 0.528)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.5
- **S_param**: 0.667
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'step', 'value': 'vi'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'step', 'value': 'vii'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'step', 'value': 'vii'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'step', 'value': 'vii'}, {'key': 'description', 'value': 'Move the flask a few times back and forth and left to right at the point where it is placed in the incubator to ensure that the cells are equally distributed (Supplementary Video 1).'}] is not of type 'object' at /protocol/steps/3/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s3/params/program
