# ENZYME vLLM/Qwen Handoff Memo (2026-02-15)

## 1. 現在の状況（事実ベース）
- 直近で `vLLM` を `0.15.1` に更新した検証環境を作成済み。
  - env: `vLLM_env_update`
  - version確認: `0.15.1`
- 既存環境 `vLLM_env` は `vLLM 0.14.1` のまま。
- ENZYME側のコードは以下を実装済み。
  - `scripts/start_vllm_qwen3_next_80b.sh` に `--reasoning-parser qwen3` を追加。
  - `scripts/llm_client.py` で `message.content` が空のときも `reasoning` / `reasoning_content` / list形式からテキスト回収するフォールバックを追加。
- ただし本日後半の試行では、Qwen起動時に `run/vllm.log` 上で最終的に `NCCL error: unhandled cuda error` で EngineCore 初期化失敗となるケースが発生。
- ユーザー環境側では `nvidia-smi` は見えているとのこと（こちらの実行コンテキストとの差異あり）。
- 最終状態として、不要プロセスは停止済み（`vllm serve` / `conda run ...` を kill 済み）。

## 2. この時点での変更ファイル
- `scripts/start_vllm_qwen3_next_80b.sh`
  - 追加: `REASONING_PARSER="${REASONING_PARSER:-qwen3}"`
  - `vllm serve` 引数へ `--reasoning-parser "${REASONING_PARSER}"`
- `scripts/llm_client.py`
  - 追加: `_stringify_parts`, `_extract_choice_text`
  - 変更: `_chat_once` のテキスト抽出をフォールバック対応化
- 参考: 上記2ファイルはこのリポジトリ上では `git status` で untracked 表示だった（ユーザー運用のgit管理状態に依存）。

## 3. ここまでの結論（暫定）
- `--reasoning-parser qwen3` 自体は「起動引数として反映」されることをログで確認済み。
- 現在のボトルネックは parser 指定の有無より、実行時の分散初期化（NCCL）側にある可能性が高い。
- ただしセッション終盤は VRAM圧迫/並行起動の影響も混ざっているため、同一条件でのクリーン再試験が必要。

## 4. 問題が解決した場合に次にやること（次Codex向け実行順）
1. **単一のクリーン起動で再確認**
   - 先に全停止確認: `pgrep -af "vllm serve|run_paper_benchmark.py|conda run -n vLLM_env|conda run -n vLLM_env_update"`
   - 0件を確認してから開始。
2. **Qwen FP8を優先して起動確認**
   - `MODEL_PATH=/users/hideto/Project/vLLM/FP8/Qwen3-Next-80B-A3B-Thinking-FP8`
   - `max_model_len=131072` 維持。
   - `--reasoning-parser qwen3` がログに出ることを確認。
3. **API最小疎通（ベンチ前）**
   - `/v1/models` 200
   - `/v1/chat/completions` 1件（JSON強制の短いプロンプト）
   - 返却で `content` 空でも `llm_client` フォールバックが動くかを確認。
4. **最小ベンチ実行（1 paper, 1 unit）**
   - `scripts/run_paper_benchmark.py --max-papers-per-group 1 --max-protocols-per-paper 1 ...`
   - 失敗時は `paper_summary.json` / `logs/unit_001.log` を回収。
5. **gpt-oss と同じ手順で比較**
   - gpt-ossでも同じ最小条件を回し、失敗形式（content欠落 or NCCL等）を比較。
6. **結果をメモ化**
   - 成功/失敗の再現条件を1ファイルに固定化（環境変数、モデルパス、ログ抜粋、再現コマンド）。

## 5. 次Codexが注意すべき点
- 複数の `conda run` / `vllm serve` を重ねない（VRAM圧迫・状態混線の原因）。
- ユーザーが既に別端末でモデルを起動している可能性があるので、実行前に必ず確認。
- 不要な長時間 `--help` や複数並列試験を避ける。
- まず「1プロセスで起動→1リクエストで応答→最小ベンチ」の順で進める。

