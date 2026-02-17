# ENZYME v7 Full-Corpus Comparison Report (EN)

## 1. Scope
- Corpus: 14 nat_protocols papers + 20 nat_siblings papers (34 total)
- Models: `gpt-oss-120b-v7` and `qwen3-next-80b-a3b-instruct-fp8-v7`

## 2. Score Comparison (paper means)
### gpt-oss-120b-v7
- overall: total=73.324, repro=24.856, units=228
- nat_protocols: total=75.035, repro=27.239, units_mean=9.14
- nat_siblings: total=72.126, repro=23.188, units_mean=5.00
- delta(protocols-siblings): total=2.909, repro=4.051
### qwen3-next-80b-a3b-instruct-fp8-v7
- overall: total=69.221, repro=21.844, units=231
- nat_protocols: total=72.836, repro=25.814, units_mean=8.50
- nat_siblings: total=66.691, repro=19.065, units_mean=5.60
- delta(protocols-siblings): total=6.145, repro=6.748

## 3. Reproducibility Significance (protocols vs siblings)
### gpt-oss-120b-v7
- Mann-Whitney p=0.096380, Welch p=0.089538
- effect size: Cohen d=0.537, Cliff delta=0.343
### qwen3-next-80b-a3b-instruct-fp8-v7
- Mann-Whitney p=0.031225, Welch p=0.003886
- effect size: Cohen d=0.978, Cliff delta=0.443

## 4. Cross-Model Correlation (paper-level)
- all: n=34, pearson_total=0.467, pearson_repro=0.355
- nat_protocols: n=14, pearson_total=0.420, pearson_repro=0.001
- nat_siblings: n=20, pearson_total=0.400, pearson_repro=0.313

## 5. Flow Metrics
### gpt-oss-120b-v7 / nat_protocols
- nodes_mean=9.143, material_edges_mean=0.500, logical_edges_mean=12.000
- combined_pass_rate=0.571, combined_isolated_rate_mean=0.095
- corr(repro, connectivity)=0.055
### gpt-oss-120b-v7 / nat_siblings
- nodes_mean=5.000, material_edges_mean=0.000, logical_edges_mean=2.100
- combined_pass_rate=0.100, combined_isolated_rate_mean=0.522
- corr(repro, connectivity)=-0.062
### qwen3-next-80b-a3b-instruct-fp8-v7 / nat_protocols
- nodes_mean=8.500, material_edges_mean=11.714, logical_edges_mean=6.714
- combined_pass_rate=0.500, combined_isolated_rate_mean=0.094
- corr(repro, connectivity)=0.385
### qwen3-next-80b-a3b-instruct-fp8-v7 / nat_siblings
- nodes_mean=5.600, material_edges_mean=2.000, logical_edges_mean=2.950
- combined_pass_rate=0.350, combined_isolated_rate_mean=0.418
- corr(repro, connectivity)=0.669

## 6. Top Categories (by unit count)
### gpt-oss-120b-v7
- nat_protocols:
  - cell_culture: n=98, repro_mean=28.153
  - centrifugation: n=37, repro_mean=28.757
  - microscopy_imaging: n=23, repro_mean=30.087
  - molecular_cloning: n=16, repro_mean=28.062
  - other: n=14, repro_mean=NA
- nat_siblings:
  - other: n=38, repro_mean=NA
  - cell_culture: n=24, repro_mean=26.833
  - microscopy_imaging: n=15, repro_mean=29.733
  - sequencing_library_prep: n=15, repro_mean=23.133
  - molecular_cloning: n=14, repro_mean=22.000
### qwen3-next-80b-a3b-instruct-fp8-v7
- nat_protocols:
  - cell_culture: n=70, repro_mean=26.600
  - other: n=32, repro_mean=NA
  - centrifugation: n=28, repro_mean=28.571
  - microscopy_imaging: n=23, repro_mean=29.870
  - flow_cytometry: n=10, repro_mean=28.800
- nat_siblings:
  - other: n=43, repro_mean=NA
  - cell_culture: n=32, repro_mean=25.000
  - microscopy_imaging: n=15, repro_mean=24.067
  - molecular_cloning: n=12, repro_mean=19.500
  - dna_rna_extraction: n=10, repro_mean=19.800

## 7. Artifacts
- `pilot_compare_repro_summary.md`
- `repro_group_significance.md`
- `model_correlation_total_grid.png` / `model_correlation_repro_grid.png`
- `repro_group_jitter_box.png`
