# ENZYME Report

**Total Score: 67/100**
(Total: 0.667)

**Schema version:** 0.4
**IR kind:** core
**Validation:** FAIL

## Scores
- **S_ambiguity**: 1.0
- **S_exec_env**: 0.5
- **S_ident**: 0.5
- **S_param**: 1.0
- **S_structural**: 0.0
- **S_vocab**: 1.0

## Issues
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Used 3,000 features to compute a 50-dimensional representation of the data using principal component analysis (PCA)'}] is not of type 'object' at /protocol/steps/0/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': "Computed a k-nearest-neighbour (kNN) graph with n_neighbors = 30 and metric = 'cosine' using the PCA representation"}] is not of type 'object' at /protocol/steps/1/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Computed a two-dimensional representation of the data using UMAP'}] is not of type 'object' at /protocol/steps/2/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Computed coarse clustering with resolution = 1 using Leiden clustering'}] is not of type 'object' at /protocol/steps/3/annotations
- `SCHEMA_INVALID` (error): [{'key': 'description', 'value': 'Computed fine clustering with resolution = 80 using Leiden clustering'}] is not of type 'object' at /protocol/steps/4/annotations
