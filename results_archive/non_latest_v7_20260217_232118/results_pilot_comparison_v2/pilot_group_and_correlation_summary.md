# Group Comparison and Model Correlation (v2)

## nat_protocols vs nat_siblings (within each model)
- gpt-oss-120b-medium-v2 / total_100: protocols n=14 mean=57.986, siblings n=20 mean=69.785, delta(protocols-siblings)=-11.799, cohen_d=-1.452
- gpt-oss-120b-medium-v2 / repro_100: protocols n=14 mean=26.986, siblings n=20 mean=16.548, delta(protocols-siblings)=10.438, cohen_d=1.732
- qwen3-next-80b-a3b-instruct-fp8-v2 / total_100: protocols n=14 mean=59.316, siblings n=20 mean=77.558, delta(protocols-siblings)=-18.242, cohen_d=-2.110
- qwen3-next-80b-a3b-instruct-fp8-v2 / repro_100: protocols n=14 mean=23.971, siblings n=20 mean=11.691, delta(protocols-siblings)=12.280, cohen_d=2.134

## Qwen vs gpt-oss correlation (paper-level means)
- Model columns: total=(gpt-oss-120b-medium-v2_total vs qwen3-next-80b-a3b-instruct-fp8-v2_total), repro=(gpt-oss-120b-medium-v2_repro vs qwen3-next-80b-a3b-instruct-fp8-v2_repro)
- group=all (n=34): pearson_total=0.735, spearman_total=0.746, pearson_repro=0.760, spearman_repro=0.735
- group=nat_protocols (n=14): pearson_total=-0.056, spearman_total=0.007, pearson_repro=-0.131, spearman_repro=-0.191
- group=nat_siblings (n=20): pearson_total=0.761, spearman_total=0.768, pearson_repro=0.795, spearman_repro=0.771
