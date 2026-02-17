# ENZYME v7 Full Comparison (EN)
## Nat Protocols vs Nat Siblings
- 34 papers (protocols=14, siblings=20)
- Models: gpt-oss-120b-v7, qwen3-next-80b-a3b-instruct-fp8-v7
---
# Score Summary
- gpt-oss-120b-v7
- total: protocols 75.035 vs siblings 72.126
- repro: protocols 27.239 vs siblings 23.188
- qwen3-next-80b-a3b-instruct-fp8-v7
- total: protocols 72.836 vs siblings 66.691
- repro: protocols 25.814 vs siblings 19.065
---
# Interpretation
- Both models show protocols > siblings (total and repro)
- Cross-model agreement is moderate at paper level
- Repro group difference is significant for Qwen; trend-level for GPT
---
# Figures
- repro_group_jitter_box.png
- model_correlation_total_grid.png
- model_correlation_repro_grid.png
