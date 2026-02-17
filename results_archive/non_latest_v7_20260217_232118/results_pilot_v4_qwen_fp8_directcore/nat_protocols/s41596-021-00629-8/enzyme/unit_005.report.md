# ENZYME Report

**Total Score: 45/100**
(Total: 0.451)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 0.875
- **S_structural**: 0.0
- **S_vocab**: 0.833

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'aspirate the medium before adding PBS w/o'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'aspirate the PBS w/o'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'critical_note', 'value': 'Prolonged incubation with Accutase might be harmful for the cells'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'rinse the flask bottom with medium to detach the cells'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'remove the supernatant'}] is not of type 'object' at /protocol/steps/6/annotations
- `SCHEMA_INVALID` (error): [{'key': 'material', 'value': 'E8 + 10 μM Y27632'}, {'key': 'volume', 'value': '1 mL'}] is not of type 'object' at /protocol/steps/7/annotations
- `SCHEMA_INVALID` (error): [{'key': 'method', 'value': 'Trypan blue staining in a hemocytometer using standard methods'}, {'key': 'reference', 'value': 'previously described33'}] is not of type 'object' at /protocol/steps/8/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s4/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s6/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: cell_viability at /protocol/steps/s9/params/features/cell_viability
