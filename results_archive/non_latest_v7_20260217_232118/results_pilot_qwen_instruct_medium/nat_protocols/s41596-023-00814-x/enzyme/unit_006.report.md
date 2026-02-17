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
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/1
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/2
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'imager'. at /protocol/steps/s6/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'imager'. at /protocol/steps/s9/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: nuclear staining (DAPI) at /protocol/steps/s41/params/features/nuclear staining (DAPI)
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: antibody signal at /protocol/steps/s41/params/features/antibody signal
- `UNIT_PARSE_ERROR` (error): Invalid unit: part at /protocol/steps/0/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: wt/vol at /protocol/steps/1/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: drops at /protocol/steps/44/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: wt/vol at /resources/materials/0/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: wt/vol at /resources/materials/3/unit
