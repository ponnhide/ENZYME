# Pilot Comparison Summary

- Compared papers: 34
- Default wins (gpt_hlcore/qwen_hlcore/Tie): 9/20/5
- Repro wins (gpt_hlcore/qwen_hlcore/Tie): 22/6/6
- Mean delta default (gpt_hlcore-qwen_hlcore): -2.317
- Mean delta repro (gpt_hlcore-qwen_hlcore): 3.966

## gpt_hlcore
- papers: 34
- units_total: 322 (mean per paper: 9.47)
- overall_total_mean: 58.724
- overall_total_median: 58.850
- overall_repro_mean: 20.122
- overall_repro_median: 20.900
- nat_protocols: n=14, total_mean=55.400, repro_mean=26.193, units_mean=10.00
- nat_siblings: n=20, total_mean=61.051, repro_mean=15.872, units_mean=9.10

## qwen_hlcore
- papers: 34
- units_total: 289 (mean per paper: 8.50)
- overall_total_mean: 61.041
- overall_total_median: 62.700
- overall_repro_mean: 16.155
- overall_repro_median: 16.500
- nat_protocols: n=14, total_mean=56.718, repro_mean=21.586, units_mean=9.50
- nat_siblings: n=20, total_mean=64.067, repro_mean=12.354, units_mean=7.80

## Protocols vs Siblings Delta
- gpt_hlcore: total(protocols-siblings)=-5.651, repro(protocols-siblings)=10.321
- qwen_hlcore: total(protocols-siblings)=-7.349, repro(protocols-siblings)=9.232
