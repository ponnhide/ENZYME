# ENZYME Report

**Total Score: 67/100**
(Total: 0.667)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 1.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Add 3 mL of DMEM/F12, and disperse the colonies into single cells by pipetting until all cells are detached.'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Remove the supernatant'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'additive', 'value': '10 μM Y27632'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Gently resuspend the cell pellet in 1 mL of E8 + 10 μM Y27632'}] is not of type 'object' at /protocol/steps/5/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s3/params/program
