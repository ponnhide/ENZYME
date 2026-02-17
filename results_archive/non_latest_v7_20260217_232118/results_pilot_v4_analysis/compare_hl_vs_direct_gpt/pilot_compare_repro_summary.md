# Pilot Comparison Summary

- Compared papers: 34
- Default wins (gpt_hlcore/gpt_directcore/Tie): 1/33/0
- Repro wins (gpt_hlcore/gpt_directcore/Tie): 22/7/5
- Mean delta default (gpt_hlcore-gpt_directcore): -10.575
- Mean delta repro (gpt_hlcore-gpt_directcore): 2.380

## gpt_hlcore
- papers: 34
- units_total: 322 (mean per paper: 9.47)
- overall_total_mean: 58.724
- overall_total_median: 58.850
- overall_repro_mean: 20.122
- overall_repro_median: 20.900
- nat_protocols: n=14, total_mean=55.400, repro_mean=26.193, units_mean=10.00
- nat_siblings: n=20, total_mean=61.051, repro_mean=15.872, units_mean=9.10

## gpt_directcore
- papers: 34
- units_total: 327 (mean per paper: 9.62)
- overall_total_mean: 69.299
- overall_total_median: 66.500
- overall_repro_mean: 17.742
- overall_repro_median: 18.900
- nat_protocols: n=14, total_mean=60.800, repro_mean=23.229, units_mean=10.00
- nat_siblings: n=20, total_mean=75.248, repro_mean=13.901, units_mean=9.35

## Protocols vs Siblings Delta
- gpt_hlcore: total(protocols-siblings)=-5.651, repro(protocols-siblings)=10.321
- gpt_directcore: total(protocols-siblings)=-14.448, repro(protocols-siblings)=9.328
