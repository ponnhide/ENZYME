# ENZYME Report

**Total Score: 42/100**
(Total: 0.417)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.5
- **S_param**: 0.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Transplant blood vessel organoids into the kidney capsule of immunocompromised mice as previously described37. When transplanting, use one blood vessel organoid per kidney and transplant the entire blood vessel organoid (Fig. 4a). Transplanted blood vessel organoids can be grown in mice for >6 months.'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'critical_note', 'value': 'Inefficient differentiation could lead to teratoma formation in mice.'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Sacrifice mice and collect transplanted blood vessel organoids. If only one kidney is used for transplantation, the kidney without human transplant should be kept as a negative control.'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Fix transplants and kidney tissue in 4% PFA solution overnight at 4 °C.'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Dehydrate and paraffinize samples according to standard histological procedures.'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Cut 2- to 5-μm sections with a standard cryostat and collect them on Ultra Plus slides.'}] is not of type 'object' at /protocol/steps/5/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Perform standard de-paraffinization procedures.'}] is not of type 'object' at /protocol/steps/6/annotations
- `SCHEMA_INVALID` (error): [{'key': 'reference_step', 'value': 'Follow Steps 39–45 of the Procedure to stain organoids.'}] is not of type 'object' at /protocol/steps/7/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Carefully remove all PBS from the slides with a cellulose wipe.'}] is not of type 'object' at /protocol/steps/8/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Add a few drops of mounting medium and lay a coverslip on top. Avoid air bubbles.'}] is not of type 'object' at /protocol/steps/9/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Dry overnight in the dark at room temperature.'}] is not of type 'object' at /protocol/steps/10/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'The next day, seal the slide with nail polish.'}] is not of type 'object' at /protocol/steps/11/annotations
- `SCHEMA_INVALID` (error): [{'key': 'reference_step', 'value': 'Proceed to Step 47 of the Procedure to image organoids.'}] is not of type 'object' at /protocol/steps/12/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'dna_delivery_device'. at /protocol/steps/s1/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s11/params/program
