#!/usr/bin/env bash
set -euo pipefail

PID_FILE="run/vllm.pid"

if [[ ! -f "${PID_FILE}" ]]; then
  echo "No PID file at ${PID_FILE}; nothing to stop."
  exit 0
fi

pid="$(cat "${PID_FILE}" 2>/dev/null || true)"
if [[ -z "${pid}" ]]; then
  rm -f "${PID_FILE}"
  echo "Empty PID file removed."
  exit 0
fi

if kill -0 "${pid}" >/dev/null 2>&1; then
  kill "${pid}" >/dev/null 2>&1 || true
  for _ in $(seq 1 20); do
    if ! kill -0 "${pid}" >/dev/null 2>&1; then
      rm -f "${PID_FILE}"
      echo "Stopped vLLM (pid=${pid})."
      exit 0
    fi
    sleep 1
  done

  kill -9 "${pid}" >/dev/null 2>&1 || true
  rm -f "${PID_FILE}"
  echo "Force-stopped vLLM (pid=${pid})."
  exit 0
fi

rm -f "${PID_FILE}"
echo "Process ${pid} not running; stale PID file removed."
