# Pilot Integrated Report (Scores + Categories + Flow)

## Scope
- Corpus: nat_protocols (14 papers) + nat_siblings (20 papers), total 34 papers.
- Models: gpt-oss-120b-high-hlcore (0 units), qwen3-next-80b-a3b-instruct-fp8-hlcore (0 units).

## Score Summary
### gpt-oss-120b-high-hlcore
- total mean (protocols/siblings): NA / NA
- repro mean (protocols/siblings): NA / NA
- delta total (protocols-siblings): 0.000
- delta repro (protocols-siblings): 0.000
### qwen3-next-80b-a3b-instruct-fp8-hlcore
- total mean (protocols/siblings): NA / NA
- repro mean (protocols/siblings): NA / NA
- delta total (protocols-siblings): 0.000
- delta repro (protocols-siblings): 0.000

## Repro Significance (nat_protocols vs nat_siblings)
### gpt_hlcore
- Mann-Whitney p(two-sided): 0.000708
- Welch t p(two-sided): 0.000059
- Cohen d: 1.542
- Cliff delta: 0.693
### qwen_hlcore
- Mann-Whitney p(two-sided): 0.000274
- Welch t p(two-sided): 0.000033
- Cohen d: 1.644
- Cliff delta: 0.739

## Flow Connectivity Summary
### gpt-oss-120b-high-hlcore / nat_protocols
- papers: 14
- mean nodes per paper: 10.000
- mean material edges: 3.357
- mean logical edges: 7.000
- nonzero-edge rate (material/logical): 0.786 / 0.857
- combined pass rate: 0.286
- combined isolated rate mean: 0.321
- corr(repro, connectivity=1-isolated_rate): 0.708
### gpt-oss-120b-high-hlcore / nat_siblings
- papers: 20
- mean nodes per paper: 9.100
- mean material edges: 0.950
- mean logical edges: 2.100
- nonzero-edge rate (material/logical): 0.300 / 0.750
- combined pass rate: 0.000
- combined isolated rate mean: 0.613
- corr(repro, connectivity=1-isolated_rate): 0.765
### qwen3-next-80b-a3b-instruct-fp8-hlcore / nat_protocols
- papers: 14
- mean nodes per paper: 9.500
- mean material edges: 2.071
- mean logical edges: 10.929
- nonzero-edge rate (material/logical): 0.571 / 1.000
- combined pass rate: 0.643
- combined isolated rate mean: 0.121
- corr(repro, connectivity=1-isolated_rate): 0.211
### qwen3-next-80b-a3b-instruct-fp8-hlcore / nat_siblings
- papers: 20
- mean nodes per paper: 7.800
- mean material edges: 2.400
- mean logical edges: 3.350
- nonzero-edge rate (material/logical): 0.250 / 0.800
- combined pass rate: 0.200
- combined isolated rate mean: 0.493
- corr(repro, connectivity=1-isolated_rate): 0.523

## Category Highlights (unit-level)
### gpt-oss-120b-high-hlcore
- nat_protocols top categories by unit count:
  - cell_culture: n=81, repro_mean=29.062
  - centrifugation: n=31, repro_mean=29.548
  - other: n=28, repro_mean=NA
  - microscopy_imaging: n=13, repro_mean=33.462
  - dna_rna_extraction: n=8, repro_mean=21.000
- nat_siblings top categories by unit count:
  - other: n=107, repro_mean=NA
  - cell_culture: n=23, repro_mean=28.783
  - sequencing_library_prep: n=18, repro_mean=14.444
  - molecular_cloning: n=15, repro_mean=14.600
  - microscopy_imaging: n=13, repro_mean=23.308
### qwen3-next-80b-a3b-instruct-fp8-hlcore
- nat_protocols top categories by unit count:
  - cell_culture: n=91, repro_mean=23.165
  - microscopy_imaging: n=33, repro_mean=24.485
  - centrifugation: n=29, repro_mean=26.655
  - other: n=23, repro_mean=NA
  - dna_rna_extraction: n=21, repro_mean=22.905
- nat_siblings top categories by unit count:
  - other: n=79, repro_mean=NA
  - cell_culture: n=26, repro_mean=19.385
  - sequencing_library_prep: n=21, repro_mean=12.381
  - molecular_cloning: n=17, repro_mean=10.176
  - dna_rna_extraction: n=14, repro_mean=13.500

## Model Correlation
- group=all (n=34): pearson_total=0.596, pearson_repro=0.749, spearman_total=NA, spearman_repro=NA
- group=nat_protocols (n=14): pearson_total=-0.031, pearson_repro=-0.019, spearman_total=NA, spearman_repro=NA
- group=nat_siblings (n=20): pearson_total=0.609, pearson_repro=0.857, spearman_total=NA, spearman_repro=NA

## Artifacts
- Score comparisons: `pilot_compare_repro_summary.md`, `pilot_compare_repro_pairwise.csv`
- Repro tests: `repro_group_significance.md`, `repro_group_jitter_box.png`
- Correlation plots: `model_correlation_total_grid.png`, `model_correlation_repro_grid.png`
- Flow tables: `pilot_flow_paper_metrics.csv`, `pilot_flow_group_summary.csv`
- Category tables: `pilot_category_distribution_long.csv`, `pilot_category_scores_long.csv`
