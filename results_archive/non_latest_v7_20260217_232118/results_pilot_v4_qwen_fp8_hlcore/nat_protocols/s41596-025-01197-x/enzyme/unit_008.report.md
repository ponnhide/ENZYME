# ENZYME Report

**Total Score: 45/100**
(Total: 0.450)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.7

## Issues
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'amplicon_readout_system'. at /protocol/steps/s4/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'profile_name' for device_kind 'thermocycler'. at /protocol/steps/s11/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'amplicon_readout_system'. at /protocol/steps/s12/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: tissue_thickening at /protocol/steps/s14/params/features/tissue_thickening
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: tissue_curling at /protocol/steps/s14/params/features/tissue_curling
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: detachments at /protocol/steps/s14/params/features/detachments
- `UNIT_PARSE_ERROR` (error): Invalid unit: e6 at /protocol/steps/5/params/amount/unit
