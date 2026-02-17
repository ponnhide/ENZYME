# ENZYME v7 論文調サマリー（JA）
## Nat Protocols vs Nat siblings (n=34)
- Models: gpt-oss-120b-v7, qwen3-next-80b-a3b-instruct-fp8-v7
---
# 背景と狙い
- 課題: 自然言語Methodsは比較・監査が難しい
- 思想: QUEENの「計算可能な履歴表現」をプロトコルへ拡張
- ENZYME: 形式化 -> 検証 -> スコアリング -> 比較
---
# ENZYME設計（コア）
- Core ops: allocate / transfer / manipulate / run_device / observe / annotate / dispose
- HL-core と direct-core の2経路
- measureはrun_device+observeへlowering
- flowはmaterial/logical/combinedで評価
---
# スコアリング設計
- default total: 9成分の等重み平均
- repro: profile駆動（資材、装置、params、QC、traceability など）
- total_mode = equal_average_non_flow
- flowはviability gateとして運用
---
# 定量結果（paper平均）
- gpt-oss-120b-v7: protocols total/repro = 75.035/27.239
- gpt-oss-120b-v7: siblings total/repro = 72.126/23.188
- qwen3-next-80b-a3b-instruct-fp8-v7: protocols total/repro = 72.836/25.814
- qwen3-next-80b-a3b-instruct-fp8-v7: siblings total/repro = 66.691/19.065
---
# 統計・相関
- gpt-oss-120b-v7 repro群差: MWU p=0.096380
- qwen3-next-80b-a3b-instruct-fp8-v7 repro群差: MWU p=0.031225
- 相関(all): pearson_total=0.467
- 相関(all): pearson_repro=0.355
---
# 議論
- 群平均傾向を再現し、再現性評価の計量化に成功
- 単一スコアではなく flow・カテゴリまで診断できる
- logical_flow と unit分割の改善が次の中心課題
---
# 今後の発展
- Nat Protocols全体への拡張
- profile寄与の事後推定（重み学習）
- QUEEN的なトレーサビリティ統合
- 生命科学Methodsの客観監査基盤へ
