# ENZYME パイロット実験報告（2026-02-15）

## 1. 目的
- `nat_protocols` と `nat_siblings` のプロトコル群を ENZYME 化し、`default` / `repro` スコア分布を比較する。
- 併せて、`unit` の実験手法カテゴリごとの低スコア傾向を探索する（探索的解析）。

## 2. 使用スクリプト
- ベンチマーク実行: `scripts/run_paper_benchmark.py`
- 基本集計: `scripts/analyze_scores.py`
- 深掘り集計（今回追加）: `scripts/deep_dive_analysis.py`
- LLM サーバ起動/停止: `scripts/start_vllm_gptoss.sh`, `scripts/stop_vllm_gptoss.sh`

## 3. 再現に必要なコマンド
前提: `/users/hideto/Project/ENZYME` で実行、`vLLM_env` を利用。

```bash
# 0) 環境
conda run -n vLLM_env python --version

# 1) vLLM 起動
bash scripts/start_vllm_gptoss.sh

# 2) no-rule-pack 実行（比較ベースライン）
conda run -n vLLM_env python scripts/run_paper_benchmark.py \
  --papers-root paper \
  --out results_ablation/no_rulepack \
  --group nat_protocols \
  --group nat_siblings \
  --llm-base-url http://127.0.0.1:8000/v1 \
  --llm-model gpt-oss-120b \
  --repro-profile profiles/reproducibility_profile.strict.v0_1.json \
  --no-enable-rule-pack \
  --skip-existing

# 3) with-rule-pack 実行（本命）
conda run -n vLLM_env python scripts/run_paper_benchmark.py \
  --papers-root paper \
  --out results_ablation/with_rulepack_full_llm \
  --group nat_protocols \
  --group nat_siblings \
  --llm-base-url http://127.0.0.1:8000/v1 \
  --llm-model gpt-oss-120b \
  --repro-profile profiles/reproducibility_profile.strict.v0_1.json \
  --enable-rule-pack \
  --skip-existing

# 4) 基本集計
conda run -n vLLM_env python scripts/analyze_scores.py --results results_ablation/no_rulepack
conda run -n vLLM_env python scripts/analyze_scores.py --results results_ablation/with_rulepack_full_llm

# 5) 深掘り集計（カテゴリ別、減点内訳）
python scripts/deep_dive_analysis.py \
  --run-dir results_ablation/with_rulepack_full_llm \
  --out-dir results_ablation/analysis

# 6) vLLM 停止
bash scripts/stop_vllm_gptoss.sh
```

## 4. 主要結果（今回の実行）
参照:
- `results_ablation/analysis/ablation_summary_with_full_llm.csv`
- `results_ablation/analysis/deep_dive_with_full_llm.json`
- `results_ablation/analysis/deep_dive_experiment_categories.csv`

### 4.1 グループ比較（unit平均）
- `no_rulepack`
  - `nat_protocols`: `default=56.795`, `repro=25.372`, `n=78`
  - `nat_siblings`: `default=66.049`, `repro=17.661`, `n=183`
- `with_rulepack_full_llm`
  - `nat_protocols`: `default=60.479`, `repro=24.575`, `n=73`
  - `nat_siblings`: `default=69.093`, `repro=17.473`, `n=182`

### 4.2 減点源（with-rule-pack, 全255 unit）
- `default` の主減点寄与（欠損シェア）
  - `nat_protocols`: `S_ident 40.2%`, `S_structural 29.0%`, `S_exec_env 28.7%`
  - `nat_siblings`: `S_ident 42.8%`, `S_exec_env 32.1%`, `S_structural 24.7%`
- `default` の主要エラーコード
  - 両群とも `SCHEMA_INVALID` が最多、次いで `MISSING_REQUIRED_PROGRAM_KEY`
- `repro` の主要欠落（高頻度）
  - `biosafety_level`, `contamination_control`, `protocol_id`, `sterility_required`
  - 加えて `sample_id`, `vendor`, `catalog_number`, `lot_number`, `source`

### 4.3 実験手法カテゴリ別の傾向（マルチラベル）
- `nat_protocols`
  - `cell_culture (n=49)`: `default=58.796`, `repro=25.367`
  - `centrifugation (n=16)`: `default=57.938`, `repro=26.875`
- `nat_siblings`
  - `molecular_cloning (n=17)`: `default=70.412`, `repro=15.882`（低repro率 0.588）
  - `dna_rna_extraction (n=17)`: `default=72.882`, `repro=16.412`（低repro率 0.588）
  - `sequencing_library_prep (n=16)`: `default=65.750`, `repro=18.250`（低repro率 0.500）
  - `cell_culture (n=41)`: `default=59.244`, `repro=24.927`

## 5. 解釈（パイロットとして）
- `default` は構造整合・必須キー充足に強く依存し、`repro` は再現実験に必要な同定/安全情報の記載有無に強く依存する。
- よって `default` が高くても `repro` は低くなり得る（軸が異なる）。
- 今回の結果は探索的比較として有用だが、優劣断定には追加検証が必要。

## 6. 次フェーズで見直す項目（合意済み論点）
- `unit` 分割品質:
  - 1実験手法1unit になっているか、複合手法が過剰に混在していないかを監査する。
- カテゴリ検出ルール:
  - ルールベース + 同義語辞書の精度検証（特に `PCR`, `cloning`, `transfection`）。
- unit 間接続（フロー整合）:
  - 「前unitの出力が後unitの入力に接続されるか」を明示評価する。
  - 終端産物（最終成果物）を誤って未使用扱いしない例外ルールを実装する。
- スコアリング:
  - 欠落フィールドの重みを再設計し、カテゴリ間の過度なバイアスを点検する。
  - 値妥当性（温度/時間/回転数など）の自動判定は現時点では実装しない（将来評価用に記録のみ保持）。
- 変換プロセス:
  - LLM プロンプトで語彙制限と canonical 名称の強制をより厳密化する。
  - `SCHEMA_INVALID` 主因の具体的失敗パターンを抽出し、前処理・修復ルールに反映する。

## 7. unit内/unit間フローグラフ（今回追加）
- 生成ファイル:
  - `results_ablation/with_rulepack_full_llm/<group>/<paper>/paper_flow_graph.json`
- 構造:
  - `unit_graphs`: unit内ステップグラフ（stepノード/stepエッジ + 入出力参照）
  - `inter_unit_graph`: unit間エッジ（`from_unit`, `to_unit`, `via_refs`）
  - `integrity`: 孤立unit検出結果（`pass`, `isolated_units`, `isolated_unit_rate`）
- ポリシー:
  - unit間接続は `sample` / `data` 参照の一致で判定（`material` など汎用ID連結は除外）
  - 完全孤立unitは `INTER_UNIT_ISOLATED_UNIT` として記録

### 7.1 現時点の観測（with-rule-pack）
- `nat_protocols`: 87 unit 中 68 unit が孤立（`78.16%`）
- `nat_siblings`: 195 unit 中 174 unit が孤立（`89.23%`）

この結果は、LLM の unit 分割や参照ID付与が unit 間連鎖を十分保持できていない可能性を示す。

## 8. 見直し項目 実装ステータス（5除外）
- 1) `unit` 分割品質監査: **実装済み**
  - `protocol_units/unit_quality_audit.json` を追加。
  - `paper_summary.json` に `unit_split_quality` を追加。
- 2) 実験カテゴリ検出ルール: **実装済み**
  - ルールを `scripts/config/experiment_category_rules.v1.json` に外出し。
  - `unit` ごとに `detected_categories`（マルチラベル+confidence）を保存。
- 3) unit 間接続評価: **実装済み**
  - `paper_flow_graph.json` を追加し、孤立unitを `INTER_UNIT_ISOLATED_UNIT` で記録。
- 4) スコアリング減点設計の明確化: **実装済み**
  - `required_fields` と `recommended_fields` を分離対応。
  - `deductions` に `missing_required_fields` / `missing_recommended_fields` を出力。
- 6) 変換前処理・語彙制約強化: **実装済み**
  - プロンプトを canonical語彙前提に更新。
  - 未知 `action_kind` / `device_kind` / `modality` は `annotate` に退避。

注: 5) 値妥当性の自動判定は合意どおり **未実装**（将来評価用に記録基盤のみ維持）。
