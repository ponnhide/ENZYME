# ENZYME Report

**Total Score: 41/100**
(Total: 0.406)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.038
- **S_param**: 0.4
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'volume', 'value': '10 mL'}, {'key': 'solution', 'value': 'PBS+++'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'filter', 'value': '100 µm cell strainer'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'matrix', 'value': 'Matrigel'}, {'key': 'temperature', 'value': 'cold'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'volume', 'value': '30 μL'}, {'key': 'density', 'value': '30–50 crypts per droplet'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'media', 'value': 'organoid growth media'}, {'key': 'action', 'value': 'fed to crypts'}] is not of type 'object' at /protocol/steps/6/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s3/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s6/params/program
