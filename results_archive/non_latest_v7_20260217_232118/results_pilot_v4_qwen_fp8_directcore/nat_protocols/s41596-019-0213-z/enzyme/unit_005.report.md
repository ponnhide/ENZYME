# ENZYME Report

**Total Score: 51/100**
(Total: 0.505)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.031
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Carefully aspirate the medium from a well using a P1000 pipette'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add 4% paraformaldehyde (PFA) solution in PBS for 20 min at room temperature'}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'critical', 'value': 'PFA fumes will affect cell viability in neighboring wells. If not all the wells of the 12-well plate are intended for fixation, use a spatula to carefully lift selected gels and use a spoon to transfer the matrix to another 12-well plate for fixation.'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Remove the PFA solution'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add PBS'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Cut the gels into smaller pieces (1/4–1/2 of a 12-well gel) under a stereomicroscope using extra-fine scissors and fine forceps. Avoid cutting through vascular networks.'}, {'key': 'tool', 'value': 'e5, e4'}] is not of type 'object' at /protocol/steps/6/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Use forceps to transfer the gel fragments to a fresh 2-mL Eppendorf tube'}] is not of type 'object' at /protocol/steps/7/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'For blood vessel organoid cultures, liberate the entire matrix from the well bottom, using the round end of a sterile spatula. Move the spatula toward the well center along the bottom of the well until the gel is freely floating.'}, {'key': 'tool', 'value': 'e2'}] is not of type 'object' at /protocol/steps/8/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Transfer the gel with a sterile lab spoon to the lid of a 10-cm dish'}] is not of type 'object' at /protocol/steps/9/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Use two sterile 30-gauge needles to cut out single blood vessel networks and try to reduce the amount of excessive matrix surrounding the organoids'}, {'key': 'tool', 'value': 'e6'}] is not of type 'object' at /protocol/steps/11/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Transfer single organoids (using a cut P1000 tip) to a 6-well low-attachment plate'}] is not of type 'object' at /protocol/steps/12/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add 5 mL of StemPro-34 SFM complete medium including 15% FBS, 100 ng/mL VEGF-A and 100 ng/mL FGF-2'}] is not of type 'object' at /protocol/steps/13/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'One day after separating the blood vessel networks (d11)'}] is not of type 'object' at /protocol/steps/14/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Use a cut P1000 tip to transfer single organoids to low-attachment round-bottom 96-well ultra-low-attachment plates'}] is not of type 'object' at /protocol/steps/15/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Add fresh StemPro-34 SFM complete medium including 15% FBS, 100 ng/mL VEGF-A and 100 ng/mL FGF-2'}] is not of type 'object' at /protocol/steps/16/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Around 4 d later (d15), blood vessel organoids should show a round and fully encapsulated morphology'}] is not of type 'object' at /protocol/steps/17/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s3/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s15/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s18/params/program
