# ENZYME Report

**Total Score: 48/100**
(Total: 0.479)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.875

## Issues
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s6/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s7/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s8/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: SIX2-GFP expression at /protocol/steps/s10/params/features/SIX2-GFP expression
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: PAX2-mCherry expression at /protocol/steps/s10/params/features/PAX2-mCherry expression
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'cell_counter'. at /protocol/steps/s11/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s14/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s22/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s23/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s24/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: ratio at /protocol/steps/15/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: cells at /protocol/steps/19/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: ratio at /protocol/steps/20/params/amount/unit
