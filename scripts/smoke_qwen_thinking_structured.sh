#!/usr/bin/env bash
set -euo pipefail

MODEL_PATH="${MODEL_PATH:-/users/hideto/Project/vLLM/FP8/Qwen3-Next-80B-A3B-Thinking-FP8}"
SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-qwen3-next-80b-a3b-thinking}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
HEALTH_HOST="${HEALTH_HOST:-127.0.0.1}"
TP_SIZE="${TP_SIZE:-4}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-131072}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.85}"
MAX_NUM_SEQS="${MAX_NUM_SEQS:-16}"
MAX_NUM_BATCHED_TOKENS="${MAX_NUM_BATCHED_TOKENS:-1024}"
REASONING_PARSER="${REASONING_PARSER:-qwen3}"
GENERATION_CONFIG="${GENERATION_CONFIG:-vllm}"
STARTUP_TIMEOUT_SEC="${STARTUP_TIMEOUT_SEC:-600}"
RUN_DIR="${RUN_DIR:-run}"
LOG_FILE="${LOG_FILE:-${RUN_DIR}/vllm_qwen_thinking_structured.log}"

mkdir -p "${RUN_DIR}"

cleanup() {
  if [[ -n "${srv_pid:-}" ]]; then
    kill "${srv_pid}" >/dev/null 2>&1 || true
    wait "${srv_pid}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

if [[ ! -d "${MODEL_PATH}" ]]; then
  echo "Model directory not found: ${MODEL_PATH}" >&2
  exit 1
fi

vllm serve "${MODEL_PATH}" \
  --tensor-parallel-size "${TP_SIZE}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --max-model-len "${MAX_MODEL_LEN}" \
  --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
  --max-num-seqs "${MAX_NUM_SEQS}" \
  --max-num-batched-tokens "${MAX_NUM_BATCHED_TOKENS}" \
  --reasoning-parser "${REASONING_PARSER}" \
  --generation-config "${GENERATION_CONFIG}" \
  --served-model-name "${SERVED_MODEL_NAME}" \
  >"${LOG_FILE}" 2>&1 &
srv_pid="$!"

max_checks=$(( STARTUP_TIMEOUT_SEC / 2 ))
if (( max_checks < 1 )); then
  max_checks=1
fi
for _ in $(seq 1 "${max_checks}"); do
  if curl -fsS "http://${HEALTH_HOST}:${PORT}/v1/models" >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "${srv_pid}" >/dev/null 2>&1; then
    echo "vLLM exited early. See ${LOG_FILE}" >&2
    exit 2
  fi
  sleep 2
done
curl -fsS "http://${HEALTH_HOST}:${PORT}/v1/models" >/dev/null

rc_schema=0
rc_object=0

echo "[smoke] json_schema"
python scripts/smoke_structured_output.py \
  --base-url "http://${HEALTH_HOST}:${PORT}/v1" \
  --model "${SERVED_MODEL_NAME}" \
  --response-format json_schema \
  --max-tokens 1024 \
  --reasoning-max-tokens 512 \
  --timeout-sec 120 || rc_schema=$?

echo "[smoke] json_object"
python scripts/smoke_structured_output.py \
  --base-url "http://${HEALTH_HOST}:${PORT}/v1" \
  --model "${SERVED_MODEL_NAME}" \
  --response-format json_object \
  --max-tokens 1024 \
  --reasoning-max-tokens 512 \
  --timeout-sec 120 || rc_object=$?

echo "[done] logs: ${LOG_FILE}"
echo "[summary] json_schema_rc=${rc_schema} json_object_rc=${rc_object}"
if [[ "${rc_schema}" -ne 0 || "${rc_object}" -ne 0 ]]; then
  exit 1
fi
