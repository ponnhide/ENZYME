# ENZYME Report

**Total Score: 56/100**
(Total: 0.555)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 1.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 0.333

## Issues
- `SCHEMA_INVALID` (error): 'type' is a required property at /resources/equipment/0
- `SCHEMA_INVALID` (error): None is not of type 'array' at /protocol/step_order
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'imager'. at /protocol/steps/s1/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: EpCAM (58,964 cells) at /protocol/steps/s2/params/features/EpCAM (58,964 cells)
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: ECAD (CDH1) (38,389 cells) at /protocol/steps/s2/params/features/ECAD (CDH1) (38,389 cells)
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: propidium iodide (PI) at /protocol/steps/s2/params/features/propidium iodide (PI)
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: Hoechst positive at /protocol/steps/s2/params/features/Hoechst positive
