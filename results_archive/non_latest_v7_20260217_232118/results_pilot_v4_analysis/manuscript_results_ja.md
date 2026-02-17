# ENZYME パイロット結果（v4）

## 結果

### 1. 評価設定と完走状況
本パイロットでは `nat_protocols` 14報、`nat_siblings` 20報（計34報）を対象に、2モデル（`gpt-oss-120b`、`Qwen3-Next-80B-A3B-Instruct-FP8`）×2形式化経路（`hl-core`、`direct-core`）の4条件を比較した。再現性評価は strict profile（`profiles/reproducibility_profile.strict.v0_1.json`）で統一した。

4条件はいずれも 34/34 論文の処理を完了した。単位（unit）スコア生成数は `gpt_hlcore=322`、`gpt_directcore=326`、`qwen_hlcore=288`、`qwen_directcore=293` であり、失敗unitは `gpt_directcore` と `qwen_hlcore` で各1件のみであった。

### 2. 総合スコアと再現性スコアの群差
全条件で共通して、`total` は `nat_siblings` が高く、`repro` は `nat_protocols` が高い傾向を示した。

| Run | total mean (all) | repro mean (all) | total Δ(protocols-siblings) | repro Δ(protocols-siblings) |
|---|---:|---:|---:|---:|
| gpt_hlcore | 58.724 | 20.122 | -5.651 | +10.321 |
| gpt_directcore | 69.299 | 17.742 | -14.448 | +9.328 |
| qwen_hlcore | 61.041 | 16.155 | -7.349 | +9.232 |
| qwen_directcore | 68.396 | 17.847 | -11.922 | +7.511 |

すなわち、`nat_siblings` はカバレッジ（total）で優位、`nat_protocols` は再現性要件（repro）で優位という分離が、モデル・形式化経路を跨いで再現された。

### 3. repro 群差の統計的検定
`nat_protocols` と `nat_siblings` の repro 差は全条件で有意であり、効果量も中〜大であった。

- `gpt_hlcore`: Mann-Whitney p=0.000708、Welch p=5.91e-05、Cohen's d=1.542、Cliff's delta=0.693
- `gpt_directcore`: Mann-Whitney p=0.000186、Welch p=3.87e-06、Cohen's d=1.818、Cliff's delta=0.764
- `qwen_hlcore`: Mann-Whitney p=0.000274、Welch p=3.30e-05、Cohen's d=1.644、Cliff's delta=0.739
- `qwen_directcore`: Mann-Whitney p=0.014847、Welch p=0.001406、Cohen's d=1.133、Cliff's delta=0.500

この結果は、今回のreproスコア系が群間差を安定に検出できることを示す。

### 4. モデル間整合性（Qwen vs GPT）
モデル間相関は `direct-core` で高く、`hl-core` より整合的であった。

- `gpt_vs_qwen_hlcore`（all）: pearson_total=0.596、pearson_repro=0.749
- `gpt_vs_qwen_directcore`（all）: pearson_total=0.822、pearson_repro=0.815

一方、`nat_protocols` 内の論文順位一致は限定的で、`hl-core` ではほぼ無相関（repro: -0.019）だった。つまり、マクロ傾向（群平均差）は一致するが、ミクロ順位（個別論文の難易度順）はモデル依存である。

### 5. フロー指標（material/logical/combined）
`combined_isolated_rate` は全runで `nat_protocols < nat_siblings` であり、プロトコル論文の方が単位間接続が保たれやすい傾向が見られた。

- gpt_hlcore: protocols 0.321 vs siblings 0.613
- gpt_directcore: protocols 0.400 vs siblings 0.629
- qwen_hlcore: protocols 0.121 vs siblings 0.493
- qwen_directcore: protocols 0.186 vs siblings 0.524

また `direct-core` では GPT 系の material edge がほぼ 0（protocols/siblings ともに平均 0.0）で、Qwen 系では少量ながら material edge を保持した（0.14/0.50）。この差は lowering・抽出挙動の違いを反映している。

### 6. unitカテゴリ分布
カテゴリ分布は run 間で概ね安定し、`cell_culture`、`sequencing_library_prep`、`molecular_cloning`、`microscopy_imaging` が主要カテゴリとして再現された。

- `nat_protocols`: `cell_culture` が最大（例: Qwen direct-coreで n=91）
- `nat_siblings`: `other` が最大（例: GPT direct-coreで n=106）

この結果は、ENZYME の unit 分割とカテゴリ付与が、コーパス特性の差（protocol特化 vs 広い methods 記述）を定量化できることを示す。

### 7. 中間的結論（パイロット段階）
本パイロットは、ENZYME が以下を同時に提供できることを示した。

1. 形式化（HL/Core）を介した論文手順の比較可能化
2. total と repro の分離評価による「網羅性」と「再現性」の切り分け
3. flow 指標による単位間接続性の可視化
4. カテゴリ分布に基づく実験タイプ別の偏り解析

したがって、34報規模の段階でも、ENZYME は生命科学プロトコル記述を「定量比較可能なオブジェクト」に変換する基盤として有効であることが示唆される。

## 参照アーティファクト
- `results_pilot_v4_analysis/pilot_v4_overview.md`
- `results_pilot_v4_analysis/pilot_v4_run_summary.csv`
- `results_pilot_v4_analysis/pilot_v4_group_summary.csv`
- `results_pilot_v4_analysis/compare_gpt_vs_qwen_hlcore/`
- `results_pilot_v4_analysis/compare_gpt_vs_qwen_directcore/`
- `results_pilot_v4_analysis/compare_hl_vs_direct_gpt/`
- `results_pilot_v4_analysis/compare_hl_vs_direct_qwen/`
