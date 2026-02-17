# ENZYME Report

**Total Score: 50/100**
(Total: 0.500)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Pick up a fused A-P spheroid using a mechanical pipette with a wide-bore 200-µl tip'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Spin down the spheroid in the 1.5-ml centrifuge tube'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'critical', 'value': 'Organoids may be visible but difficult to see; a dissecting microscope will help with visibility and handling'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add 20–30 µl/well of 100% Matrigel (Phenol Red–Free) on ice'}, {'key': 'critical', 'value': 'To avoid solidification of Matrigel, this step should be performed quickly'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Gently re-suspend the single A-P spheroid using a mechanical pipette with a wide-bore 200-µl tip'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Slowly plate the spheroid on a 24-well tissue culture plate (VWR International) to make a Matrigel drop'}, {'key': 'note', 'value': 'The tissue culture plate does not need to be on ice'}] is not of type 'object' at /protocol/steps/5/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Incubate the drop in a CO2 incubator at 37 °C for 5 min'}] is not of type 'object' at /protocol/steps/6/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Flip the plate upside down'}] is not of type 'object' at /protocol/steps/7/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Incubate for a further 5 min to prevent the spheroid from attaching to the bottom'}] is not of type 'object' at /protocol/steps/8/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add enough gut growth medium to cover the entire drop'}] is not of type 'object' at /protocol/steps/9/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Culture for 4 d to generate HBPOs'}, {'key': 'note', 'value': 'Cultures for spheroids should be maintained at 37 °C in an atmosphere of 5% CO2, 95% air'}, {'key': 'note', 'value': 'Gut growth medium should be replaced every 4 d'}] is not of type 'object' at /protocol/steps/10/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'centrifuge'. at /protocol/steps/s2/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s7/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s9/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s11/params/program
