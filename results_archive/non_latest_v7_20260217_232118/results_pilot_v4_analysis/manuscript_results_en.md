# ENZYME Pilot Results (v4)

## Results

### 1. Evaluation setup and completion status
We evaluated 34 papers in total (`nat_protocols`: 14, `nat_siblings`: 20) under four conditions: two models (`gpt-oss-120b`, `Qwen3-Next-80B-A3B-Instruct-FP8`) and two formalization paths (`hl-core`, `direct-core`). Reproducibility scoring used a unified strict profile (`profiles/reproducibility_profile.strict.v0_1.json`).

All four runs completed 34/34 papers. Unit-level scored outputs were `gpt_hlcore=322`, `gpt_directcore=326`, `qwen_hlcore=288`, and `qwen_directcore=293`. Only one failed unit was observed in `gpt_directcore` and one in `qwen_hlcore`.

### 2. Group-level pattern in total vs reproducibility
A shared pattern appeared across all runs: `nat_siblings` had higher `total` scores, while `nat_protocols` had higher `repro` scores.

| Run | total mean (all) | repro mean (all) | total Δ(protocols-siblings) | repro Δ(protocols-siblings) |
|---|---:|---:|---:|---:|
| gpt_hlcore | 58.724 | 20.122 | -5.651 | +10.321 |
| gpt_directcore | 69.299 | 17.742 | -14.448 | +9.328 |
| qwen_hlcore | 61.041 | 16.155 | -7.349 | +9.232 |
| qwen_directcore | 68.396 | 17.847 | -11.922 | +7.511 |

Thus, siblings favored coverage (`total`), whereas protocols favored reproducibility-oriented completeness (`repro`), consistently across model and IR route.

### 3. Statistical evidence for reproducibility separation
The repro gap between `nat_protocols` and `nat_siblings` was significant in all four runs, with medium-to-large effect sizes.

- `gpt_hlcore`: Mann-Whitney p=0.000708, Welch p=5.91e-05, Cohen's d=1.542, Cliff's delta=0.693
- `gpt_directcore`: Mann-Whitney p=0.000186, Welch p=3.87e-06, Cohen's d=1.818, Cliff's delta=0.764
- `qwen_hlcore`: Mann-Whitney p=0.000274, Welch p=3.30e-05, Cohen's d=1.644, Cliff's delta=0.739
- `qwen_directcore`: Mann-Whitney p=0.014847, Welch p=0.001406, Cohen's d=1.133, Cliff's delta=0.500

These results indicate that the current repro scoring system reliably detects group-level reproducibility differences.

### 4. Cross-model consistency (Qwen vs GPT)
Cross-model agreement was stronger in `direct-core` than in `hl-core`.

- `gpt_vs_qwen_hlcore` (all): pearson_total=0.596, pearson_repro=0.749
- `gpt_vs_qwen_directcore` (all): pearson_total=0.822, pearson_repro=0.815

However, within `nat_protocols`, paper-wise ranking agreement remained weak (e.g., `hl-core` repro correlation: -0.019). This means macro trends (group means) align, while micro ranking (paper difficulty ordering) is still model-dependent.

### 5. Flow metrics (material/logical/combined)
`combined_isolated_rate` was consistently lower in `nat_protocols` than in `nat_siblings`, suggesting stronger inter-unit connectivity in protocol-oriented papers.

- gpt_hlcore: protocols 0.321 vs siblings 0.613
- gpt_directcore: protocols 0.400 vs siblings 0.629
- qwen_hlcore: protocols 0.121 vs siblings 0.493
- qwen_directcore: protocols 0.186 vs siblings 0.524

In `direct-core`, GPT runs produced near-zero material edges (mean 0.0 for both groups), while Qwen retained a small number of material edges (0.14/0.50). This indicates route/model-dependent lowering and extraction behavior.

### 6. Unit category distribution
Category distributions were broadly stable across runs, with `cell_culture`, `sequencing_library_prep`, `molecular_cloning`, and `microscopy_imaging` repeatedly emerging as major categories.

- `nat_protocols`: `cell_culture` was the dominant category (e.g., Qwen direct-core: n=91)
- `nat_siblings`: `other` was dominant (e.g., GPT direct-core: n=106)

This supports that ENZYME category assignment can capture corpus-level methodological differences between protocol-focused and broader-method papers.

### 7. Interim conclusion at pilot scale
At this 34-paper scale, ENZYME already provides a practical basis for:

1. comparable formal representations (HL/Core),
2. decoupled evaluation of coverage (`total`) and reproducibility (`repro`),
3. connectivity diagnostics via flow metrics, and
4. experiment-type profiling via unit categories.

Overall, these pilot results support ENZYME as a viable framework for turning life-science methods text into quantitatively comparable structured objects.

## Referenced artifacts
- `results_pilot_v4_analysis/pilot_v4_overview.md`
- `results_pilot_v4_analysis/pilot_v4_run_summary.csv`
- `results_pilot_v4_analysis/pilot_v4_group_summary.csv`
- `results_pilot_v4_analysis/compare_gpt_vs_qwen_hlcore/`
- `results_pilot_v4_analysis/compare_gpt_vs_qwen_directcore/`
- `results_pilot_v4_analysis/compare_hl_vs_direct_gpt/`
- `results_pilot_v4_analysis/compare_hl_vs_direct_qwen/`
