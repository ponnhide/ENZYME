# ENZYME Report

**Total Score: 54/100**
(Total: 0.542)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.25
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Organoid culture medium was supplemented with 10 µM EdU (5-ethynyl-2’-deoxyuridine, Beyotime)'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'incubated for 1 hour'}] is not of type 'object' at /protocol/steps/1/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s2/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: concentration at /protocol/steps/0/params/amount/unit
