# StructureClaw

> 开源建筑结构分析与设计平台原型，包含 Web 前端、Node.js API 和 Python 分析引擎。

## 当前状态

这个仓库目前已经整理成可运行的多服务原型，包含：

- `frontend`: Next.js 14 前端
- `backend`: Fastify + Prisma + Redis/Postgres 接入的 API 服务
- `core`: FastAPI 结构分析引擎
- `docker-compose.yml`: 编排数据库、缓存、前后端和 Nginx

目前更接近“可运行的项目骨架”而不是完整产品，部分接口是可用的最小实现，用于保证工程链路能跑通。

## 技术架构

```text
Browser
  -> Next.js frontend (:3000)
  -> Fastify backend (:8000)
  -> FastAPI analysis engine (:8001)
  -> PostgreSQL / Redis
  -> Nginx reverse proxy (Docker only)
```

## 目录结构

```text
structureclaw/
├── backend/                 # Fastify API + Prisma
├── core/                    # FastAPI 分析引擎
├── frontend/                # Next.js 前端
├── docker/                  # Nginx 配置
├── docs/                    # 预留文档目录
├── plugins/                 # 预留插件目录
├── services/                # 预留微服务目录
├── tests/                   # 预留测试目录
├── .env.example             # Docker Compose 用环境变量示例
├── Makefile                 # 常用开发命令
└── docker-compose.yml
```

## 环境要求

推荐直接使用 Docker（门槛最低）：

- Docker Engine / Docker Desktop
- Docker Compose v2

本地源码开发（非 Docker）时需要：

- Node.js >= 18
- Python >= 3.10
- PostgreSQL >= 14（必须）
- Redis >= 7（可选，不启用时自动降级内存缓存）

## 快速开始

### 方式一（推荐）：Docker Compose

1. 复制根目录环境变量：

```bash
cp .env.example .env
```

2. 启动全部服务（最少一步）：

```bash
make up
```

3. 访问：

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Analysis Engine: `http://localhost:8001`

### 方式二：一键本地启动

```bash
make local-up
```

这个命令会自动：

- 补齐缺失的环境变量文件
- 检查并安装前后端依赖（使用 `npm ci`）
- 创建 `core/.venv`
- 启动 `postgres` 和 `redis`（Docker）
- 执行 Prisma migration 和 seed
- 启动前端、后端和分析引擎

如果你要使用完整分析依赖，可以改用：

```bash
make local-up-full
```

停止和查看状态：

```bash
make local-status
make local-down
```

### 方式三：本地开发（已有外部数据库/缓存）

如果你已经有可用的 PostgreSQL/Redis，不想由脚本启动 Docker：

```bash
make local-up-noinfra
```

默认会执行 DB 初始化；若你已初始化过数据库，可直接：

```bash
./scripts/dev-up.sh lite --skip-infra --skip-db-init
```

### 方式四：手动分步启动

1. 安装前后端依赖：

```bash
make install
```

2. 准备后端环境变量：

```bash
cp backend/.env.example backend/.env
```

3. 启动数据库和 Redis：

```bash
make db-up
```

4. 初始化数据库结构和种子数据：

```bash
make db-init
```

5. 准备 Python 分析引擎环境：

轻量模式，仅用于本地跑通接口和简化分析：

```bash
make setup-core-lite
```

完整模式，安装全部分析依赖：

```bash
make setup-core-full
```

6. 分别启动三个服务：

```bash
make dev-backend
```

```bash
make dev-frontend
```

```bash
make dev-core-lite
```

如果你装的是完整依赖，也可以使用：

```bash
make dev-core-full
```

## 常用命令

```bash
make help
make up
make install
make build
make db-up
make db-down
make db-init
make docker-up
make docker-down
make local-up
make local-up-noinfra
make local-down
make local-status
make health
```

## 环境变量

### 根目录 `.env`

用于 `docker compose`：

```bash
OPENAI_API_KEY=
```

### `backend/.env`

复制自 `backend/.env.example`，主要字段：

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `ANALYSIS_ENGINE_URL`
- `OPENAI_API_KEY`

说明：

- `OPENAI_API_KEY` 是可选的，未配置时聊天接口自动降级提示
- `REDIS_URL=disabled` 表示禁用 Redis，后端自动降级为内存缓存

### Prisma 初始化

后端现在已经包含：

- `backend/prisma/migrations/20260308000100_init/migration.sql`
- `backend/prisma/seed.ts`

常用命令：

```bash
npm run db:validate --prefix backend
npm run db:deploy --prefix backend
npm run db:seed --prefix backend
npm run db:init --prefix backend
```

### `frontend/.env.local`

可参考 `frontend/.env.example`：

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 已验证的运行状态

已验证：

- 后端可成功编译
- `docker compose config` 校验通过
- Prisma schema 校验通过

说明：

- 在当前机器上 Docker daemon 无访问权限，因此未能在本机完成 `make local-up` 的全链路实启；如你的环境 Docker 可用，该流程应可直接跑通。
- 前端 `next build` 在本机文件系统上触发 `EXDEV`（跨设备 rename）错误；这通常与宿主文件系统挂载方式有关，不影响 `next dev` 本地开发启动。

## 当前已实现的主要接口

### Backend

- `GET /health`
- `GET /docs`
- `GET /api/v1`
- `GET /api/v1/users/*`
- `GET /api/v1/projects/*`
- `GET /api/v1/skills/*`
- `GET /api/v1/community/*`
- `GET /api/v1/analysis/*`

### Core

- `GET /`
- `GET /health`
- `POST /analyze`
- `POST /code-check`
- `POST /design/beam`
- `POST /design/column`

## 已知说明

- 当前部分后端业务实现属于“最小可运行版本”，用于确保启动链路、数据流和接口结构可用
- 如果未配置 Redis，后端会使用内存缓存降级模式
- `core/requirements.txt` 包含较重的工程分析依赖，首次安装可能较慢
- `core/requirements-lite.txt` 适合本地快速起服务，但不代表具备完整分析能力

## 后续建议

适合下一步继续完善的方向：

1. 为后端补充 Prisma migration 和初始化 seed
2. 为主要 API 增加自动化测试
3. 给前端补更多真实页面，而不仅是首页
4. 把当前最小实现逐步替换成真实业务逻辑

## 许可证

本项目采用 MIT 许可证，详见 `LICENSE`。
