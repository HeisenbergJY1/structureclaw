#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/.runtime"
LOG_DIR="$RUNTIME_DIR/logs"
PID_DIR="$RUNTIME_DIR/pids"
CORE_PROFILE="lite"
SKIP_INFRA=0
SKIP_DB_INIT=0

print_usage() {
  cat <<'EOF'
Usage: ./scripts/dev-up.sh [lite|full] [--skip-infra] [--skip-db-init]

Options:
  lite            Start core with lightweight Python dependencies (default)
  full            Start core with full Python dependencies
  --skip-infra    Do not start postgres/redis via docker compose
  --skip-db-init  Skip Prisma migrate+seed
EOF
}

for arg in "$@"; do
  case "$arg" in
    lite|full)
      CORE_PROFILE="$arg"
      ;;
    --skip-infra)
      SKIP_INFRA=1
      ;;
    --skip-db-init)
      SKIP_DB_INIT=1
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg"
      print_usage
      exit 1
      ;;
  esac
done

mkdir -p "$LOG_DIR" "$PID_DIR"

ensure_file() {
  local target="$1"
  local example="$2"
  if [[ ! -f "$target" && -f "$example" ]]; then
    cp "$example" "$target"
    echo "Created $target from example."
  fi
}

is_pid_running() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" >/dev/null 2>&1; then
      return 0
    fi
    rm -f "$pid_file"
  fi
  return 1
}

start_service() {
  local name="$1"
  local command="$2"
  local pid_file="$PID_DIR/$name.pid"
  local log_file="$LOG_DIR/$name.log"

  if is_pid_running "$pid_file"; then
    echo "$name is already running (pid $(cat "$pid_file"))."
    return 0
  fi

  echo "Starting $name..."
  bash -lc "cd \"$ROOT_DIR\" && $command" >>"$log_file" 2>&1 &
  echo $! >"$pid_file"
}

require_command() {
  local cmd="$1"
  local hint="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd"
    echo "$hint"
    exit 1
  fi
}

docker_ready() {
  docker info >/dev/null 2>&1
}

wait_for_postgres() {
  echo "Waiting for PostgreSQL..."
  for _ in {1..30}; do
    if docker compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
      echo "PostgreSQL is ready."
      return 0
    fi
    sleep 2
  done

  echo "PostgreSQL did not become ready in time."
  return 1
}

ensure_file "$ROOT_DIR/.env" "$ROOT_DIR/.env.example"
ensure_file "$ROOT_DIR/backend/.env" "$ROOT_DIR/backend/.env.example"
ensure_file "$ROOT_DIR/frontend/.env.local" "$ROOT_DIR/frontend/.env.example"

require_command "node" "Install Node.js 18+ and retry."
require_command "npm" "Install npm and retry."
require_command "python" "Install Python 3.10+ and retry."

if [[ ! -d "$ROOT_DIR/backend/node_modules" || ! -d "$ROOT_DIR/frontend/node_modules" ]]; then
  echo "Installing frontend/backend dependencies..."
  npm ci --prefix "$ROOT_DIR/backend"
  npm ci --prefix "$ROOT_DIR/frontend"
fi

if [[ ! -x "$ROOT_DIR/core/.venv/bin/python" ]]; then
  echo "Creating Python virtual environment for core ($CORE_PROFILE)..."
  if [[ "$CORE_PROFILE" == "full" ]]; then
    make -C "$ROOT_DIR" setup-core-full
  else
    make -C "$ROOT_DIR" setup-core-lite
  fi
fi

if [[ "$SKIP_INFRA" -eq 0 ]]; then
  require_command "docker" "Install Docker and Docker Compose plugin, or rerun with --skip-infra."

  if ! docker_ready; then
    echo "Docker daemon is not reachable."
    echo "Start Docker Desktop/service, or rerun with --skip-infra if you already have PostgreSQL/Redis."
    exit 1
  fi

  echo "Starting local infrastructure..."
  docker compose -f "$ROOT_DIR/docker-compose.yml" up -d postgres redis
  wait_for_postgres
else
  echo "Skipping local postgres/redis startup (--skip-infra)."
fi

if [[ "$SKIP_DB_INIT" -eq 0 ]]; then
  echo "Running database migrations and seed..."
  npm run db:init --prefix "$ROOT_DIR/backend"
else
  echo "Skipping database init (--skip-db-init)."
fi

start_service "backend" "npm run dev --prefix backend"
start_service "frontend" "npm run dev --prefix frontend"
start_service "core" "core/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload --app-dir core"

echo
echo "Local stack started."
echo "Logs: $LOG_DIR"
echo "Use ./scripts/dev-status.sh to inspect services."
