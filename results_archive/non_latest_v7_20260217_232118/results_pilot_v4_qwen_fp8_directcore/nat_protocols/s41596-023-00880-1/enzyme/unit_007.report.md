# ENZYME Report

**Total Score: 47/100**
(Total: 0.467)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.5
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.3

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'assay', 'value': 'Albumin uptake assay'}, {'key': 'organoid_stage', 'value': 'PT-enhanced organoid, day 27'}, {'key': 'imaging_mode', 'value': 'live confocal images'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'imaging_device', 'value': 'confocal microscope'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'assay', 'value': 'DAPI/organic cation transport assay'}, {'key': 'organoid_stage', 'value': 'PT-enhanced organoid, day 27'}, {'key': 'imaging_mode', 'value': 'live confocal images'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'assay', 'value': 'DAPI/organic cation transport assay'}, {'key': 'organoid_stage', 'value': 'PT-enhanced organoid, day 27'}, {'key': 'imaging_mode', 'value': 'live confocal images'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'condition', 'value': 'Substrate only'}, {'key': 'imaging_device', 'value': 'confocal microscope'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'assay', 'value': 'DAPI/organic cation transport assay'}, {'key': 'organoid_stage', 'value': 'PT-enhanced organoid, day 27'}, {'key': 'imaging_mode', 'value': 'live confocal images'}, {'key': 'condition', 'value': 'Substrate + inhibitor'}] is not of type 'object' at /protocol/steps/5/annotations
- `SCHEMA_INVALID` (error): [{'key': 'condition', 'value': 'Substrate + inhibitor'}, {'key': 'imaging_device', 'value': 'confocal microscope'}] is not of type 'object' at /protocol/steps/6/annotations
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: TRITC–albumin at /protocol/steps/s2/params/features/TRITC–albumin
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: Brightfield at /protocol/steps/s2/params/features/Brightfield
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: DAPI at /protocol/steps/s5/params/features/DAPI
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: DRAQ7 at /protocol/steps/s5/params/features/DRAQ7
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: Brightfield at /protocol/steps/s5/params/features/Brightfield
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: DAPI at /protocol/steps/s7/params/features/DAPI
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: DRAQ7 at /protocol/steps/s7/params/features/DRAQ7
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/0/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/2/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/3/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/5/params/amount/unit
