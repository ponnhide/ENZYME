# Pilot Integrated Report (Scores + Categories + Flow)

## Scope
- Corpus: nat_protocols (14 papers) + nat_siblings (20 papers), total 34 papers.
- Models: gpt-oss-120b-v7 (228 units), qwen3-next-80b-a3b-instruct-fp8-v7 (231 units).

## Score Summary
### gpt-oss-120b-v7
- total mean (protocols/siblings): 75.035 / 72.126
- repro mean (protocols/siblings): 27.239 / 23.188
- delta total (protocols-siblings): 2.909
- delta repro (protocols-siblings): 4.051
### qwen3-next-80b-a3b-instruct-fp8-v7
- total mean (protocols/siblings): 72.836 / 66.691
- repro mean (protocols/siblings): 25.814 / 19.065
- delta total (protocols-siblings): 6.145
- delta repro (protocols-siblings): 6.748

## Repro Significance (nat_protocols vs nat_siblings)
### gpt-oss-120b-v7
- Mann-Whitney p(two-sided): 0.096380
- Welch t p(two-sided): 0.089538
- Cohen d: 0.537
- Cliff delta: 0.343
### qwen3-next-80b-a3b-instruct-fp8-v7
- Mann-Whitney p(two-sided): 0.031225
- Welch t p(two-sided): 0.003886
- Cohen d: 0.978
- Cliff delta: 0.443

## Flow Connectivity Summary
### gpt-oss-120b-v7 / nat_protocols
- papers: 14
- mean nodes per paper: 9.143
- mean material edges: 0.500
- mean logical edges: 12.000
- nonzero-edge rate (material/logical): 0.286 / 1.000
- combined pass rate: 0.571
- combined isolated rate mean: 0.095
- corr(repro, connectivity=1-isolated_rate): 0.055
### gpt-oss-120b-v7 / nat_siblings
- papers: 20
- mean nodes per paper: 5.000
- mean material edges: 0.000
- mean logical edges: 2.100
- nonzero-edge rate (material/logical): 0.000 / 0.600
- combined pass rate: 0.100
- combined isolated rate mean: 0.522
- corr(repro, connectivity=1-isolated_rate): -0.062
### qwen3-next-80b-a3b-instruct-fp8-v7 / nat_protocols
- papers: 14
- mean nodes per paper: 8.500
- mean material edges: 11.714
- mean logical edges: 6.714
- nonzero-edge rate (material/logical): 0.929 / 0.929
- combined pass rate: 0.500
- combined isolated rate mean: 0.094
- corr(repro, connectivity=1-isolated_rate): 0.385
### qwen3-next-80b-a3b-instruct-fp8-v7 / nat_siblings
- papers: 20
- mean nodes per paper: 5.600
- mean material edges: 2.000
- mean logical edges: 2.950
- nonzero-edge rate (material/logical): 0.450 / 0.700
- combined pass rate: 0.350
- combined isolated rate mean: 0.418
- corr(repro, connectivity=1-isolated_rate): 0.669

## Category Highlights (unit-level)
### gpt-oss-120b-v7
- nat_protocols top categories by unit count:
  - cell_culture: n=98, repro_mean=28.153
  - centrifugation: n=37, repro_mean=28.757
  - microscopy_imaging: n=23, repro_mean=30.087
  - molecular_cloning: n=16, repro_mean=28.062
  - other: n=14, repro_mean=NA
- nat_siblings top categories by unit count:
  - other: n=38, repro_mean=NA
  - cell_culture: n=24, repro_mean=26.833
  - microscopy_imaging: n=15, repro_mean=29.733
  - sequencing_library_prep: n=15, repro_mean=23.133
  - molecular_cloning: n=14, repro_mean=22.000
### qwen3-next-80b-a3b-instruct-fp8-v7
- nat_protocols top categories by unit count:
  - cell_culture: n=70, repro_mean=26.600
  - other: n=32, repro_mean=NA
  - centrifugation: n=28, repro_mean=28.571
  - microscopy_imaging: n=23, repro_mean=29.870
  - flow_cytometry: n=10, repro_mean=28.800
- nat_siblings top categories by unit count:
  - other: n=43, repro_mean=NA
  - cell_culture: n=32, repro_mean=25.000
  - microscopy_imaging: n=15, repro_mean=24.067
  - molecular_cloning: n=12, repro_mean=19.500
  - dna_rna_extraction: n=10, repro_mean=19.800

## Model Correlation
- group=all (n=34): pearson_total=0.467, pearson_repro=0.355, spearman_total=NA, spearman_repro=NA
- group=nat_protocols (n=14): pearson_total=0.420, pearson_repro=0.001, spearman_total=NA, spearman_repro=NA
- group=nat_siblings (n=20): pearson_total=0.400, pearson_repro=0.313, spearman_total=NA, spearman_repro=NA

## Artifacts
- Score comparisons: `pilot_compare_repro_summary.md`, `pilot_compare_repro_pairwise.csv`
- Repro tests: `repro_group_significance.md`, `repro_group_jitter_box.png`
- Correlation plots: `model_correlation_total_grid.png`, `model_correlation_repro_grid.png`
- Flow tables: `pilot_flow_paper_metrics.csv`, `pilot_flow_group_summary.csv`
- Category tables: `pilot_category_distribution_long.csv`, `pilot_category_scores_long.csv`
