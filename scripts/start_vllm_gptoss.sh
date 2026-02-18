#!/usr/bin/env bash
set -euo pipefail

MODEL_PATH="/users/hideto/Project/vLLM/Raw/gpt-oss-120b"
HOST="0.0.0.0"
PORT="8000"
HEALTH_HOST="127.0.0.1"
MAX_MODEL_LEN="131072"
SERVED_MODEL_NAME="gpt-oss-120b"
TP_SIZE="4"
RUN_DIR="run"
PID_FILE="${RUN_DIR}/vllm.pid"
LOG_FILE="${RUN_DIR}/vllm.log"

mkdir -p "${RUN_DIR}"

is_healthy() {
  curl -fsS "http://${HEALTH_HOST}:${PORT}/v1/models" >/dev/null 2>&1
}

if [[ -f "${PID_FILE}" ]]; then
  existing_pid="$(cat "${PID_FILE}" 2>/dev/null || true)"
  if [[ -n "${existing_pid}" ]] && kill -0 "${existing_pid}" >/dev/null 2>&1; then
    echo "vLLM already running (pid=${existing_pid})."
    exit 0
  fi
fi

if is_healthy; then
  echo "vLLM endpoint already reachable at http://${HEALTH_HOST}:${PORT}/v1/models"
  exit 0
fi

if [[ ! -d "${MODEL_PATH}" ]]; then
  echo "Model directory not found: ${MODEL_PATH}" >&2
  exit 1
fi

if command -v nvidia-smi >/dev/null 2>&1; then
  gpu_count="$(nvidia-smi --query-gpu=index --format=csv,noheader 2>/dev/null | wc -l | tr -d ' ')"
  if [[ -n "${gpu_count}" && "${gpu_count}" != "0" ]]; then
    echo "Detected ${gpu_count} GPU(s)."
    if (( gpu_count < TP_SIZE )); then
      echo "Need at least ${TP_SIZE} GPUs for --tensor-parallel-size ${TP_SIZE}." >&2
      exit 1
    fi
  else
    echo "GPU probe failed; continuing with --tensor-parallel-size ${TP_SIZE}." >&2
  fi
else
  echo "nvidia-smi not found; continuing with --tensor-parallel-size ${TP_SIZE}." >&2
fi

nohup vllm serve "${MODEL_PATH}" \
  --tensor-parallel-size "${TP_SIZE}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --max-model-len "${MAX_MODEL_LEN}" \
  --served-model-name "${SERVED_MODEL_NAME}" \
  >"${LOG_FILE}" 2>&1 &

pid="$!"
echo "${pid}" > "${PID_FILE}"

for _ in $(seq 1 60); do
  if is_healthy; then
    echo "vLLM started (pid=${pid}) and is healthy at http://${HEALTH_HOST}:${PORT}/v1/models"
    exit 0
  fi
  if ! kill -0 "${pid}" >/dev/null 2>&1; then
    echo "vLLM exited early. See ${LOG_FILE}" >&2
    exit 1
  fi
  sleep 2
done

echo "vLLM start timed out. Check ${LOG_FILE}" >&2
exit 1
