# Pilot v4 Overview (4-run)

## Runs
- gpt_hlcore: papers=34, units=322, mean_total=58.724, mean_repro=20.122, failed_units=0
- gpt_directcore: papers=34, units=327, mean_total=69.299, mean_repro=17.742, failed_units=1
- qwen_hlcore: papers=34, units=289, mean_total=61.041, mean_repro=16.155, failed_units=1
- qwen_directcore: papers=34, units=293, mean_total=68.396, mean_repro=17.847, failed_units=0

## Group Means (paper-level)
- gpt_hlcore: total protocols=55.400 vs siblings=61.051 (Δ=-5.651); repro protocols=26.193 vs siblings=15.872 (Δ=10.321)
- gpt_directcore: total protocols=60.800 vs siblings=75.248 (Δ=-14.448); repro protocols=23.229 vs siblings=13.901 (Δ=9.328)
- qwen_hlcore: total protocols=56.718 vs siblings=64.067 (Δ=-7.349); repro protocols=21.586 vs siblings=12.354 (Δ=9.232)
- qwen_directcore: total protocols=61.383 vs siblings=73.305 (Δ=-11.922); repro protocols=22.265 vs siblings=14.754 (Δ=7.511)

## Pairwise Correlations (from compare outputs)
### gpt_vs_qwen_hlcore
- all (n=34): pearson_total=0.5957344038742228, pearson_repro=0.7485362999645048, spearman_total=NA, spearman_repro=NA
- nat_protocols (n=14): pearson_total=-0.030887189560538073, pearson_repro=-0.019256198598884593, spearman_total=NA, spearman_repro=NA
- nat_siblings (n=20): pearson_total=0.6094806081950721, pearson_repro=0.8572491202583526, spearman_total=NA, spearman_repro=NA
### gpt_vs_qwen_directcore
- all (n=34): pearson_total=0.8223797972423453, pearson_repro=0.8148968719232096, spearman_total=NA, spearman_repro=NA
- nat_protocols (n=14): pearson_total=0.08950960088109357, pearson_repro=0.29013640854543205, spearman_total=NA, spearman_repro=NA
- nat_siblings (n=20): pearson_total=0.9359709366850991, pearson_repro=0.8908741890059612, spearman_total=NA, spearman_repro=NA
### hl_vs_direct_gpt
- all (n=34): pearson_total=0.8105870751225713, pearson_repro=0.8280692553457862, spearman_total=NA, spearman_repro=NA
- nat_protocols (n=14): pearson_total=0.309108218830615, pearson_repro=0.03406847831497345, spearman_total=NA, spearman_repro=NA
- nat_siblings (n=20): pearson_total=0.8153728222296205, pearson_repro=0.9572829316630177, spearman_total=NA, spearman_repro=NA
### hl_vs_direct_qwen
- all (n=34): pearson_total=0.8818244314326676, pearson_repro=0.920824575879422, spearman_total=NA, spearman_repro=NA
- nat_protocols (n=14): pearson_total=0.8163995809910324, pearson_repro=0.8076826804972634, spearman_total=NA, spearman_repro=NA
- nat_siblings (n=20): pearson_total=0.8688897569395457, pearson_repro=0.9485949104412865, spearman_total=NA, spearman_repro=NA

## Repro Significance (protocols vs siblings)
### gpt_vs_qwen_hlcore
- gpt_hlcore: mannwhitney_p=0.0007082071639880739, welch_p=5.911073696540864e-05, cohen_d=1.5418385144819642, cliffs_delta=0.6928571428571428
- qwen_hlcore: mannwhitney_p=0.00027442428202305736, welch_p=3.2965771242545204e-05, cohen_d=1.6435657387596896, cliffs_delta=0.7392857142857143
### gpt_vs_qwen_directcore
- gpt_directcore: mannwhitney_p=0.00018621755389202225, welch_p=3.871288346718843e-06, cohen_d=1.8184283440033961, cliffs_delta=0.7642857142857142
- qwen_directcore: mannwhitney_p=0.01484694463031733, welch_p=0.001405807912986673, cohen_d=1.132737828418396, cliffs_delta=0.5
### hl_vs_direct_gpt
- gpt_directcore: mannwhitney_p=0.00018621755389202225, welch_p=3.871288346718843e-06, cohen_d=1.8184283440033961, cliffs_delta=0.7642857142857142
- gpt_hlcore: mannwhitney_p=0.0007082071639880739, welch_p=5.911073696540864e-05, cohen_d=1.5418385144819642, cliffs_delta=0.6928571428571428
### hl_vs_direct_qwen
- qwen_directcore: mannwhitney_p=0.01484694463031733, welch_p=0.001405807912986673, cohen_d=1.132737828418396, cliffs_delta=0.5
- qwen_hlcore: mannwhitney_p=0.00027442428202305736, welch_p=3.2965771242545204e-05, cohen_d=1.6435657387596896, cliffs_delta=0.7392857142857143

## Artifacts
- `pilot_v4_run_summary.csv`
- `pilot_v4_group_summary.csv`
- `pilot_v4_failure_summary.csv`
- `compare_*/pilot_integrated_report.md`
