# Pilot Comparison Summary

- Compared papers: 34
- Default wins (gpt-oss-120b-v7/qwen3-next-80b-a3b-instruct-fp8-v7/Tie): 28/5/1
- Repro wins (gpt-oss-120b-v7/qwen3-next-80b-a3b-instruct-fp8-v7/Tie): 19/14/1
- Mean delta default (gpt-oss-120b-v7-qwen3-next-80b-a3b-instruct-fp8-v7): 4.102
- Mean delta repro (gpt-oss-120b-v7-qwen3-next-80b-a3b-instruct-fp8-v7): 3.012

## gpt-oss-120b-v7
- papers: 34
- units_total: 228 (mean per paper: 6.71)
- overall_total_mean: 73.324
- overall_total_median: 74.562
- overall_repro_mean: 24.856
- overall_repro_median: 25.285
- nat_protocols: n=14, total_mean=75.035, repro_mean=27.239, units_mean=9.14
- nat_siblings: n=20, total_mean=72.126, repro_mean=23.188, units_mean=5.00

## qwen3-next-80b-a3b-instruct-fp8-v7
- papers: 34
- units_total: 231 (mean per paper: 6.79)
- overall_total_mean: 69.221
- overall_total_median: 70.389
- overall_repro_mean: 21.844
- overall_repro_median: 24.967
- nat_protocols: n=14, total_mean=72.836, repro_mean=25.814, units_mean=8.50
- nat_siblings: n=20, total_mean=66.691, repro_mean=19.065, units_mean=5.60

## Protocols vs Siblings Delta
- gpt-oss-120b-v7: total(protocols-siblings)=2.909, repro(protocols-siblings)=4.051
- qwen3-next-80b-a3b-instruct-fp8-v7: total(protocols-siblings)=6.145, repro(protocols-siblings)=6.748
