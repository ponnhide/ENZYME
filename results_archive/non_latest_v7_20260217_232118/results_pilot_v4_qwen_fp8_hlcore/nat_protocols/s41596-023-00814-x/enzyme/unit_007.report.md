# ENZYME Report

**Total Score: 62/100**
(Total: 0.617)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 1.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.7

## Issues
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'amplicon_readout_system'. at /protocol/steps/s17/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: sequencing quality at /protocol/steps/s18/params/features/sequencing quality
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: paired-end read mapping to Hg19 at /protocol/steps/s18/params/features/paired-end read mapping to Hg19
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: quantification with featureCounts at /protocol/steps/s18/params/features/quantification with featureCounts
- `UNIT_PARSE_ERROR` (error): Invalid unit: OVB organoids at /protocol/steps/0/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: medium at /protocol/steps/1/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: PBS at /protocol/steps/2/params/amount/unit
