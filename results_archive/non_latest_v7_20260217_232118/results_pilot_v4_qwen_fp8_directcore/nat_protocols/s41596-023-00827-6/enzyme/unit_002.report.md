# ENZYME Report

**Total Score: 49/100**
(Total: 0.488)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.929

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Pipette up and down several times to break the Matrigel and collect the content of the insert.'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Mix with equal amount of 100% ethanol'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add 5 μl DNase I (6 U/μl), 35 μl DNA Digestion Buffer'}] is not of type 'object' at /protocol/steps/10/annotations
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/10/params
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/26/params
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/31/params
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/32/params
- `SCHEMA_INVALID` (error): 'allocate_kind' is a required property at /protocol/steps/33/params
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s4/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s8/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s14/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s16/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s19/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s22/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s26/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s30/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'profile_name' for device_kind 'thermocycler'. at /protocol/steps/s31/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'amplicon_readout_system'. at /protocol/steps/s36/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: Ct value at /protocol/steps/s37/params/features/Ct value
