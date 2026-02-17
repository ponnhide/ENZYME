# ENZYME Report

**Total Score: 62/100**
(Total: 0.617)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.5
- **S_ident**: 0.2
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'medium', 'value': 'Neurobasal medium, 1:50'}, {'key': 'supplement', 'value': 'B27 supplement without vitamin A (Thermo Fisher Scientific, #12587010)'}, {'key': 'growth_factor', 'value': 'FGF-8b (Miltenyi, #130-095-740), 100 ng/mL'}] is not of type 'object' at /protocol/steps/0/annotations
- `UNIT_PARSE_ERROR` (error): Invalid unit: unknown at /protocol/steps/0/params/amount/unit
