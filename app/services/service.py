from datetime import datetime
import json
import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import delete_cache, get_cache, set_cache
from app.db.models import Task, TaskStatus
from app.repositories.repository import TaskRepository
from app.schemas.schemas import (
    TaskCreateRequest,
    TaskResponse,
    TaskUpdateRequest,
)
from app.tasks import process_task_completion
from app.utils.cache_key import task_key, tasks_user_key

repo = TaskRepository()
logger = logging.getLogger("task_status")

class TaskStateMachine:

    transitions = {
        TaskStatus.PENDING: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
        TaskStatus.IN_PROGRESS: {TaskStatus.COMPLETED,TaskStatus.CANCELLED},
        TaskStatus.COMPLETED: set(),
        TaskStatus.CANCELLED: set(),
    }

    @classmethod
    def can_transition(cls, from_status, to_status):
        return to_status in cls.transitions.get(from_status, set())

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
        await set_cache(key, json.dumps(response.model_dump(mode="json")), ttl=300)
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
            json.dumps([r.model_dump(mode="json") for r in response]), ttl=300
        )
        return response

    @staticmethod
    async def update(
        session: AsyncSession,
        task_id: int,
        payload: TaskUpdateRequest,
    ):
        data = payload.model_dump(exclude_unset=True)

        task = await repo.get_task(session, task_id)

        if not task:
            raise HTTPException(404, "Task not found")

        old_user = task.assigned_to
        old_status = task.status

        new_status = data.get("status")

        if new_status:

            if not TaskStateMachine.can_transition(old_status, new_status):
                raise HTTPException(
                    400,
                    detail=(
                        f"Invalid status transition "
                        f"from '{old_status}' to '{new_status}'"
                    ),
                )

        if new_status == TaskStatus.COMPLETED:
            updated_task = await repo.update_task(session, task_id, {"status": TaskStatus.COMPLETED})
            await session.commit()
            await delete_cache(task_key(task_id))
            if old_user:
                await delete_cache(tasks_user_key(old_user))

            process_task_completion.delay(task.id)
            logger.info(
                f"[TASK QUEUED] task_id={task.id} for background completion"
            )
            return to_response(updated_task)

        # Normal updates
        updated = await repo.update_task(session, task_id, data)

        await session.commit()

        await delete_cache(task_key(task_id))

        if old_user:
            await delete_cache(tasks_user_key(old_user))

        if new_status and new_status != old_status:

            logger.info(
                f"[TASK STATUS CHANGE] "
                f"user_id={updated.assigned_to} "
                f"task_id={updated.id} "
                f"old_status={old_status} "
                f"new_status={new_status} "
                f"timestamp={datetime.utcnow().isoformat()}"
            )

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

    @staticmethod
    async def assign_task_to_user(session: AsyncSession, task_id: int, user_id: int):

        user = await repo.get_user(session, user_id)

        if not user or not user.is_active:

            logger.warning(
                f"[TASK ASSIGN FAILED] "
                f"task_id={task_id} "
                f"user_id={user_id} "
                f"outcome=INVALID_USER"
            )

            raise HTTPException(
                400,
                "User invalid or inactive",
            )

        task = await repo.get_task(session, task_id)

        if not task:

            logger.warning(
                f"[TASK ASSIGN FAILED] "
                f"task_id={task_id} "
                f"user_id={user_id} "
                f"outcome=TASK_NOT_FOUND"
            )

            raise HTTPException(404, "Task not found")

        if task.status != TaskStatus.PENDING:

            logger.warning(
                f"[TASK ASSIGN FAILED] "
                f"task_id={task_id} "
                f"user_id={user_id} "
                f"outcome=INVALID_STATUS"
            )

            raise HTTPException(400, "Task not assignable")

        if task.assigned_to is not None:

            logger.warning(
                f"[TASK ASSIGN FAILED] "
                f"task_id={task_id} "
                f"user_id={user_id} "
                f"outcome=ALREADY_ASSIGNED"
            )

            raise HTTPException(400, "Task already assigned")

        updated = await repo.assign_task_to_user(
            session,
            task_id,
            user_id,
        )

        if not updated:
            await session.rollback()

            logger.warning(
                f"[TASK ASSIGN FAILED] "
                f"task_id={task_id} "
                f"user_id={user_id} "
                f"outcome=CONCURRENT_MODIFICATION"
            )

            raise HTTPException(409, "Task already assigned by another request")

        await session.commit()

        await delete_cache(task_key(task_id))
        await delete_cache(tasks_user_key(user_id))

        logger.info(
            f"[TASK ASSIGNED] "
            f"task_id={task_id} "
            f"user_id={user_id} "
            f"outcome=SUCCESS "
            f"timestamp={datetime.utcnow().isoformat()}"
        )

        return to_response(updated)