# ENZYME Report

**Total Score: 47/100**
(Total: 0.472)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.5
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.333

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'warm medium at room temperature before transfer'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'warm medium at room temperature before transfer'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'phenol red turns yellow by 24 h due to high live cell count'}, {'key': 'reference_figure', 'value': 'Fig. 2d–f'}] is not of type 'object' at /protocol/steps/2/annotations
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: medium color change to yellow at /protocol/steps/s3/params/features/medium color change to yellow
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: formation of 3D structures including attached and floating spheroids at /protocol/steps/s3/params/features/formation of 3D structures including attached and floating spheroids
- `UNIT_PARSE_ERROR` (error): Invalid unit: μl/well at /protocol/steps/0/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: μl/well at /protocol/steps/1/params/amount/unit
