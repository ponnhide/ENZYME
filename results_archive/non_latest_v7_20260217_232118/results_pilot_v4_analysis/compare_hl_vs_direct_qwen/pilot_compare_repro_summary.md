# Pilot Comparison Summary

- Compared papers: 34
- Default wins (qwen_hlcore/qwen_directcore/Tie): 4/30/0
- Repro wins (qwen_hlcore/qwen_directcore/Tie): 10/19/5
- Mean delta default (qwen_hlcore-qwen_directcore): -7.355
- Mean delta repro (qwen_hlcore-qwen_directcore): -1.692

## qwen_hlcore
- papers: 34
- units_total: 289 (mean per paper: 8.50)
- overall_total_mean: 61.041
- overall_total_median: 62.700
- overall_repro_mean: 16.155
- overall_repro_median: 16.500
- nat_protocols: n=14, total_mean=56.718, repro_mean=21.586, units_mean=9.50
- nat_siblings: n=20, total_mean=64.067, repro_mean=12.354, units_mean=7.80

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
- qwen_hlcore: total(protocols-siblings)=-7.349, repro(protocols-siblings)=9.232
- qwen_directcore: total(protocols-siblings)=-11.922, repro(protocols-siblings)=7.511
