# ENZYME Report

**Total Score: 40/100**
(Total: 0.403)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 0.667
- **S_structural**: 0.0
- **S_vocab**: 0.75

## Issues
- `SCHEMA_INVALID` (error): 'pick_colony' is not one of ['allocate', 'transfer', 'manipulate', 'run_device', 'observe', 'annotate', 'dispose'] at /protocol/steps/2/op
- `UNKNOWN_CORE_OP` (error): Unknown core op: pick_colony at /protocol/steps/s3/op
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'dna_delivery_device'. at /protocol/steps/s2/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: MBD3 protein expression at /protocol/steps/s5/params/features/MBD3 protein expression
