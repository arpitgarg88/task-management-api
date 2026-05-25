---
title: Production-Ready Task Management API
author: Arpit Garg
created: 2026-05-21
updated: 2026-05-25
status: Active
tags: fastapi, postgresql, sqlalchemy, alembic, redis, celery, async-api, docker, state-machine
---

# Production-Ready Task Management API

## TL;DR (30 Seconds Read)

Production-ready asynchronous Task Management API built using:

- FastAPI
- PostgreSQL
- SQLAlchemy Async ORM
- Redis Caching
- Celery Background Workers
- Dockerized Infrastructure
- Alembic Migrations

The system supports:

- CRUD task operations
- Redis caching with DB fallback
- Celery async background processing
- Task status state machine validation
- Query filtering and pagination
- Bulk task operations
- Partial failure handling
- Concurrent-safe task assignment
- Layered backend architecture
- Structured logging
- Production-style workflows

---

# Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Developer Documentation](#developer-documentation)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Guide](#setup-guide)
- [Environment Variables](#environment-variables)
- [Docker Setup](#docker-setup)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Running Celery Worker](#running-celery-worker)
- [API Documentation](#api-documentation)
- [Redis Caching](#redis-caching)
- [Task Status State Machine](#task-status-state-machine)
- [Celery Background Tasks](#celery-background-tasks)
- [Bulk Operations](#bulk-operations)
- [Concurrency Handling](#concurrency-handling)
- [Testing Guide](#testing-guide)
- [Database Tables](#database-tables)
- [Common Errors & Fixes](#common-errors--fixes)
- [Useful Docker Commands](#useful-docker-commands)
- [Future Enhancements](#future-enhancements)
- [Changelog](#changelog)

---

# Overview

## Problem Statement

The task management system required:

- Production-grade backend architecture
- Async database support
- Efficient task retrieval
- Controlled task lifecycle management
- Background task execution
- Cache optimization
- Failure resilience
- Bulk task handling
- Concurrent-safe workflows
- Scalable querying support

Without these:

- Repeated DB calls increased latency
- Invalid task transitions corrupted workflows
- Long-running operations blocked APIs
- Redis failures could break APIs
- Concurrent assignments created race conditions
- Bulk workflows became unreliable
- Background processing was unavailable

---

# Solution Summary

This implementation introduces:

- FastAPI async APIs
- PostgreSQL async integration
- Redis cache-aside strategy
- Celery background workers
- Repository-service architecture
- Task status state machine
- Query filtering + pagination
- Bulk operation support
- Partial failure handling
- Concurrent-safe assignment
- Cache invalidation handling
- Graceful Redis fallback
- Dockerized infrastructure

---

# Features

## Core Features

- Create tasks
- Read tasks
- Update tasks
- Delete tasks

---

## Advanced Features

- Redis caching
- Cache invalidation
- Celery background workers
- Background task processing
- State machine validation
- Async PostgreSQL
- Layered architecture
- Docker support
- Alembic migrations
- Structured logging
- Graceful failure handling
- Query filtering
- Pagination
- Bulk task creation
- Bulk task status updates
- Partial failure responses
- Concurrent-safe assignment workflow

---

# Architecture

## High-Level Architecture

```text
Client
   ↓
FastAPI Routes
   ↓
Service Layer
   ↓
Redis Cache
   ↓
Repository Layer
   ↓
SQLAlchemy Async ORM
   ↓
PostgreSQL Database

Background Tasks:
FastAPI → Celery → Redis Broker → Worker
```

---

## Layered Architecture

```mermaid
flowchart TD

A[Client / Swagger UI]

A --> B[Routes Layer]

B --> C[Service Layer]

C --> D[Redis Cache]
C --> E[Repository Layer]

E --> F[SQLAlchemy Async ORM]
F --> G[(PostgreSQL)]

C --> H[Celery Queue]
H --> I[Redis Broker]
I --> J[Celery Worker]
```

---

# Developer Documentation

Detailed internal backend architecture and workflow documentation is available inside the `docs/` directory.

## Available Documents

| Document | Purpose |
|---|---|
| `docs/ARCHITECTURE.md` | Complete system architecture, layers, Redis, Celery, DB, concurrency, scalability |
| `docs/WORKFLOWS.md` | Route-by-route execution lifecycle and internal DB interaction workflows |

---

## Documentation Coverage

The documentation includes:

- layered backend architecture
- request lifecycle
- service orchestration
- repository workflows
- cache lifecycle
- Celery execution pipeline
- state machine execution
- concurrency-safe assignment logic
- transaction lifecycle
- partial failure handling
- background processing workflows
- Redis fallback strategy
- internal route → DB interaction charts
- production deployment architecture

---

## Recommended Reading Order

For new developers:

```text
README.md
   ↓
docs/ARCHITECTURE.md
   ↓
docs/WORKFLOWS.md
   ↓
Swagger Documentation
```

---

## Documentation Philosophy

The docs are intentionally:

- developer-friendly
- onboarding-focused
- architecture-oriented
- workflow-centric
- production-oriented
- scalable for future contributors

---

# Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | API framework |
| PostgreSQL | Primary database |
| SQLAlchemy Async | ORM |
| Alembic | Database migrations |
| Redis | Cache + Celery broker |
| Celery | Background task processing |
| Docker | Containerization |
| Uvicorn | ASGI server |

---

# Project Structure

```text
task-management/
│
├── alembic/
│
├── app/
│   ├── api/
│   │   └── routes.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── redis.py
│   │   └── celery_app.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── repositories/
│   │   └── repository.py
│   │
│   ├── schemas/
│   │   └── schemas.py
│   │
│   ├── services/
│   │   └── service.py
│   │
│   ├── utils/
│   │   └── cache_key.py
│   │
│   ├── tasks.py
│   └── main.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── WORKFLOWS.md
│
├── .env
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md
```

---

# Setup Guide

# 1. Clone Repository

```bash
git clone https://github.com/arpitgarg88/task-management-api
```

---

# 2. Navigate to Project

```bash
cd task-management
```

---

# 3. Create Virtual Environment

## Windows

```bash
python -m venv .venv
```

---

# 4. Activate Virtual Environment

## Windows PowerShell

```bash
.venv\Scripts\Activate.ps1
```

---

# 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in project root.

---

## Example `.env`

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/taskdb

REDIS_URL=redis://localhost:6379/0
```

---

# Docker Setup

# 1. Start PostgreSQL + Redis Containers

```bash
docker compose up -d
```

---

# 2. Verify Containers

```bash
docker ps
```

Expected containers:

- PostgreSQL
- Redis

---

# 3. Stop Containers

```bash
docker compose down
```

---

# Database Setup

# 1. Generate Migration

```bash
alembic revision --autogenerate -m "initial migration"
```

---

# 2. Apply Migration

```bash
alembic upgrade head
```

---

# 3. Verify Tables

Enter PostgreSQL container:

```bash
docker exec -it task_postgres psql -U postgres
```

---

# 4. Connect Database

```sql
\c taskdb
```

---

# 5. Verify Tables

```sql
\dt
```

Expected:

```text
tm_tasks
tm_users
alembic_version
```

---

# Running the Application

# Start FastAPI Server

```bash
uvicorn app.main:app --reload
```

---

# Swagger UI

Open:

```text
http://127.0.0.1:8000/docs
```

---

# Running Celery Worker

# Start Celery Worker

## Windows

```bash
celery -A app.tasks worker -Q task_completion_queue --pool=solo --loglevel=info
```

---

# API Documentation

Swagger automatically documents all API routes.

## Swagger URL

```text
http://127.0.0.1:8000/docs
```

---

## Available APIs

| Method | Route | Purpose |
|---|---|---|
| POST | `/tasks` | Create task |
| GET | `/tasks` | List tasks |
| GET | `/tasks/{task_id}` | Get task |
| PUT | `/tasks/{task_id}` | Update task |
| DELETE | `/tasks/{task_id}` | Delete task |
| POST | `/tasks/{task_id}/assign` | Assign task |
| POST | `/tasks/bulk` | Bulk create |
| PUT | `/tasks/bulk/status` | Bulk status update |

---

# Redis Caching

## Cache Strategy

| Operation | Cache Key | TTL |
|---|---|---|
| Get Task By ID | `task:{task_id}` | 300s |
| List User Tasks | `tasks:user:{user_id}` | 300s |

---

# Cache Invalidation

Triggered on:

- task creation
- task update
- task deletion
- task assignment
- bulk task operations

---

# Cache Logs

```text
[CACHE HIT]
[CACHE MISS]
[CACHE SET]
[CACHE DELETE]
```

---

# Redis Failure Handling

If Redis is unavailable:

- API falls back to PostgreSQL
- Request still succeeds

---

# Task Status State Machine

| Current Status | Allowed Transition |
|---|---|
| PENDING | IN_PROGRESS, CANCELLED |
| IN_PROGRESS | COMPLETED, CANCELLED |
| COMPLETED | Not Allowed |
| CANCELLED | Not Allowed |

---

# Valid Example

```text
PENDING → IN_PROGRESS
```

---

# Invalid Example

```text
COMPLETED → PENDING
```

---

# Invalid Response

```json
{
  "detail": "Invalid status transition"
}
```

---

# Celery Background Tasks

# Purpose

Celery handles asynchronous task execution.

---

# Workflow

```text
Task Updated
    ↓
Celery Queue
    ↓
Redis Broker
    ↓
Celery Worker
    ↓
Background Processing
```

---

# Current Background Features

- Notification simulation
- Analytics simulation
- Activity feed simulation
- Search indexing simulation
- Automatic retries

---

# Celery Logs

```text
[TASK WORKER START]
[TASK NOTIFICATION PROCESSING]
[TASK ANALYTICS PROCESSING]
[TASK ACTIVITY FEED UPDATED]
[TASK SEARCH INDEX UPDATED]
[TASK WORKER DONE]
```

---

# Bulk Operations

The API supports partial-failure bulk workflows.

---

# Bulk Create

```http
POST /tasks/bulk
```

---

# Bulk Status Update

```http
PUT /tasks/bulk/status
```

---

# Partial Failure Example

```json
{
  "results": [
    {
      "success": true
    },
    {
      "success": false,
      "error": "Task not found"
    }
  ]
}
```

---

# Concurrency Handling

Task assignment uses atomic SQL updates to prevent race conditions.

---

# Protected Workflow

```text
Request A assigns task
Request B assigns same task
```

Only one request succeeds.

---

# Conflict Response

```json
{
  "detail": "Task already assigned by another request"
}
```

---

# Testing Guide

# Create User First

Before assigning tasks:

```bash
docker exec -it task_postgres psql -U postgres
```

---

## Connect Database

```sql
\c taskdb
```

---

## Insert User

```sql
INSERT INTO tm_users (username, email, role, is_active)
VALUES ('alice', 'alice@gmail.com', 'USER', true);
```

---

# Create Task

1. Open Swagger UI
2. Execute `POST /tasks`
3. Use `assigned_to=1`

---

# Test Cache

Call:

```text
GET /tasks/1
```

First call:

```text
[CACHE MISS]
```

Second call:

```text
[CACHE HIT]
```

---

# Test Celery Worker

Update task status:

```json
{
  "status": "completed"
}
```

Observe worker logs:

```text
[TASK WORKER START]
[TASK WORKER DONE]
```

---

# Test Bulk Create

```json
{
  "tasks": [
    {
      "title": "Task 1"
    },
    {
      "title": "Task 2"
    }
  ]
}
```

---

# Test State Machine

## Valid

```text
PENDING → IN_PROGRESS
```

---

## Invalid

```text
COMPLETED → PENDING
```

Expected:

```json
{
  "detail": "Invalid status transition"
}
```

---

# Database Tables

# Table: `tm_users`

| Column | Type |
|---|---|
| id | Integer |
| username | String |
| email | String |
| role | Enum |
| is_active | Boolean |

---

# Table: `tm_tasks`

| Column | Type |
|---|---|
| id | Integer |
| title | String |
| description | Text |
| status | Enum |
| assigned_to | Integer |
| created_at | DateTime |
| updated_at | DateTime |

---

# Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| Connection refused | PostgreSQL/Redis not running | Start Docker containers |
| ForeignKeyViolationError | User missing | Insert user first |
| Invalid status transition | Invalid workflow | Use allowed transitions |
| Redis connection error | Redis down | Restart Redis container |
| another operation is in progress | Async event loop misuse | Use dedicated loop in Celery |
| Task already assigned | Concurrent assignment | Retry request |
| Task already assigned by another request | Race condition handling | Request safely rejected |

---

# Useful Docker Commands

# View Running Containers

```bash
docker ps
```

---

# View Logs

```bash
docker logs task_postgres
```

```bash
docker logs task_redis
```

---

# Restart Containers

```bash
docker compose restart
```

---

# Remove Containers

```bash
docker compose down
```

---

# Remove Containers + Volumes

```bash
docker compose down -v
```

---

# Future Enhancements

Potential future improvements:

- JWT authentication
- RBAC authorization
- OpenTelemetry tracing
- Prometheus metrics
- Grafana dashboards
- Flower worker monitoring
- Distributed locking
- API versioning
- Kubernetes deployment
- CI/CD pipelines
- Dead letter queues
- Kafka event streaming
- Automated test suite

---

# Changelog

| Date | Author | Change |
|---|---|---|
| 2026-05-21 | Arpit Garg | Initial CRUD implementation |
| 2026-05-22 | Arpit Garg | Added Redis caching |
| 2026-05-22 | Arpit Garg | Added task state machine |
| 2026-05-23 | Arpit Garg | Added Celery integration |
| 2026-05-23 | Arpit Garg | Added async background processing |
| 2026-05-23 | Arpit Garg | Added production-ready worker handling |
| 2026-05-23 | Arpit Garg | Added filtering and pagination |
| 2026-05-23 | Arpit Garg | Added bulk task operations |
| 2026-05-23 | Arpit Garg | Added partial failure handling |
| 2026-05-25 | Arpit Garg | Added architecture and workflow developer documentation |

---