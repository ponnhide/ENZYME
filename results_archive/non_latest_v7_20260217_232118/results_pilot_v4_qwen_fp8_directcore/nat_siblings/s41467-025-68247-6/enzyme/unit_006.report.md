# ENZYME Report

**Total Score: 64/100**
(Total: 0.643)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 1.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.857

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'source', 'value': 'SUN bioscience'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'source', 'value': 'Cultrex domes'}, {'key': 'duration', 'value': 'at least 5 days after passaging'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'duration', 'value': '12 min'}, {'key': 'note', 'value': 'until organoids were largely single cells'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'protocol', 'value': 'as in the passaging protocol'}] is not of type 'object' at /protocol/steps/5/annotations
- `SCHEMA_INVALID` (error): [{'key': 'material', 'value': 'm4'}] is not of type 'object' at /protocol/steps/7/annotations
- `SCHEMA_INVALID` (error): [{'key': 'device', 'value': 'hemocytometer'}] is not of type 'object' at /protocol/steps/8/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'It is critical that Matrigel is added to the media while cold'}] is not of type 'object' at /protocol/steps/11/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s3/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: cell count at /protocol/steps/s9/params/features/cell count
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s11/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/4/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/6/params/amount/unit
