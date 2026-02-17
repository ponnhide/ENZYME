# ENZYME v7 全件比較（JA）
## Nat Protocols vs Nat Siblings
- 34 papers (protocols=14, siblings=20)
- Models: gpt-oss-120b-v7, qwen3-next-80b-a3b-instruct-fp8-v7
---
# スコア全体
- gpt-oss-120b-v7
- total: protocols 75.035 vs siblings 72.126
- repro: protocols 27.239 vs siblings 23.188
- qwen3-next-80b-a3b-instruct-fp8-v7
- total: protocols 72.836 vs siblings 66.691
- repro: protocols 25.814 vs siblings 19.065
---
# 解釈
- 両モデルで protocols > siblings（total/repro）
- ただし paper-level のモデル一致は中程度
- repro群差は Qwen で有意、GPTは有意傾向
---
# 参照図
- repro_group_jitter_box.png
- model_correlation_total_grid.png
- model_correlation_repro_grid.png
