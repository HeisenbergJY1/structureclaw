#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_DIR="$ROOT_DIR/.runtime/pids"

show_service() {
  local name="$1"
  local pid_file="$PID_DIR/$name.pid"

  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" >/dev/null 2>&1; then
      echo "$name: running (pid $pid)"
      return 0
    fi
    echo "$name: stale pid file"
    return 0
  fi

  echo "$name: stopped"
}

show_service "backend"
show_service "frontend"
show_service "core"

echo
echo "Health checks:"
curl -sf http://localhost:8000/health >/dev/null && echo "backend: healthy" || echo "backend: unavailable"
curl -sf http://localhost:8001/health >/dev/null && echo "core: healthy" || echo "core: unavailable"
curl -sfI http://localhost:3000 >/dev/null && echo "frontend: healthy" || echo "frontend: unavailable"
