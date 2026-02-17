# ENZYME Report

**Total Score: 49/100**
(Total: 0.487)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.923

## Issues
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/containers/0
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/containers/1
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/1
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/2
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/3
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/4
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/5
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/6
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/7
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s6/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s8/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s10/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s12/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'dna_delivery_device'. at /protocol/steps/s15/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: reads per cell at /protocol/steps/s16/params/features/reads per cell
