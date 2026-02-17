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
- `SCHEMA_INVALID` (error): [{'key': 'source_step', 'value': 'Step 7'}, {'key': 'note', 'value': 'Any barcode combination can be used to stain any culture condition (Supplementary Tables 3 and 4)'}] is not of type 'object' at /protocol/steps/0/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s2/params/program
