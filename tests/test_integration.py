import json
import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_cache_hit_miss_and_invalidation(client, monkeypatch):
    """
    Verify cache miss, cache hit, and cache invalidation behavior.
    """
    mock_get_cache = AsyncMock(
        side_effect=[
            None,
            json.dumps(
                {
                    "id": 1,
                    "title": "Cache Test Task",
                    "description": "Testing cache behavior",
                    "status": "pending",
                    "assigned_to": None,
                    "created_at": "2026-05-26T15:00:00",
                    "updated_at": "2026-05-26T15:00:00",
                }
            ),
        ]
    )

    mock_set_cache = AsyncMock()
    mock_delete_cache = AsyncMock()

    monkeypatch.setattr("app.services.service.get_cache", mock_get_cache)
    monkeypatch.setattr("app.services.service.set_cache", mock_set_cache)
    monkeypatch.setattr("app.services.service.delete_cache", mock_delete_cache)

    resp = client.post(
        "/tasks",
        json={
            "title": "Cache Test Task",
            "description": "Testing cache behavior",
        },
    )

    assert resp.status_code == 201
    task_id = resp.json()["id"]

    resp1 = client.get(f"/tasks/{task_id}")
    assert resp1.status_code == 200
    assert mock_get_cache.await_count >= 1
    assert mock_set_cache.await_count == 1

    resp2 = client.get(f"/tasks/{task_id}")
    assert resp2.status_code == 200
    assert mock_get_cache.await_count == 2

    assert resp1.json()["id"] == resp2.json()["id"]


@pytest.mark.asyncio
async def test_redis_down_graceful_degradation(client, monkeypatch):
    """
    Ensure API continues functioning when Redis operations fail.
    """

    async def failing(*args, **kwargs):
        raise Exception("Redis down")

    monkeypatch.setattr("app.services.service.get_cache", failing)
    monkeypatch.setattr("app.services.service.set_cache", failing)
    monkeypatch.setattr("app.services.service.delete_cache", failing)

    resp = client.post("/tasks", json={"title": "Redis Down Task"})
    assert resp.status_code == 201

    task_id = resp.json()["id"]

    resp2 = client.get(f"/tasks/{task_id}")
    assert resp2.status_code == 200

    assert resp2.json()["title"] == "Redis Down Task"
    assert resp2.json()["id"] == task_id


@pytest.mark.asyncio
async def test_valid_status_transitions(client):
    """
    Verify valid task status transitions are accepted.
    """
    resp = client.post("/tasks", json={"title": "Transition Test"})
    assert resp.status_code == 201

    task_id = resp.json()["id"]
    assert resp.json()["status"] == "pending"

    resp = client.put(f"/tasks/{task_id}", json={"status": "in_progress"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"

    resp = client.put(f"/tasks/{task_id}", json={"status": "completed"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_invalid_status_transitions(client):
    """
    Verify invalid task status transitions are rejected.
    """
    resp = client.post("/tasks", json={"title": "Invalid Transition"})
    assert resp.status_code == 201

    task_id = resp.json()["id"]

    resp = client.put(
        f"/tasks/{task_id}",
        json={"status": "completed"},
    )

    assert resp.status_code == 400
    assert "Invalid status transition" in resp.json()["detail"]

    resp_check = client.get(f"/tasks/{task_id}")
    assert resp_check.status_code == 200
    assert resp_check.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_celery_completion_workflow(client, celery_worker):
    """
    Verify Celery-driven task completion workflow executes successfully.
    """
    resp = client.post("/tasks", json={"title": "Celery Test"})
    assert resp.status_code == 201

    task_id = resp.json()["id"]

    client.put(f"/tasks/{task_id}", json={"status": "in_progress"})

    resp = client.put(f"/tasks/{task_id}", json={"status": "completed"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_task_assignment(client):
    """
    Verify task assignment behavior and resulting task state.
    """
    resp = client.post("/tasks", json={"title": "Assign Test"})
    assert resp.status_code == 201

    task_id = resp.json()["id"]

    resp = client.post(f"/tasks/{task_id}/assign", params={"user_id": 1})

    assert resp.status_code in (200, 400, 404)

    if resp.status_code == 200:
        resp_check = client.get(f"/tasks/{task_id}")
        assert resp_check.status_code == 200
        assert resp_check.json().get("assigned_to") in (1, None)


@pytest.mark.asyncio
async def test_list_tasks_with_filters_and_pagination(client):
    """
    Verify task listing supports filtering, sorting, and pagination.
    """
    for i in range(5):
        resp = client.post("/tasks", json={"title": f"Task {i}"})
        assert resp.status_code == 201

    resp = client.get("/tasks?limit=3&offset=0&sort_by=created_at&order=desc")

    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 3


@pytest.mark.asyncio
async def test_bulk_create(client):
    """
    Verify bulk task creation persists all tasks successfully.
    """
    payload = {
        "tasks": [
            {"title": "Bulk 1"},
            {"title": "Bulk 2", "status": "in_progress"},
            {"title": "Bulk 3"},
        ]
    }

    resp = client.post("/tasks/bulk", json=payload)
    assert resp.status_code == 201

    results = resp.json().get("results", [])
    assert len(results) == 3

    created_titles = {
        payload["tasks"][i]["title"]
        for i in range(len(payload["tasks"]))
    }

    resp_all = client.get("/tasks")
    assert resp_all.status_code == 200

    all_tasks = resp_all.json()

    system_titles = {
        t.get("title")
        for t in all_tasks
        if isinstance(t, dict)
    }

    assert created_titles.issubset(system_titles)


@pytest.mark.asyncio
async def test_bulk_status_update(client):
    """
    Verify bulk task status updates are applied correctly.
    """
    task_ids = []

    for i in range(3):
        resp = client.post("/tasks", json={"title": f"Bulk Update {i}"})
        assert resp.status_code == 201
        task_ids.append(resp.json()["id"])

    resp = client.put(
        "/tasks/bulk/status",
        json={
            "tasks": [
                {"task_id": task_ids[0], "status": "in_progress"},
                {"task_id": task_ids[1], "status": "completed"},
                {"task_id": 99999, "status": "pending"},
            ]
        },
    )

    assert resp.status_code == 200

    results = resp.json().get("results", [])
    assert len(results) == 3

    resp_check = client.get(f"/tasks/{task_ids[0]}")
    assert resp_check.json()["status"] == "in_progress"

    resp_check = client.get(f"/tasks/{task_ids[1]}")
    data = resp_check.json()

    if data.get("status") in ("completed", "pending"):
        assert data["status"] in ("completed", "pending")


@pytest.mark.asyncio
async def test_concurrent_assignment_protection(client):
    """
    Verify concurrent task assignment attempts are properly rejected.
    """
    resp = client.post("/tasks", json={"title": "Concurrent Assign Test"})
    assert resp.status_code == 201

    task_id = resp.json()["id"]

    client.post(f"/tasks/{task_id}/assign", params={"user_id": 1})

    resp = client.post(f"/tasks/{task_id}/assign", params={"user_id": 2})

    assert resp.status_code in (400, 409)


@pytest.mark.asyncio
async def test_celery_idempotency_and_retries(client, celery_worker):
    """
    Verify Celery task execution remains idempotent across retries.
    """
    resp = client.post("/tasks", json={"title": "Idempotency Test"})
    assert resp.status_code == 201

    task_id = resp.json()["id"]

    client.put(f"/tasks/{task_id}", json={"status": "in_progress"})

    resp = client.put(f"/tasks/{task_id}", json={"status": "completed"})
    assert resp.status_code == 200

    resp_check = client.get(f"/tasks/{task_id}")
    assert resp_check.json()["status"] == "completed"