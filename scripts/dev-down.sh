#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_DIR="$ROOT_DIR/.runtime/pids"

stop_service() {
  local name="$1"
  local pid_file="$PID_DIR/$name.pid"

  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" >/dev/null 2>&1; then
      echo "Stopping $name (pid $pid)..."
      kill "$pid" >/dev/null 2>&1 || true
    fi
    rm -f "$pid_file"
  else
    echo "$name is not tracked."
  fi
}

stop_service "frontend"
stop_service "backend"
stop_service "core"

echo "Stopping local infrastructure..."
docker compose -f "$ROOT_DIR/docker-compose.yml" stop postgres redis >/dev/null 2>&1 || true

echo "Local stack stopped."
