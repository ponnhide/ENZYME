# ENZYME Report

**Total Score: 39/100**
(Total: 0.389)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 0.333
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'colon tissue was sliced open lengthwise and wiped 3–4 times with gauze (Fisher Scientific) to remove waste and mucus'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'tissue was cut into small sections of ~2" × 2" and placed into a 15 cm dish filled with PBS++'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'epithelium was minced from tissue segments using scalpels (Fisher Scientific) and collected into 50 mL conical tubes'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'minced epithelium was washed 3 times with DMEM++'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'centrifuged at 4 °C, 500 × g for 3 min between each wash'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'repeat', 'value': 'steps s4 and s5 repeated 3 times total'}] is not of type 'object' at /protocol/steps/5/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s5/params/program
