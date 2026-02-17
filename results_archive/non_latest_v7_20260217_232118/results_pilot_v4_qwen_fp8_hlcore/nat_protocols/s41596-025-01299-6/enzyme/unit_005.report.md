# ENZYME Report

**Total Score: 47/100**
(Total: 0.467)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.8

## Issues
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'plate_reader'. at /protocol/steps/s5/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: GFP_fluorescence_intensity at /protocol/steps/s6/params/features/GFP_fluorescence_intensity
- `UNIT_PARSE_ERROR` (error): Invalid unit: each at /protocol/steps/7/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: each at /protocol/steps/10/params/amount/unit
