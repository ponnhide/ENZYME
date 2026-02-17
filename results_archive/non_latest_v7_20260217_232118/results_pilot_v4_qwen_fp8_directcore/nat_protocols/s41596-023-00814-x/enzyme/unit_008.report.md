# ENZYME Report

**Total Score: 48/100**
(Total: 0.479)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.0
- **S_ident**: 0.0
- **S_param**: 0.929
- **S_structural**: 0.0
- **S_vocab**: 0.944

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Fix the required number of OVB organoids by immersing them in 3–4 ml of 2.5% glutaraldehyde and 1.8% sucrose in PBS (pH 7.2)'}, {'key': 'critical', 'value': 'Ensure pH is adjusted to 7.2 to diminish fixation artifacts'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): 'rinse' is not one of ['allocate', 'transfer', 'manipulate', 'run_device', 'observe', 'annotate', 'dispose'] at /protocol/steps/2/op
- `SCHEMA_INVALID` (error): [{'key': 'critical', 'value': 'This washing step is critical to remove all traces of fixative, as glutaraldehyde and osmium tetroxide (to be used in the next step) form an intermediate compound that can break down to osmium black, a precipitate that can compromise the quality of the sample'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): 'rinse' is not one of ['allocate', 'transfer', 'manipulate', 'run_device', 'observe', 'annotate', 'dispose'] at /protocol/steps/3/op
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'post-fix in 1% aqueous solution of osmium tetroxide for 1–2 h at 4 °C'}, {'key': 'critical', 'value': 'Avoid longer exposures to osmium tetroxide as this may extract cytoplasmic components'}] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Agitate the samples very slowly on a wheel rotator'}] is not of type 'object' at /protocol/steps/18/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'cut the block with a razor blade to remove the resin around the sample and create a small trapezoidal block'}] is not of type 'object' at /protocol/steps/25/annotations
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'Perform ultrathin sections of uniform thickness of 400–500 nm using a Reichert ultramicrotome'}] is not of type 'object' at /protocol/steps/26/annotations
- `SCHEMA_INVALID` (error): 'rinse' is not one of ['allocate', 'transfer', 'manipulate', 'run_device', 'observe', 'annotate', 'dispose'] at /protocol/steps/31/op
- `SCHEMA_INVALID` (error): 'rinse' is not one of ['allocate', 'transfer', 'manipulate', 'run_device', 'observe', 'annotate', 'dispose'] at /protocol/steps/32/op
- `SCHEMA_INVALID` (error): 'rinse' is not one of ['allocate', 'transfer', 'manipulate', 'run_device', 'observe', 'annotate', 'dispose'] at /protocol/steps/35/op
- `SCHEMA_INVALID` (error): [{'key': 'note', 'value': 'One can perform observations on aTEM. In our case, we used a Tecnai G2 Spirit EM (FEI) equipped with a Morada CCD camera (Olympus)'}] is not of type 'object' at /protocol/steps/37/annotations
- `UNKNOWN_CORE_OP` (error): Unknown core op: rinse at /protocol/steps/s3/op
- `UNKNOWN_CORE_OP` (error): Unknown core op: rinse at /protocol/steps/s4/op
- `UNKNOWN_CORE_OP` (error): Unknown core op: rinse at /protocol/steps/s32/op
- `UNKNOWN_CORE_OP` (error): Unknown core op: rinse at /protocol/steps/s33/op
- `UNKNOWN_CORE_OP` (error): Unknown core op: rinse at /protocol/steps/s36/op
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s2/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s6/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s8/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s10/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s12/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s14/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s16/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s18/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s20/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s22/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s25/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'dna_delivery_device'. at /protocol/steps/s27/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s30/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s35/params/program
- `UNKNOWN_OBSERVATION_FEATURE` (warn): Unknown registry value: ultrathin section morphology at /protocol/steps/s38/params/features/ultrathin section morphology
- `UNIT_PARSE_ERROR` (error): Invalid unit: drop at /protocol/steps/33/params/amount/unit
