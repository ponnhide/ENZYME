# ENZYME Report

**Total Score: 71/100**
(Total: 0.709)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 1.0
- **S_ident**: 0.254
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/0/params
- `SCHEMA_INVALID` (error): [{'key': 'purpose', 'value': 'prepare 10 mL blocking buffer for immunofluorescence staining'}, {'key': 'storage', 'value': 'store at 4 °C for up to 2 weeks'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'purpose', 'value': 'reconstitute BMP7 (10 µg) in 0.1% human serum albumin with 4 mM HCl'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'final_concentration', 'value': '100 µg/mL'}, {'key': 'aliquot_volume', 'value': '5 µL'}, {'key': 'storage', 'value': 'store at −80 °C for up to 6 months'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'final_concentration', 'value': '10 mM'}, {'key': 'storage', 'value': 'store at −20 °C for up to 12 months'}] is not of type 'object' at /protocol/steps/5/annotations
- `SCHEMA_INVALID` (error): [{'key': 'location', 'value': 'prepare in 50 mL Falcon tube (c8)'}, {'key': 'temperature', 'value': 'on ice'}, {'key': 'location', 'value': 'biological safety cabinet (e3)'}] is not of type 'object' at /protocol/steps/7/annotations
- `SCHEMA_INVALID` (error): [{'key': 'method', 'value': 'invert tube to mix'}] is not of type 'object' at /protocol/steps/8/annotations
- `SCHEMA_INVALID` (error): [{'key': 'storage', 'value': 'refrigerate aliquots'}] is not of type 'object' at /protocol/steps/9/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s5/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/7/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/9/params/amount/unit
