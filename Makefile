SHELL := /bin/bash

.PHONY: help install setup-core-lite setup-core-full dev-backend dev-frontend dev-core-lite dev-core-full build db-up db-down db-init docker-up docker-down local-up local-up-full local-up-noinfra local-down local-status health up

help:
	@echo "Available targets:"
	@echo "  install         Install frontend and backend npm dependencies"
	@echo "  setup-core-lite Create core .venv with lightweight dependencies"
	@echo "  setup-core-full Create core .venv with full dependencies"
	@echo "  dev-backend     Start backend in watch mode"
	@echo "  dev-frontend    Start frontend in dev mode"
	@echo "  dev-core-lite   Start analysis engine with lightweight deps"
	@echo "  dev-core-full   Start analysis engine with full deps"
	@echo "  build           Build frontend and backend"
	@echo "  db-up           Start postgres and redis only"
	@echo "  db-down         Stop postgres and redis"
	@echo "  db-init         Run Prisma migrations and seed"
	@echo "  docker-up       Start full docker compose stack"
	@echo "  docker-down     Stop full docker compose stack"
	@echo "  local-up        One-command local startup (lite core profile)"
	@echo "  local-up-full   One-command local startup (full core profile)"
	@echo "  local-up-noinfra Start local app stack without starting postgres/redis docker containers"
	@echo "  local-down      Stop local app processes and infra"
	@echo "  local-status    Show local app process/health status"
	@echo "  health          Check local service health endpoints"
	@echo "  up              Alias of docker-up"

install:
	npm install --prefix backend
	npm install --prefix frontend

setup-core-lite:
	python -m venv core/.venv
	core/.venv/bin/pip install -r core/requirements-lite.txt

setup-core-full:
	python -m venv core/.venv
	core/.venv/bin/pip install -r core/requirements.txt

dev-backend:
	npm run dev --prefix backend

dev-frontend:
	npm run dev --prefix frontend

dev-core-lite:
	core/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload --app-dir core

dev-core-full:
	core/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload --app-dir core

build:
	npm run build --prefix backend
	npm run build --prefix frontend

db-up:
	docker compose up -d postgres redis

db-down:
	docker compose stop postgres redis

db-init:
	npm run db:init --prefix backend

docker-up:
	docker compose up --build

docker-down:
	docker compose down

local-up:
	./scripts/dev-up.sh

local-up-full:
	./scripts/dev-up.sh full

local-up-noinfra:
	./scripts/dev-up.sh lite --skip-infra

local-down:
	./scripts/dev-down.sh

local-status:
	./scripts/dev-status.sh

health:
	curl http://localhost:8000/health
	curl http://localhost:8001/health
	curl -I http://localhost:3000

up: docker-up
