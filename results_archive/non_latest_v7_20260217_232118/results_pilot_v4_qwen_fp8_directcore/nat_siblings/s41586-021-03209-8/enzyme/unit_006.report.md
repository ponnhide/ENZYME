# ENZYME Report

**Total Score: 50/100**
(Total: 0.500)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 1.0
- **S_ident**: 0.0
- **S_param**: 0.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Single cells were loaded onto chromium chips with a capture target of 10,000 cells per sample.'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Libraries were prepared following the provided protocol and sequenced with a targeted sequencing depth of 50,000 reads per cell.'}] is not of type 'object' at /protocol/steps/1/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'dna_delivery_device'. at /protocol/steps/s1/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'amplicon_readout_system'. at /protocol/steps/s2/params/program
