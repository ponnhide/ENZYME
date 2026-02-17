# ENZYME Report

**Total Score: 63/100**
(Total: 0.633)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 1.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.8

## Issues
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/0/params
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'amplicon_readout_system'. at /protocol/steps/s2/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'amplicon_readout_system'. at /protocol/steps/s3/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'imager'. at /protocol/steps/s5/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: spatial transcriptomics image at /protocol/steps/s6/params/features/spatial transcriptomics image
