# ENZYME パイロット結果
## Nat Protocols vs Nat Siblings
### GPT-OSS と Qwen での形式化・再現性評価

- 対象: 34論文（protocols 14 / siblings 20）
- モデル: `gpt-oss-120b-medium-v2`, `qwen3-next-80b-a3b-instruct-fp8-v2`
- 出典: `results_pilot_comparison_v2/*`

---

## 背景思想（QUEENとの関係）

- 参照論文: Nature Communications 2022, `s41467-022-30588-x`
- 要点:
  - 複雑なプロセスを最小操作に還元
  - 操作履歴を保持し再生成可能性を高める
- ENZYMEの対応:
  - Core関数を最小化
  - 高級手順はLoweringでCoreへ
  - 履歴/根拠をJSONで保持

---

## ENZYME実装（E2E）

- CLI: `import -> compile -> validate -> score -> report`
- 実装根拠:
  - `src/enzyme/cli.py:33-105`
  - `src/enzyme/lowering.py:29-136`
  - `src/enzyme/validator.py:372-395`
  - `src/enzyme/scoring.py:755-784`

---

## 形式化のコア設計

- HL-IRとCore-IRを分離
- Macro展開:
  - `thermocycle/incubate/centrifuge -> run_device`
  - `measure -> run_device + observe`
- 意図:
  - 生成自由度（HL）と検証厳密性（Core）を両立

---

## スコアリング設計

- default 6軸:
  - `S_structural, S_param, S_vocab, S_ident, S_ambiguity, S_exec_env`
- `total = 6軸平均`
- reproducibility拡張:
  - profile駆動カテゴリ評価
  - `flow_integrity`はviability gate
  - `repro.total = non-flowカテゴリの等平均`

---

## フロー設計（2層）

- unit内flow（スコア側）
  - source/order/kind mismatch/unused intermediate を検出
- paper内unit間flow（ベンチ側）
  - `material_flow`（厳密ref一致）
  - `logical_flow`（時系列＋語彙アンカー＋継続語）
  - `combined_integrity`

---

## unitカテゴリ設計

- ルールベース分類（regex）
- split品質監査:
  - `UNIT_TOO_SHORT_*`
  - `UNIT_NO_EXPERIMENT_CATEGORY`
  - `UNIT_CATEGORY_OVERMIXED`
- 解析出力:
  - 群別カテゴリ分布
  - カテゴリ別repro平均

---

## 実行完了性

- GPT: 34 papers / 315 units / failure 0 / repro欠損 0
- Qwen: 34 papers / 288 units / failure 0 / repro欠損 0
- 出典: `pilot_run_integrity.csv`

---

## 全体比較（34本）

- Default wins（GPT/Qwen/Tie）: `9 / 23 / 2`
- Repro wins（GPT/Qwen/Tie）: `24 / 5 / 5`
- Mean delta default（GPT-Qwen）: `-5.120`
- Mean delta repro（GPT-Qwen）: `+4.098`
- 出典: `pilot_compare_repro_summary.md`

---

## protocols vs siblings（群平均）

- GPT
  - total: `57.986 vs 69.785`（Δ `-11.799`）
  - repro: `26.986 vs 16.548`（Δ `+10.438`）
- Qwen
  - total: `59.316 vs 77.558`（Δ `-18.242`）
  - repro: `23.971 vs 11.691`（Δ `+12.280`）

---

## repro有意差（protocols vs siblings）

- GPT
  - Mann-Whitney p=`0.000404`
  - Welch p=`0.000005`
  - Cohen d=`1.732`
- Qwen
  - Mann-Whitney p=`0.000011`
  - Welch p=`0.000001`
  - Cohen d=`2.134`
- 出典: `repro_group_significance.md`

---

## モデル間相関（paper-level）

- all (n=34):
  - pearson_total=`0.735`, pearson_repro=`0.760`
- nat_protocols (n=14):
  - pearson_total=`-0.056`, pearson_repro=`-0.131`
- nat_siblings (n=20):
  - pearson_total=`0.761`, pearson_repro=`0.795`
- 出典: `pilot_model_correlation.csv`

---

## フロー結果ハイライト

- combined isolated rate（平均）
  - GPT: protocols `0.400`, siblings `0.658`
  - Qwen: protocols `0.179`, siblings `0.503`
- corr(repro, connectivity)
  - GPT: protocols `0.690`, siblings `0.758`
  - Qwen: protocols `0.658`, siblings `0.606`
- 出典: `pilot_flow_group_summary.csv`

---

## カテゴリ結果ハイライト

- protocols上位: `cell_culture`, `centrifugation`, `microscopy_imaging`
- siblings上位: `other`, `cell_culture`, `sequencing_library_prep`
- 同一カテゴリでも群間でrepro平均差が見える
- 出典:
  - `pilot_category_distribution_long.csv`
  - `pilot_category_scores_long.csv`

---

## 解釈

- 群平均傾向は両モデルで一致
  - siblingsのtotalは高い
  - protocolsのreproは高い
- 一方でprotocols群内の論文順位相関は低い
- つまり:
  - マクロ傾向の一致
  - ミクロ順位の不一致
  が同時成立

---

## ENZYMEの貢献可能性（現時点評価）

- 形式化品質と再現性品質を分離評価できる
- flow・categoryを統合して原因を掘れる
- 投稿前監査・ラボ標準化・LLM生成プロトコル評価に実用的
- 本パイロットは「本格展開に進む価値あり」を示す

---

## 次段の開発計画

1. `logical_flow`の高度化（co-reference / dependency）
2. カテゴリ分類のhybrid化（regex + embedding）
3. 重み最適化（外部再現成功データで学習）
4. Nat Protocols全件化で分野横断マップ作成
5. 回帰テストと再現解析パイプライン固定化

---

## 付録（主要成果物）

- 総合報告: `ENZYME_pilot_impact_report_ja.md`
- 相関図: `model_correlation_total_grid.png`, `model_correlation_repro_grid.png`
- 有意差図: `repro_group_jitter_box.png`
- 全表: `pilot_compare_repro_pairwise.csv`, `pilot_flow_paper_metrics.csv`, `pilot_category_scores_long.csv`
- protocols repro全件: `nat_protocols_repro_only.csv`
