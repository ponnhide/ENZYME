# Pilot Comparison Summary

- Compared papers: 34
- Default wins (gpt_directcore/qwen_directcore/Tie): 16/14/4
- Repro wins (gpt_directcore/qwen_directcore/Tie): 15/16/3
- Mean delta default (gpt_directcore-qwen_directcore): 0.903
- Mean delta repro (gpt_directcore-qwen_directcore): -0.105

## gpt_directcore
- papers: 34
- units_total: 327 (mean per paper: 9.62)
- overall_total_mean: 69.299
- overall_total_median: 66.500
- overall_repro_mean: 17.742
- overall_repro_median: 18.900
- nat_protocols: n=14, total_mean=60.800, repro_mean=23.229, units_mean=10.00
- nat_siblings: n=20, total_mean=75.248, repro_mean=13.901, units_mean=9.35

## qwen_directcore
- papers: 34
- units_total: 293 (mean per paper: 8.62)
- overall_total_mean: 68.396
- overall_total_median: 66.450
- overall_repro_mean: 17.847
- overall_repro_median: 18.807
- nat_protocols: n=14, total_mean=61.383, repro_mean=22.265, units_mean=9.57
- nat_siblings: n=20, total_mean=73.305, repro_mean=14.754, units_mean=7.95

## Protocols vs Siblings Delta
- gpt_directcore: total(protocols-siblings)=-14.448, repro(protocols-siblings)=9.328
- qwen_directcore: total(protocols-siblings)=-11.922, repro(protocols-siblings)=7.511
