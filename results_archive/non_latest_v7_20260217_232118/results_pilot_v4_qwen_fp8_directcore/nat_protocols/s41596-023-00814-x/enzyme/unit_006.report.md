# ENZYME Report

**Total Score: 48/100**
(Total: 0.478)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.867

## Issues
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: organoid_dissociation_status at /protocol/steps/s8/params/features/organoid_dissociation_status
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: organoid_dissociation_status at /protocol/steps/s11/params/features/organoid_dissociation_status
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s15/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'dna_delivery_device'. at /protocol/steps/s25/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'profile_name' for device_kind 'thermocycler'. at /protocol/steps/s30/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: organoids at /protocol/steps/0/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: carried-over medium at /protocol/steps/1/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: entire suspension at /protocol/steps/13/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: supernatant at /protocol/steps/15/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: appropriate amount at /protocol/steps/21/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: appropriate amount at /protocol/steps/22/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: pooled_cDNA at /protocol/steps/26/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: entire volume at /protocol/steps/27/params/amount/unit
