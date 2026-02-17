# ENZYME Report

**Total Score: 50/100**
(Total: 0.500)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'option', 'value': 'A'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'method', 'value': 'remove PBS with cellulose wipe'}, {'key': 'caution', 'value': 'do not touch gel with wipe'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'a few drops'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'action', 'value': 'place on top and squeeze gently'}, {'key': 'caution', 'value': 'avoid moving gel out of sandwich'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'purpose', 'value': 'avoid adhesion to surface'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'nail_polish'}, {'key': 'purpose', 'value': 'seal coverslip'}] is not of type 'object' at /protocol/steps/6/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'iSpacers'}, {'key': 'method', 'value': 'glue onto coverslip'}] is not of type 'object' at /protocol/steps/8/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'organoids'}] is not of type 'object' at /protocol/steps/9/annotations
- `SCHEMA_INVALID` (error): [{'key': 'method', 'value': 'remove PBS with P200 pipette'}] is not of type 'object' at /protocol/steps/10/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'drops'}] is not of type 'object' at /protocol/steps/11/annotations
- `SCHEMA_INVALID` (error): [{'key': 'tool', 'value': 'P200 pipette tip'}] is not of type 'object' at /protocol/steps/12/annotations
- `SCHEMA_INVALID` (error): [{'key': 'action', 'value': 'place on top'}] is not of type 'object' at /protocol/steps/13/annotations
- `SCHEMA_INVALID` (error): [{'key': 'action', 'value': 'remove excess mounting medium'}] is not of type 'object' at /protocol/steps/14/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'nail_polish'}, {'key': 'purpose', 'value': 'seal coverslip'}] is not of type 'object' at /protocol/steps/16/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s6/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s16/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: gel fragment at /protocol/steps/0/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: drop at /protocol/steps/2/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: coverslip at /protocol/steps/3/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: coverslip sandwich at /protocol/steps/4/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: drop at /protocol/steps/6/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: iSpacer at /protocol/steps/8/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: organoid at /protocol/steps/9/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: drop at /protocol/steps/11/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: coverslip at /protocol/steps/13/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: drop at /protocol/steps/16/params/amount/unit
