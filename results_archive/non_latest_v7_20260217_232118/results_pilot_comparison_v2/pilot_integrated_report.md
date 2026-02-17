# Pilot Integrated Report (Scores + Categories + Flow)

## Scope
- Corpus: nat_protocols (14 papers) + nat_siblings (20 papers), total 34 papers.
- Models: gpt-oss-120b-medium-v2 (315 units), qwen3-next-80b-a3b-instruct-fp8-v2 (288 units).

## Score Summary
### gpt-oss-120b-medium-v2
- total mean (protocols/siblings): 57.986 / 69.785
- repro mean (protocols/siblings): 26.986 / 16.548
- delta total (protocols-siblings): -11.799
- delta repro (protocols-siblings): 10.438
### qwen3-next-80b-a3b-instruct-fp8-v2
- total mean (protocols/siblings): 59.316 / 77.558
- repro mean (protocols/siblings): 23.971 / 11.691
- delta total (protocols-siblings): -18.242
- delta repro (protocols-siblings): 12.280

## Repro Significance (nat_protocols vs nat_siblings)
### gpt-oss-120b-medium-v2
- Mann-Whitney p(two-sided): 0.000404
- Welch t p(two-sided): 0.000005
- Cohen d: 1.732
- Cliff delta: 0.725
### qwen3-next-80b-a3b-instruct-fp8-v2
- Mann-Whitney p(two-sided): 0.000011
- Welch t p(two-sided): 0.000001
- Cohen d: 2.134
- Cliff delta: 0.882

## Flow Connectivity Summary
### gpt-oss-120b-medium-v2 / nat_protocols
- papers: 14
- mean nodes per paper: 10.000
- mean material edges: 2.714
- mean logical edges: 4.857
- nonzero-edge rate (material/logical): 0.500 / 0.857
- combined pass rate: 0.143
- combined isolated rate mean: 0.400
- corr(repro, connectivity=1-isolated_rate): 0.690
### gpt-oss-120b-medium-v2 / nat_siblings
- papers: 20
- mean nodes per paper: 8.750
- mean material edges: 1.000
- mean logical edges: 1.600
- nonzero-edge rate (material/logical): 0.300 / 0.700
- combined pass rate: 0.000
- combined isolated rate mean: 0.658
- corr(repro, connectivity=1-isolated_rate): 0.758
### qwen3-next-80b-a3b-instruct-fp8-v2 / nat_protocols
- papers: 14
- mean nodes per paper: 9.500
- mean material edges: 3.571
- mean logical edges: 9.357
- nonzero-edge rate (material/logical): 0.643 / 1.000
- combined pass rate: 0.571
- combined isolated rate mean: 0.179
- corr(repro, connectivity=1-isolated_rate): 0.658
### qwen3-next-80b-a3b-instruct-fp8-v2 / nat_siblings
- papers: 20
- mean nodes per paper: 7.750
- mean material edges: 3.050
- mean logical edges: 3.300
- nonzero-edge rate (material/logical): 0.300 / 0.800
- combined pass rate: 0.100
- combined isolated rate mean: 0.503
- corr(repro, connectivity=1-isolated_rate): 0.606

## Category Highlights (unit-level)
### gpt-oss-120b-medium-v2
- nat_protocols top categories by unit count:
  - cell_culture: n=81, repro_mean=28.210
  - other: n=33, repro_mean=NA
  - centrifugation: n=26, repro_mean=28.846
  - microscopy_imaging: n=9, repro_mean=37.444
  - flow_cytometry: n=7, repro_mean=29.000
- nat_siblings top categories by unit count:
  - other: n=106, repro_mean=NA
  - cell_culture: n=20, repro_mean=29.850
  - sequencing_library_prep: n=17, repro_mean=19.059
  - microscopy_imaging: n=15, repro_mean=18.667
  - molecular_cloning: n=12, repro_mean=17.000
### qwen3-next-80b-a3b-instruct-fp8-v2
- nat_protocols top categories by unit count:
  - cell_culture: n=85, repro_mean=25.835
  - centrifugation: n=33, repro_mean=26.515
  - other: n=27, repro_mean=NA
  - microscopy_imaging: n=20, repro_mean=31.800
  - dna_rna_extraction: n=9, repro_mean=28.444
- nat_siblings top categories by unit count:
  - other: n=79, repro_mean=NA
  - cell_culture: n=28, repro_mean=19.321
  - sequencing_library_prep: n=19, repro_mean=11.895
  - molecular_cloning: n=16, repro_mean=8.000
  - dna_rna_extraction: n=13, repro_mean=14.615

## Model Correlation
- group=all (n=34): pearson_total=0.735, pearson_repro=0.760, spearman_total=0.746, spearman_repro=0.735
- group=nat_protocols (n=14): pearson_total=-0.056, pearson_repro=-0.131, spearman_total=0.007, spearman_repro=-0.191
- group=nat_siblings (n=20): pearson_total=0.761, pearson_repro=0.795, spearman_total=0.768, spearman_repro=0.771

## Artifacts
- Score comparisons: `pilot_compare_repro_summary.md`, `pilot_compare_repro_pairwise.csv`
- Repro tests: `repro_group_significance.md`, `repro_group_jitter_box.png`
- Correlation plots: `model_correlation_total_grid.png`, `model_correlation_repro_grid.png`
- Flow tables: `pilot_flow_paper_metrics.csv`, `pilot_flow_group_summary.csv`
- Category tables: `pilot_category_distribution_long.csv`, `pilot_category_scores_long.csv`
