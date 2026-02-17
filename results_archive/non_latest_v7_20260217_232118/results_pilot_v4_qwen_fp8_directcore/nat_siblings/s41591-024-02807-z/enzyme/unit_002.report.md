# ENZYME Report

**Total Score: 42/100**
(Total: 0.417)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.5
- **S_ident**: 0.0
- **S_param**: 0.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): 'pick_colony' is not one of ['allocate', 'transfer', 'manipulate', 'run_device', 'observe', 'annotate', 'dispose'] at /protocol/steps/0/op
- `SCHEMA_INVALID` (error): 'dislodge_cells' is not one of ['allocate', 'transfer', 'manipulate', 'run_device', 'observe', 'annotate', 'dispose'] at /protocol/steps/1/op
- `UNKNOWN_CORE_OP` (error): Unknown core op: pick_colony at /protocol/steps/s1/op
- `UNKNOWN_CORE_OP` (error): Unknown core op: dislodge_cells at /protocol/steps/s2/op
