# Pilot Comparison Summary (v2)

- Compared papers: 34
- Default wins (GPT/Qwen/Tie): 9/23/2
- Repro wins (GPT/Qwen/Tie): 24/5/5
- Mean delta default (GPT-Qwen): -5.120
- Mean delta repro (GPT-Qwen): 4.098

## gpt-oss-120b-medium-v2
- papers: 34
- units_total: 315 (mean per paper: 9.26)
- overall_total_mean: 64.926
- overall_total_median: 62.300
- overall_repro_mean: 20.846
- overall_repro_median: 23.900
- nat_protocols: n=14, total_mean=57.986, repro_mean=26.986, units_mean=10.00
- nat_siblings: n=20, total_mean=69.785, repro_mean=16.548, units_mean=8.75

## qwen3-next-80b-a3b-instruct-fp8-v2
- papers: 34
- units_total: 288 (mean per paper: 8.47)
- overall_total_mean: 70.047
- overall_total_median: 70.900
- overall_repro_mean: 16.748
- overall_repro_median: 16.400
- nat_protocols: n=14, total_mean=59.316, repro_mean=23.971, units_mean=9.50
- nat_siblings: n=20, total_mean=77.558, repro_mean=11.691, units_mean=7.75

## Protocols vs Siblings Delta
- gpt-oss-120b-medium-v2: total(protocols-siblings)=-11.799, repro(protocols-siblings)=10.438
- qwen3-next-80b-a3b-instruct-fp8-v2: total(protocols-siblings)=-18.242, repro(protocols-siblings)=12.280
