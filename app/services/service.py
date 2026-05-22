from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.db.models import Task
from app.repositories.repository import TaskRepository
from app.schemas.schemas import TaskCreateRequest, TaskUpdateRequest, TaskResponse

from app.core.redis import get_cache, set_cache, delete_cache
from app.utils.cache_key import task_key, tasks_user_key

repo = TaskRepository()


def to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        assigned_to=task.assigned_to,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


class TaskService:

    @staticmethod
    async def create(session: AsyncSession, payload: TaskCreateRequest):
        task = Task(**payload.model_dump())

        task = await repo.create_task(session, task)
        await session.commit()

        if task.assigned_to:
            await delete_cache(tasks_user_key(task.assigned_to))

        return to_response(task)

    @staticmethod
    async def get(session: AsyncSession, task_id: int):
        key = task_key(task_id)

        cached = await get_cache(key, {"task_id": task_id})
        if cached:
            return TaskResponse(**json.loads(cached))

        task = await repo.get_task(session, task_id)
        if not task:
            raise HTTPException(404, "Task not found")

        response = to_response(task)

        await set_cache(
            key,
            json.dumps(response.model_dump(mode="json")),
            ttl=300
        )

        return response

    @staticmethod
    async def list(session: AsyncSession, user_id: int):
        key = tasks_user_key(user_id)

        cached = await get_cache(key, {"user_id": user_id})
        if cached:
            return [TaskResponse(**t) for t in json.loads(cached)]

        tasks = await repo.list_tasks(session, user_id)
        response = [to_response(t) for t in tasks]

        await set_cache(
            key,
            json.dumps([r.model_dump(mode="json") for r in response]),
            ttl=300
        )

        return response

    @staticmethod
    async def update(session: AsyncSession, task_id: int, payload: TaskUpdateRequest):
        data = payload.model_dump(exclude_unset=True)

        task = await repo.get_task(session, task_id)
        if not task:
            raise HTTPException(404, "Task not found")

        old_user = task.assigned_to

        updated = await repo.update_task(session, task_id, data)
        if not updated:
            raise HTTPException(404, "Task not found")

        await session.commit()

        await delete_cache(task_key(task_id))

        if old_user:
            await delete_cache(tasks_user_key(old_user))

        if "assigned_to" in data and data["assigned_to"]:
            await delete_cache(tasks_user_key(data["assigned_to"]))

        return to_response(updated)

    @staticmethod
    async def delete(session: AsyncSession, task_id: int):
        task = await repo.get_task(session, task_id)
        if not task:
            raise HTTPException(404, "Task not found")

        user_id = task.assigned_to

        deleted = await repo.delete_task(session, task_id)
        if not deleted:
            raise HTTPException(404, "Task not found")

        await session.commit()

        await delete_cache(task_key(task_id))

        if user_id:
            await delete_cache(tasks_user_key(user_id))

        return None