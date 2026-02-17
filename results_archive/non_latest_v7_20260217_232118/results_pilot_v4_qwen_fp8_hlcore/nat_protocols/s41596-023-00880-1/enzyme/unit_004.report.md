# ENZYME Report

**Total Score: 47/100**
(Total: 0.470)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.125
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.692

## Issues
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s2/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s5/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s10/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s11/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: fluorescent albumin uptake at /protocol/steps/s12/params/features/fluorescent albumin uptake
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: DAPI uptake at /protocol/steps/s13/params/features/DAPI uptake
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: PT-specific protein expression at /protocol/steps/s15/params/features/PT-specific protein expression
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: Lotus tetragonobulus lectin (LTL) binding at /protocol/steps/s15/params/features/Lotus tetragonobulus lectin (LTL) binding
- `UNIT_PARSE_ERROR` (error): Invalid unit: cells at /protocol/steps/0/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: well at /protocol/steps/2/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: fraction at /protocol/steps/5/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: fraction at /protocol/steps/6/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: well at /protocol/steps/7/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: well at /protocol/steps/8/params/amount/unit
