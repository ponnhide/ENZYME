# ENZYME Benchmark Pre-Run Checklist

対象: `nat_protocols` vs `nat_siblings` 比較実験（`gpt-oss` / `qwen`）

## 1. Run設計の固定
- モデルごとに出力先を分離する
  - 例: `results_compare_gptoss`, `results_compare_qwen`
- 比較条件を事前固定する
  - `--max-protocols-per-paper`
  - `--skip-existing` の有無
  - `--enable-rule-pack` / `--no-enable-rule-pack`

## 2. 単一起動の徹底
- 実行前に残プロセス確認:
  - `pgrep -af "vllm serve|run_paper_benchmark.py"`
- サーバは同時に1つだけ起動する

## 3. vLLM実行環境の固定
- `vLLM_env_update`（vLLM 0.15.1）を使う
- QwenはFP8モデルパスを固定する
  - `MODEL_PATH=/users/hideto/Project/vLLM/FP8/Qwen3-Next-80B-A3B-Thinking-FP8`

## 4. 起動コマンド
- gpt-oss:
  - `bash scripts/start_vllm_gptoss.sh`
- qwen:
  - `MODEL_PATH=/users/hideto/Project/vLLM/FP8/Qwen3-Next-80B-A3B-Thinking-FP8 bash scripts/start_vllm_qwen3_next_80b.sh`

## 5. API最小疎通（必須）
- モデル一覧:
  - `curl -fsS http://127.0.0.1:8000/v1/models`
- chat疎通:
  - `curl -fsS http://127.0.0.1:8000/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"<MODEL_NAME>","messages":[{"role":"user","content":"return JSON only: {\"ok\":true}"}],"temperature":0,"max_tokens":64}'`
- 疎通失敗時は本実験に進まない

## 6. 当日スモーク（モデルごと）
- 1 paper / 1 unit で実行:
  - `python scripts/run_paper_benchmark.py --group nat_protocols --papers-root papers --out <SMOKE_OUT_DIR> --max-papers-per-group 1 --max-protocols-per-paper 1 --llm-model <MODEL_NAME>`
- `paper_summary.json` の `unit_scores[].status` が `ok` か確認

## 7. 本実行（モデルごと同一条件）
- `nat_protocols`:
  - `python scripts/run_paper_benchmark.py --group nat_protocols --papers-root papers --out <OUT_DIR> --llm-model <MODEL_NAME>`
- `nat_siblings`:
  - `python scripts/run_paper_benchmark.py --group nat_siblings --papers-root papers --out <OUT_DIR> --llm-model <MODEL_NAME>`

## 8. 失敗データの扱いを事前定義
- `status=failed` を除外するか、失敗率として別指標化するか決める
- segmentation fallback発生を別フラグとして扱う

## 9. 回収すべき成果物
- `results/<group>/<paper>/paper_summary.json`
- `results/<group>/<paper>/paper_flow_graph.json`
- `results/<group>/<paper>/logs/pipeline.log`
- `results/<group>/<paper>/logs/unit_*.log`
- `results/<group>/<paper>/enzyme/unit_*.scores.json`

## 10. 集計前チェック
- 全paperで `paper_summary.json` 存在確認
- `unit_*.scores.json` 欠損件数を確認
- 欠損/失敗率をモデル間で比較

## 11. 集計・可視化
- `python scripts/analyze_scores.py --results <OUT_DIR>`
- 各モデルの `results/analysis/scores_long.csv` / `scores_per_paper.csv` / `plots/*` を比較

## 12. 終了処理
- サーバ停止:
  - `bash scripts/stop_vllm_gptoss.sh`
- 残プロセス確認:
  - `pgrep -af "vllm serve|run_paper_benchmark.py"`
