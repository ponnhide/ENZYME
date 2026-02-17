# Pilot Integrated Report (Scores + Categories + Flow)

## Scope
- Corpus: nat_protocols (14 papers) + nat_siblings (20 papers), total 34 papers.
- Models: gpt-oss-120b-high-directcore (0 units), qwen3-next-80b-a3b-instruct-fp8-directcore (0 units).

## Score Summary
### gpt-oss-120b-high-directcore
- total mean (protocols/siblings): NA / NA
- repro mean (protocols/siblings): NA / NA
- delta total (protocols-siblings): 0.000
- delta repro (protocols-siblings): 0.000
### qwen3-next-80b-a3b-instruct-fp8-directcore
- total mean (protocols/siblings): NA / NA
- repro mean (protocols/siblings): NA / NA
- delta total (protocols-siblings): 0.000
- delta repro (protocols-siblings): 0.000

## Repro Significance (nat_protocols vs nat_siblings)
### gpt_directcore
- Mann-Whitney p(two-sided): 0.000186
- Welch t p(two-sided): 0.000004
- Cohen d: 1.818
- Cliff delta: 0.764
### qwen_directcore
- Mann-Whitney p(two-sided): 0.014847
- Welch t p(two-sided): 0.001406
- Cohen d: 1.133
- Cliff delta: 0.500

## Flow Connectivity Summary
### gpt-oss-120b-high-directcore / nat_protocols
- papers: 14
- mean nodes per paper: 10.000
- mean material edges: 0.000
- mean logical edges: 6.000
- nonzero-edge rate (material/logical): 0.000 / 0.929
- combined pass rate: 0.143
- combined isolated rate mean: 0.400
- corr(repro, connectivity=1-isolated_rate): 0.385
### gpt-oss-120b-high-directcore / nat_siblings
- papers: 20
- mean nodes per paper: 9.350
- mean material edges: 0.000
- mean logical edges: 2.650
- nonzero-edge rate (material/logical): 0.000 / 0.750
- combined pass rate: 0.050
- combined isolated rate mean: 0.629
- corr(repro, connectivity=1-isolated_rate): 0.530
### qwen3-next-80b-a3b-instruct-fp8-directcore / nat_protocols
- papers: 14
- mean nodes per paper: 9.571
- mean material edges: 0.143
- mean logical edges: 11.429
- nonzero-edge rate (material/logical): 0.143 / 1.000
- combined pass rate: 0.643
- combined isolated rate mean: 0.186
- corr(repro, connectivity=1-isolated_rate): 0.590
### qwen3-next-80b-a3b-instruct-fp8-directcore / nat_siblings
- papers: 20
- mean nodes per paper: 7.950
- mean material edges: 0.500
- mean logical edges: 3.750
- nonzero-edge rate (material/logical): 0.100 / 0.800
- combined pass rate: 0.150
- combined isolated rate mean: 0.524
- corr(repro, connectivity=1-isolated_rate): 0.479

## Category Highlights (unit-level)
### gpt-oss-120b-high-directcore
- nat_protocols top categories by unit count:
  - cell_culture: n=78, repro_mean=24.872
  - other: n=38, repro_mean=NA
  - centrifugation: n=28, repro_mean=20.964
  - microscopy_imaging: n=14, repro_mean=29.429
  - flow_cytometry: n=7, repro_mean=25.429
- nat_siblings top categories by unit count:
  - other: n=106, repro_mean=NA
  - cell_culture: n=23, repro_mean=25.304
  - sequencing_library_prep: n=19, repro_mean=15.947
  - microscopy_imaging: n=17, repro_mean=19.588
  - molecular_cloning: n=16, repro_mean=11.375
### qwen3-next-80b-a3b-instruct-fp8-directcore
- nat_protocols top categories by unit count:
  - cell_culture: n=91, repro_mean=24.044
  - microscopy_imaging: n=33, repro_mean=25.030
  - centrifugation: n=28, repro_mean=26.536
  - other: n=24, repro_mean=NA
  - dna_rna_extraction: n=20, repro_mean=25.550
- nat_siblings top categories by unit count:
  - other: n=77, repro_mean=NA
  - cell_culture: n=30, repro_mean=22.733
  - sequencing_library_prep: n=20, repro_mean=16.800
  - microscopy_imaging: n=16, repro_mean=15.625
  - molecular_cloning: n=16, repro_mean=12.250

## Model Correlation
- group=all (n=34): pearson_total=0.822, pearson_repro=0.815, spearman_total=NA, spearman_repro=NA
- group=nat_protocols (n=14): pearson_total=0.090, pearson_repro=0.290, spearman_total=NA, spearman_repro=NA
- group=nat_siblings (n=20): pearson_total=0.936, pearson_repro=0.891, spearman_total=NA, spearman_repro=NA

## Artifacts
- Score comparisons: `pilot_compare_repro_summary.md`, `pilot_compare_repro_pairwise.csv`
- Repro tests: `repro_group_significance.md`, `repro_group_jitter_box.png`
- Correlation plots: `model_correlation_total_grid.png`, `model_correlation_repro_grid.png`
- Flow tables: `pilot_flow_paper_metrics.csv`, `pilot_flow_group_summary.csv`
- Category tables: `pilot_category_distribution_long.csv`, `pilot_category_scores_long.csv`
