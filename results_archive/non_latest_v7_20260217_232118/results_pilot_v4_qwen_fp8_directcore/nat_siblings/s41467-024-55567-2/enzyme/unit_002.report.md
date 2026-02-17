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
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add SJ000291942 (10 μM) to culture'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add R-spondin1 CM (10%) to culture'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add Gastrin I (10 nM) to culture'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add A83-01 (0.5 μM) to culture'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add CHIR (4 μM) to culture'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add DAPT (10 μM) to culture'}] is not of type 'object' at /protocol/steps/5/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Incubate for 2 days with all additives'}] is not of type 'object' at /protocol/steps/6/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Replace CHIR with IWR-1'}] is not of type 'object' at /protocol/steps/7/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add IWR-1 (2 μM) to culture'}] is not of type 'object' at /protocol/steps/8/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Incubate for 3 days with IWR-1 replacing CHIR'}] is not of type 'object' at /protocol/steps/9/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s7/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s10/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/0/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/1/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/2/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/3/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/4/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/5/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/8/params/amount/unit
