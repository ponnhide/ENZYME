# Pilot Integrated Report (Scores + Categories + Flow)

## Scope
- Corpus: nat_protocols (14 papers) + nat_siblings (20 papers), total 34 papers.
- Models: gpt-oss-120b-high-hlcore (0 units), gpt-oss-120b-high-directcore (0 units).

## Score Summary
### gpt-oss-120b-high-hlcore
- total mean (protocols/siblings): NA / NA
- repro mean (protocols/siblings): NA / NA
- delta total (protocols-siblings): 0.000
- delta repro (protocols-siblings): 0.000
### gpt-oss-120b-high-directcore
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
### gpt_hlcore
- Mann-Whitney p(two-sided): 0.000708
- Welch t p(two-sided): 0.000059
- Cohen d: 1.542
- Cliff delta: 0.693

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

## Model Correlation
- group=all (n=34): pearson_total=0.811, pearson_repro=0.828, spearman_total=NA, spearman_repro=NA
- group=nat_protocols (n=14): pearson_total=0.309, pearson_repro=0.034, spearman_total=NA, spearman_repro=NA
- group=nat_siblings (n=20): pearson_total=0.815, pearson_repro=0.957, spearman_total=NA, spearman_repro=NA

## Artifacts
- Score comparisons: `pilot_compare_repro_summary.md`, `pilot_compare_repro_pairwise.csv`
- Repro tests: `repro_group_significance.md`, `repro_group_jitter_box.png`
- Correlation plots: `model_correlation_total_grid.png`, `model_correlation_repro_grid.png`
- Flow tables: `pilot_flow_paper_metrics.csv`, `pilot_flow_group_summary.csv`
- Category tables: `pilot_category_distribution_long.csv`, `pilot_category_scores_long.csv`
