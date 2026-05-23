---
title: Production-Ready Task Management API
author: Arpit Garg
created: 2026-05-21
updated: 2026-05-23
status: Active
ticket: INTERN-TASK-MANAGEMENT
pr: N/A
tags: fastapi, postgresql, sqlalchemy, alembic, redis, celery, async-api, docker, state-machine
---

# Production-Ready Task Management API

## TL;DR (30 Seconds Read)

Production-ready Task Management API built using:

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
- Layered architecture
- Async PostgreSQL integration
- Cache invalidation strategies
- Structured logging
- Production-style backend workflows

---

# Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
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
- [Testing Guide](#testing-guide)
- [Database Tables](#database-tables)
- [Common Errors & Fixes](#common-errors--fixes)
- [Developer Guidelines](#developer-guidelines)
- [Future Enhancements](#future-enhancements)

---

# Overview

## Problem Statement

The task management system required:

- Production-grade architecture
- Async database support
- Efficient task retrieval
- Controlled task lifecycle
- Background task execution
- Cache optimization
- Fault tolerance

Without these:

- Repeated DB calls increased latency
- Invalid task transitions corrupted workflows
- Long-running operations blocked APIs
- Redis failures could break APIs
- Background processing was unavailable

---

## Solution Summary

This implementation introduces:

- FastAPI async APIs
- PostgreSQL async integration
- Redis caching layer
- Celery background workers
- Repository-service architecture
- Task status state machine
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
- Celery async workers
- Background task processing
- State machine validation
- Async PostgreSQL
- Layered architecture
- Docker support
- Alembic migrations
- Structured logging
- Graceful failure handling

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
````

---

## Layered Architecture

```mermaid
flowchart TD

A[Client / Swagger UI]

A --> B[Routes Layer]
B --> C[Service Layer]

C --> D[Redis Cache]
C --> E[Repository Layer]

E --> F[SQLAlchemy ORM]
F --> G[(PostgreSQL)]

C --> H[Celery Queue]
H --> I[Redis Broker]
I --> J[Celery Worker]
```

---

# Tech Stack

| Technology       | Purpose                    |
| ---------------- | -------------------------- |
| FastAPI          | API framework              |
| PostgreSQL       | Primary database           |
| SQLAlchemy Async | ORM                        |
| Alembic          | Database migrations        |
| Redis            | Cache + Celery broker      |
| Celery           | Background task processing |
| Docker           | Containerization           |
| Uvicorn          | ASGI server                |

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
│   ├── cache/
│   │   └── cache.py
│   │
│   ├── core/
│   │   ├── config.py
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
│   ├── tasks.py
│   └── main.py
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
git clone <your-repository-url>
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

## Windows CMD

```bash
.venv\Scripts\activate.bat
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
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/taskdb

REDIS_URL=redis://localhost:6379/0

CELERY_BROKER_URL=redis://localhost:6379/0

CELERY_RESULT_BACKEND=redis://localhost:6379/0
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

* PostgreSQL
* Redis

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

## Linux / Mac

```bash
celery -A app.tasks worker -Q task_completion_queue --loglevel=info
```

---

# Why `--pool=solo` on Windows?

Windows does not fully support prefork multiprocessing used by Celery.

Using:

```bash
--pool=solo
```

prevents worker crashes on Windows.

---

# API Documentation

# POST `/tasks`

## Create Task

### Request

```json
{
  "title": "Build Redis Cache",
  "description": "Implement Redis caching",
  "assigned_to": 1,
  "status": "PENDING"
}
```

---

# GET `/tasks`

## Fetch All Tasks

### Cache Key

```text
tasks:user:{user_id}
```

---

# GET `/tasks/{task_id}`

## Fetch Task By ID

### Cache Key

```text
task:{task_id}
```

---

# PUT `/tasks/{task_id}`

## Update Task

Supports:

* title update
* description update
* status update

---

# DELETE `/tasks/{task_id}`

## Delete Task

Returns:

```text
204 No Content
```

---

# Redis Caching

# Cache Strategy

| Operation       | Cache Key              | TTL  |
| --------------- | ---------------------- | ---- |
| Get Task By ID  | `task:{task_id}`       | 300s |
| List User Tasks | `tasks:user:{user_id}` | 300s |

---

# Cache Invalidation

Triggered on:

* task creation
* task update
* task deletion

---

# Cache Logs

```text
[CACHE HIT]
[CACHE MISS]
[REDIS ERROR]
```

---

# Redis Failure Handling

If Redis is unavailable:

* API falls back to PostgreSQL
* Request still succeeds
* Warning logs generated

---

# Task Status State Machine

| Current Status | Allowed Transition     |
| -------------- | ---------------------- |
| PENDING        | IN_PROGRESS, CANCELLED |
| IN_PROGRESS    | COMPLETED, CANCELLED   |
| COMPLETED      | Not Allowed            |
| CANCELLED      | Not Allowed            |

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

Example workflow:

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

* Async task completion workflow
* Status updates
* Notification simulation
* Analytics simulation
* Automatic retries
* Retry backoff

---

# Celery Logs

```text
[TASK WORKER START]
[TASK STATUS UPDATED]
[TASK NOTIFICATION SENT]
[TASK ANALYTICS UPDATED]
[TASK WORKER DONE]
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
  "status": "COMPLETED"
}
```

Observe worker logs:

```text
[TASK WORKER START]
[TASK STATUS UPDATED]
[TASK WORKER DONE]
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

| Column    | Type    |
| --------- | ------- |
| id        | Integer |
| username  | String  |
| email     | String  |
| role      | Enum    |
| is_active | Boolean |

---

# Table: `tm_tasks`

| Column      | Type     |
| ----------- | -------- |
| id          | Integer  |
| title       | String   |
| description | Text     |
| status      | Enum     |
| assigned_to | Integer  |
| created_at  | DateTime |
| updated_at  | DateTime |

---

# Common Errors & Fixes

| Error                                      | Cause                              | Fix                                  |
| ------------------------------------------ | ---------------------------------- | ------------------------------------ |
| `Connection refused`                       | PostgreSQL/Redis not running       | Start Docker containers              |
| `ForeignKeyViolationError`                 | User missing                       | Insert user first                    |
| `Invalid status transition`                | Invalid workflow                   | Use allowed transitions              |
| `Redis connection error`                   | Redis down                         | Restart Redis container              |
| `another operation is in progress`         | Async event loop misuse            | Use dedicated loop in Celery         |
| `'NoneType' object has no attribute send'` | Notification service misconfigured | Initialize mail/notification service |

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

# Developer Guidelines

# Do's

* Keep business logic inside services
* Keep DB operations inside repositories
* Use async DB sessions
* Validate state transitions
* Invalidate cache after updates
* Handle Redis failures gracefully
* Use structured logging

---

# Don'ts

* Do not query DB directly from routes
* Do not bypass service layer
* Do not bypass repository layer
* Do not mutate status without validation
* Do not depend entirely on Redis
* Do not share AsyncSession globally

---

# Future Enhancements

* [ ] JWT Authentication
* [ ] Role-based access control
* [ ] Pagination
* [ ] Filtering
* [ ] Bulk task operations
* [ ] WebSocket notifications
* [ ] Prometheus metrics
* [ ] Grafana dashboards
* [ ] Integration testing
* [ ] Kubernetes deployment

---

# Changelog

| Date       | Author     | Change                                 |
| ---------- | ---------- | -------------------------------------- |
| 2026-05-21 | Arpit Garg | Initial CRUD implementation            |
| 2026-05-22 | Arpit Garg | Added Redis caching                    |
| 2026-05-22 | Arpit Garg | Added task state machine               |
| 2026-05-23 | Arpit Garg | Added Celery integration               |
| 2026-05-23 | Arpit Garg | Added async background processing      |
| 2026-05-23 | Arpit Garg | Added production-ready worker handling |

---

```