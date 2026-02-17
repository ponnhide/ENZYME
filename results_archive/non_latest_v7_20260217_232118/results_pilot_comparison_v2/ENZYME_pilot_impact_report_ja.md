# ENZYME パイロット評価報告書（Nat Protocols vs Nat Siblings, GPT-OSS vs Qwen）

## 要旨
本報告は、ENZYMEの現行実装（v0.4 MVP）について、(i) 形式化パイプラインの実装妥当性、(ii) スコアリング体系の挙動、(iii) フロー・カテゴリ情報を含めた生命科学プロトコル評価としての有用性、を実データで検証した結果をまとめる。対象は `nat_protocols=14本`、`nat_siblings=20本` の計34論文で、モデルは `gpt-oss-120b-medium` と `Qwen3-Next-80B-A3B-Instruct-FP8` を用いた。概念的基盤としては、QUEEN論文（Nature Communications, 2022, s41467-022-30588-x）が提示した「プロセスを再利用可能な最小操作へ還元し、履歴を保持して再現可能性と継承性を担保する」という思想を参照している。

主要結果は次の通りである。`default(total)` はQwenが高い一方、`reproducibility` はGPT-OSSが高く、群平均では両モデルとも一貫して `siblings > protocols (total)`、`protocols > siblings (repro)` を示した。加えて、`repro` の群間差は両モデルで有意（Mann-Whitney, Welchともに有意）であり、効果量も大きい。モデル間相関は全体・siblingsで高いが、protocols内ではほぼ0であり、「群平均傾向は一致するが、群内ランキングは一致しない」という構造が確認された。

これらは、ENZYMEが単純な品質スコアではなく、**再現性（トレーサビリティ・QC・フロー整合など）を別軸で分離評価できる**ことを示す。すなわち、本パイロットはENZYMEの生命科学実験への貢献可能性を「実装上も、解析上も、十分に議論可能な水準」で示している。ただし、汎化主張には全Nat Protocols級の大規模化と、重み最適化・外部妥当化が次段で必要である。

---

## 1. ENZYME実装の中核と設計意図

### 1.0 思想的基盤（QUEEN論文との対応）
参考論文: https://www.nature.com/articles/s41467-022-30588-x  
同論文は、DNA構築プロセスを最小操作関数へ分解し、操作履歴を再生成可能に保持する設計（quining）を提示している（Nature本文の`Results > Queen`で、基本操作`cut/flip/join/modify ends`を中心に記載）。ENZYMEがCore関数を絞る方針は、この「拡張容易性は周辺へ、信頼核は最小へ」という思想に整合する。

ENZYME側の対応関係は次の通り。

- 最小Core演算に固定: `allocate/transfer/manipulate/run_device/observe/annotate/dispose`（`README.md`, `ENZYME_Spec_v0_4.md:59-61`）

- 高級手順はLoweringでCore化: `lower_to_core`（`src/enzyme/lowering.py:29-136`）

- 再現性/継承性評価のための履歴・メタ保持: unitメタ、flow graph、deductions等（`scripts/run_paper_benchmark.py:1373-1431`, `src/enzyme/scoring.py:675-752`）

### 1.1 E2Eパイプライン（import → compile → validate → score → report）
ENZYME CLIは、`import/compile/validate/score/report` を直列に提供する（`src/enzyme/cli.py:33-105`）。

- `import`: protocols.io JSONをHL-IRへ（`src/enzyme/cli.py:33-45`, `src/enzyme/importers/protocolsio.py:6-99`）
- `compile`: HL-IRをCore-IRへLowering（`src/enzyme/cli.py:47-56`, `src/enzyme/lowering.py:29-136`）
- `validate`: schema + registry + graph + refs + unit/range（`src/enzyme/validator.py:372-395`）
- `score`: 6軸スコア + （任意）reproducibility拡張（`src/enzyme/scoring.py:755-784`）
- `report`: Markdown整形（`src/enzyme/report.py:6-45`）

設計意図は、仕様書が明示する「小さな信頼核（Core）」と「二層評価（二値 + 連続）」に一致する（`ENZYME_Spec_v0_4.md:1-83`, `ENZYME_Spec_v0_4.md:413-464`）。

### 1.2 形式化（HL→Core）のコアメソッドと意図
Loweringの本体は `lower_to_core`（`src/enzyme/lowering.py:29-136`）。

- マクロ展開:
  - `thermocycle/incubate/centrifuge` → `run_device`（`src/enzyme/lowering.py:7-11`, `39-56`）
  - `measure` → `run_device + observe` に2分割（`57-97`）
- `annotations.lowered_from` と provenance継承（`14-27`）
- edge再配線とstep_order再構成（`102-135`）

この設計により、LLM/人手が書きやすいHL表現を、Kernelが検証しやすいCore正規形に落とす。実験記述の自由度と検証の厳密性を分離することが意図である。

### 1.3 Kernel Validatorの実装と意図
`validate_core` は以下を統合検査する（`src/enzyme/validator.py:372-395`）。

- JSON Schema検証（`39-56`, `376-377`）
- Core op制約（`276-289`）
- Registry整合（action/device/modality/features）（`141-201`）
- 参照整合（refs/edges）（`204-248`）
- グラフ基本整合（start_step_id, edges）（`251-273`）
- unit解釈（pint）とobserveのrange制約（`291-369`）

未知語彙のwarn/error切替が `detail_level` で変わる点（`145`）は、仕様が想定する粒度制御と整合的である。

### 1.4 スコアリング（default 6軸）の詳細
`score_core` は6軸を算出し単純平均で `total` を作る（`src/enzyme/scoring.py:766-775`）。

- `S_structural`: issue severity依存（errorがあると0, warn/infoで減点）（`15-22`）
- `S_param`: transfer/run_device/observeの必要パラメータ充足率（`24-43`）
- `S_vocab`: registry/cutom registry既知率（`45-72`）
- `S_ident`: vendor/catalog/model/identifier充足（`91-104`）
- `S_ambiguity`: symbol/range密度で減点（`106-129`）
- `S_exec_env`: device_ref有無 + container容量情報（`131-143`）

**意図**: 「構造的に正しいか」だけでなく、「再利用・再実験に必要な情報密度」を多面体で把握する。

### 1.5 reproducibilityスコアリングの詳細と意図
reproducibilityはプロファイル駆動（`profiles/reproducibility_profile.strict.v0_1.json`）で実装され、カテゴリは以下を含む:
`reagent_ident, sample_ident, device_ident, container_ident, param_completeness, qc_completeness, traceability, safety_disposal, flow_integrity`。

実装上の重要点:

- カテゴリ別詳細（missing_fields, deductions, issue_counts）を返す（`src/enzyme/scoring.py:629-752`）
- `flow_integrity` は viability gateとして扱う（`733-750`）
- `repro.total` は **非flowカテゴリの等重み平均**（`732`, `741`）
  - `total_mode = equal_average_non_flow`

これは「初期MVPでは重みバイアスを抑え、どの欠損が効くかを先に観測する」という運用方針に合致する。

### 1.6 フロー実装の二層構造
ENZYMEには2種類のフロー評価が実装されている。

1. **unit内フロー（scoring側）**
   - `check_flow_integrity`（`src/enzyme/scoring.py:548-626`）
   - 検出: `FLOW_INPUT_WITHOUT_SOURCE`, `FLOW_ORDER_VIOLATION`, `FLOW_KIND_MISMATCH`, `FLOW_UNUSED_INTERMEDIATE`
   - ペナルティ重み付きスコア（`607-617`）

2. **paper内unit間フロー（benchmark側）**
   - `build_paper_flow_graph`（`scripts/run_paper_benchmark.py:886-1082`）
   - `material_flow`: sample/data refの厳密一致（`949-966`）
   - `logical_flow`: 時系列窓 + shared target terms + continuity cue + op pattern（`967-1038`）
   - `combined_integrity`: material/logical併合（`1052-1061`）

**意図**: 「実体受け渡しの厳密連結」と「文章上の手順依存」を分離し、両方を観測可能にする。

### 1.7 unitカテゴリ付与（分類）
分類は2段で実装される。

- 生成時カテゴリ付与 + split品質監査（`scripts/run_paper_benchmark.py:251-325`）
  - regexカテゴリルール: `scripts/config/experiment_category_rules.v1.json`
  - flags: `UNIT_TOO_SHORT_*`, `UNIT_NO_EXPERIMENT_CATEGORY`, `UNIT_CATEGORY_OVERMIXED`
- 解析時カテゴリ集計（`scripts/deep_dive_analysis.py:26-83`, `169-225`）
  - unitテキストから `labels` を再判定し、群別カテゴリ分布・カテゴリ別repro平均を出力

**意図**: 単一スコアでは見えない「どの実験タイプで何が欠けるか」を把握する。

---

## 2. 実験設定とデータ

- コーパス: `nat_protocols=14`, `nat_siblings=20`, 計34論文
- モデル:
  - `gpt-oss-120b-medium-v2`
  - `qwen3-next-80b-a3b-instruct-fp8-v2`
- 実行完了性:
  - GPT: 34 papers, 315 units, paper failure=0, missing total=0, missing repro=0
  - Qwen: 34 papers, 288 units, paper failure=0, missing total=0, missing repro=0
  - 出典: `results_pilot_comparison_v2/pilot_run_integrity.csv`

出力群:
- スコア比較: `pilot_compare_repro_summary.md`, `pilot_compare_repro_pairwise.csv`
- 有意差: `repro_group_significance.md`, `repro_group_significance.csv`
- 相関: `pilot_model_correlation.csv`, `model_correlation_*_grid.png`
- フロー: `pilot_flow_group_summary.csv`, `pilot_flow_paper_metrics.csv`
- カテゴリ: `pilot_category_distribution_long.csv`, `pilot_category_scores_long.csv`
- protocols全repro一覧: `nat_protocols_repro_only.csv`

---

## 3. 結果（全出力に基づく）

### 3.1 全体比較（default/repro）
出典: `results_pilot_comparison_v2/pilot_compare_repro_summary.md`

- Compared papers: 34
- Default wins（GPT/Qwen/Tie）: 9 / 23 / 2
- Repro wins（GPT/Qwen/Tie）: 24 / 5 / 5
- Mean delta default（GPT-Qwen）: -5.120
- Mean delta repro（GPT-Qwen）: +4.098

解釈:
- defaultではQwenが高く出やすい
- reproではGPTが高く出やすい
- ENZYMEが「総合整形品質」と「再現性情報密度」を分離できていることを示唆

### 3.2 群平均（protocols vs siblings）
出典: `results_pilot_comparison_v2/pilot_compare_repro_summary.md`

- GPT
  - total: protocols 57.986 vs siblings 69.785（Δ=-11.799）
  - repro: protocols 26.986 vs siblings 16.548（Δ=+10.438）
- Qwen
  - total: protocols 59.316 vs siblings 77.558（Δ=-18.242）
  - repro: protocols 23.971 vs siblings 11.691（Δ=+12.280）

**両モデルで方向一致**:
- `siblings > protocols`（total）
- `protocols > siblings`（repro）

### 3.3 repro群間差の有意性
出典: `results_pilot_comparison_v2/repro_group_significance.md`

- GPT
  - Mann-Whitney p=0.000404
  - Welch t p=0.000005
  - Cohen d=1.732, Cliff delta=0.725
- Qwen
  - Mann-Whitney p=0.000011
  - Welch t p=0.000001
  - Cohen d=2.134, Cliff delta=0.882

結論:
- reproにおける protocols/siblings 差は統計的に強く有意
- 効果量も大きく、実質差としても解釈可能

### 3.4 モデル間相関（paper-level）
出典: `results_pilot_comparison_v2/pilot_model_correlation.csv`

- all (n=34)
  - pearson_total=0.735, pearson_repro=0.760
- nat_protocols (n=14)
  - pearson_total=-0.056, pearson_repro=-0.131
- nat_siblings (n=20)
  - pearson_total=0.761, pearson_repro=0.795

解釈:
- 全体・siblingsではモデル整合が高い
- protocols内ではランキング整合が弱い
- これは「群平均傾向一致」と矛盾しない（平均差と群内順位相関は別指標）

### 3.5 nat_protocolsのrepro全件（引用）
出典: `results_pilot_comparison_v2/nat_protocols_repro_only.csv`

主要14本のうち、GPT優位/同等/Qwen優位が混在。
特に差が大きい論文として:
- `s41596-025-01197-x`: GPT 35.0 vs Qwen 15.8（Δ=+19.2）
- `s41596-020-00474-1`: GPT 23.7 vs Qwen 8.5（Δ=+15.2）
- `s41596-025-01236-7`: GPT 28.4 vs Qwen 31.5（Δ=-3.1）

この混在が、protocols群内相関の低さにつながっている。

### 3.6 フロー解析結果
出典: `results_pilot_comparison_v2/pilot_flow_group_summary.csv`

- GPT / protocols
  - material_nonzero_rate=0.50
  - logical_nonzero_rate=0.857
  - combined_pass_rate=0.143
  - combined_isolated_rate_mean=0.400
  - corr(repro, connectivity)=0.690
- GPT / siblings
  - combined_pass_rate=0.000
  - combined_isolated_rate_mean=0.658
  - corr(repro, connectivity)=0.758
- Qwen / protocols
  - material_nonzero_rate=0.643
  - logical_nonzero_rate=1.000
  - combined_pass_rate=0.571
  - combined_isolated_rate_mean=0.179
  - corr(repro, connectivity)=0.658
- Qwen / siblings
  - combined_pass_rate=0.100
  - combined_isolated_rate_mean=0.503
  - corr(repro, connectivity)=0.606

示唆:
- 接続性（1-isolated_rate）とreproが正相関
- フロー情報は再現性評価の意味ある補助軸になっている

### 3.7 カテゴリ解析結果
出典: `results_pilot_comparison_v2/pilot_category_distribution_long.csv`, `pilot_category_scores_long.csv`

代表例（unit数上位）:
- protocols
  - `cell_culture`, `centrifugation`, `microscopy_imaging` が主要カテゴリ
- siblings
  - `other` の比率が高く、次いで `cell_culture`, `sequencing_library_prep`, `molecular_cloning`

カテゴリ別repro平均では、同一カテゴリでも群差が観察される（例: `cell_culture`）。
これは「分野差」より「記載様式差（ID/traceability/QC/flow記述）」の寄与を示唆する。

---

## 4. これらの結果が示すENZYMEの貢献可能性

### 4.1 どの程度示せたか（本パイロット時点）
本パイロットは、ENZYMEの貢献可能性を次の3点で実証した。

1. **再現性の独立軸化**
   - default高スコアでもreproが低いケースを明確に分離できる
   - 生命科学における「きれいな方法記述」と「再実験可能性」のギャップ可視化に有効

2. **フロー統合評価**
   - 厳密material flow + 論理flowの2層でunit連結性を評価
   - connectivityとreproの正相関が、フロー評価の妥当性を支持

3. **実験タイプ別の欠損診断**
   - カテゴリ単位で missing_fields / deductions の傾向を集計
   - 改善対象（どのカテゴリで何が抜けるか）を具体化可能

総合すると、**「実験再現性監査ライブラリ」として中〜高い有用性**を示す段階に到達したと評価できる。

### 4.2 生物学コミュニティに対する実務的価値
ENZYMEの価値は、単なるベンチマーク順位ではなく次の運用にある。

- Methodsセクションの品質監査（投稿前/再現性チェック）
- Lab内プロトコルの標準化と欠損検出
- 論文群比較での「再現性上の暗黙知不足」の定量化
- 自動生成プロトコル（LLM）への安全な品質ゲート

特に `repro.total` と `viability_gate` の分離は、
- 再現性改善（情報補完）
- 実行可能性改善（フロー破綻修正）
を別々に最適化できる点で実装的に重要である。

---

## 5. 限界

1. パイロット規模は34論文で、統計頑健性は中規模
2. Qwenはunit数が少なく（288 vs 315）、分割差分の影響が残る
3. カテゴリ分類はregex中心で、語彙表現揺れに弱い
4. logical_flowはヒューリスティック（`heuristic_v0_1`）であり、過検出/見逃しの可能性がある
5. 重み未使用（equal-average）はMVPとして妥当だが、最終的な最適設計は未確定

---

## 6. 今後の発展可能性（Nat Protocols全件化を含む）

### 6.1 全Nat Protocols規模で可能になる議論
全件形式化が実現すると、以下が可能になる。

- 分野別（細胞/分子/イメージング等）の再現性地図
- 年次変化（Methods記述の質トレンド）
- ジャーナル横断比較（Nat Protocols vs 他誌Methods）
- カテゴリ別ボトルネック（例: sample_ident不足が高頻度な領域）
- フロー連結性と再現成功率（外部実験再現データが取れた場合）の因果仮説検証

### 6.2 実装ロードマップ（優先順）
1. `logical_flow`の改善
   - dependency parser / coreference / entity linkingの導入
2. カテゴリ分類の強化
   - regex + embedding/NERのハイブリッド
3. 重み学習
   - 等重みをベースラインに、外部正解（再現成功/失敗）で学習
4. 反事実診断
   - 「どのmissing fieldを補完するとreproがどれだけ改善するか」の推定
5. 品質保証
   - 解析スクリプト群の回帰テスト追加

### 6.3 学術的インパクトの見込み
現段階でも、ENZYMEは以下の論点を学術的に提示できる。

- 実験方法記述の品質を、形式妥当性と再現性情報の二層で分解可能
- 実験分野横断で比較可能な共通IRを提供
- LLM生成プロトコルの評価基盤として、単一スコア以上の説明責任を持つ

パイロット結果は、**「本格展開に進む価値がある」ことを十分示している**。

---

## 7. 結論
本パイロットは、ENZYMEが
- 実装面ではE2Eで安定稼働し、
- 分析面ではscore / repro / flow / categoryを統合して、
- 生命科学Methodsの再現性議論に実用的な定量軸を与える
ことを示した。

次段は、全件規模での統計的頑健化と、logical_flow・カテゴリ分類・重み推定の高度化である。これが実現すれば、ENZYMEは「方法記述の客観監査インフラ」として、生命科学コミュニティへの明確なインパクトを持つ可能性が高い。

---

## 付録A. 本報告で引用した主要成果物

### A1. 結果サマリ
- `results_pilot_comparison_v2/pilot_compare_repro_summary.md`
- `results_pilot_comparison_v2/pilot_compare_repro_pairwise.csv`
- `results_pilot_comparison_v2/pilot_run_integrity.csv`

### A2. 統計
- `results_pilot_comparison_v2/repro_group_significance.md`
- `results_pilot_comparison_v2/repro_group_significance.csv`
- `results_pilot_comparison_v2/pilot_model_correlation.csv`

### A3. 可視化
- `results_pilot_comparison_v2/repro_group_jitter_box.png`
- `results_pilot_comparison_v2/model_correlation_total_grid.png`
- `results_pilot_comparison_v2/model_correlation_repro_grid.png`

### A4. フロー・カテゴリ
- `results_pilot_comparison_v2/pilot_flow_paper_metrics.csv`
- `results_pilot_comparison_v2/pilot_flow_group_summary.csv`
- `results_pilot_comparison_v2/pilot_category_distribution_long.csv`
- `results_pilot_comparison_v2/pilot_category_scores_long.csv`
- `results_pilot_comparison_v2/nat_protocols_repro_only.csv`

### A5. 実装根拠（コード）
- `src/enzyme/cli.py:33`
- `src/enzyme/lowering.py:29`
- `src/enzyme/validator.py:372`
- `src/enzyme/scoring.py:15`
- `src/enzyme/scoring.py:548`
- `src/enzyme/scoring.py:629`
- `scripts/run_paper_benchmark.py:251`
- `scripts/run_paper_benchmark.py:886`
- `scripts/run_paper_benchmark.py:1398`
- `scripts/deep_dive_analysis.py:39`

### A6. 思想的参照
- QUEEN論文（Nature Communications, 2022）: `https://www.nature.com/articles/s41467-022-30588-x`
