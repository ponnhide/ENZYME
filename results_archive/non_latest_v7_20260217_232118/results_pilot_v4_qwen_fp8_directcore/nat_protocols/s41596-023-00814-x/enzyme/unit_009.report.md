# ENZYME Report

**Total Score: 67/100**
(Total: 0.667)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 1.0
- **S_ident**: 0.0
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): ['Transfer 60-d-old organoids each to one well of a suspension culture 12-well plate.'] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): ['Add 2 ml of OVB-organoid medium per well.'] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): ['Keep the plate in absolute darkness at 37 °C and 5% CO2 for 24 h before ERG experiments.'] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): ['Prepare fresh OVB organoid medium in 50 ml centrifuge tubes.'] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): ['Oxygenate the OVB organoid medium by pumping air onto the bottom of the centrifuge tube with a sterile 10 ml serological pipette for 2 min under the clean bench.'] is not of type 'object' at /protocol/steps/4/annotations
- `SCHEMA_INVALID` (error): ['Set up the ERG aperture and fill the superfusion system with an oxygenated OVB medium.'] is not of type 'object' at /protocol/steps/6/annotations
- `SCHEMA_INVALID` (error): ['Place organoids under red light in an electrode chamber.'] is not of type 'object' at /protocol/steps/7/annotations
- `SCHEMA_INVALID` (error): ['Place electrode chamber into the dark chamber of the ERG aperture and connect it to the superfusion system containing oxygenated OVB medium.'] is not of type 'object' at /protocol/steps/8/annotations
- `SCHEMA_INVALID` (error): ['Set up the speed of superfusion to 0.5 ml/min.'] is not of type 'object' at /protocol/steps/9/annotations
- `SCHEMA_INVALID` (error): ['For dose-dependent light sensitivity, expose each organoid to 500 ms long flashes. Start with a low intensity of 2,000 mlux (moonlight on a clear night), increase to 20,000 mlux (candle light) and then to 200,000 mlux (daylight on a cloudy day). Repeat each intensity three times at 3 min intervals, and then switch to the next higher light intensity. Record all responses.'] is not of type 'object' at /protocol/steps/10/annotations
- `SCHEMA_INVALID` (error): ['Desensitize the organoid in the electrode chamber by bright light exposure with a light intensity of 4,600 lux for 10 min continuously. A 150 W white light bulb could be used as a bright light source.'] is not of type 'object' at /protocol/steps/12/annotations
- `SCHEMA_INVALID` (error): ['Place an infrared filter between the bulb and electrode chamber to subtract the thermal impact of the bright light source.'] is not of type 'object' at /protocol/steps/13/annotations
- `SCHEMA_INVALID` (error): ['Start light flashes of 500 ms and 200,000 mlux every 3 min and record the responses.'] is not of type 'object' at /protocol/steps/15/annotations
- `SCHEMA_INVALID` (error): ['After 30 min of flashing and recording, using the same organoids under the same conditions to repeat Step 11, but do not use bright light exposure, instead replacing it with 0 mlux (darkness). This can be used as a negative control for the bright light exposure procedure.'] is not of type 'object' at /protocol/steps/16/annotations
- `SCHEMA_INVALID` (error): ['Set up the superfusion system containing the OVB organoid medium to a higher speed of 2 ml/min.'] is not of type 'object' at /protocol/steps/17/annotations
- `SCHEMA_INVALID` (error): ["Add 10 mM aspartate to the medium after equilibration time is completed. Record electric response continuously. Aspartate will block the signal transduction from photoreceptors to the subsequent retinal cell layers ('A-wave')."] is not of type 'object' at /protocol/steps/19/annotations
- `SCHEMA_INVALID` (error): ['Wash out aspartate by adding OVB organoid medium without aspartate into the system. Continuously record the electric signals as responses to light flashes.'] is not of type 'object' at /protocol/steps/20/annotations
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'incubator'. at /protocol/steps/s3/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'imager'. at /protocol/steps/s11/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'imager'. at /protocol/steps/s13/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'imager'. at /protocol/steps/s16/params/program
- `MISSING_REQUIRED_PROGRAM_KEY` (error): Missing required program key 'program_name' for device_kind 'imager'. at /protocol/steps/s17/params/program
- `UNIT_PARSE_ERROR` (error): Invalid unit: organoid at /protocol/steps/0/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: organoid at /protocol/steps/7/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: chamber at /protocol/steps/8/params/amount/unit
- `UNIT_PARSE_ERROR` (error): Invalid unit: volume at /protocol/steps/20/params/amount/unit
