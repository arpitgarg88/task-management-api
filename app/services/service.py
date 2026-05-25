import json
import logging
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import delete_cache, get_cache, set_cache
from app.db.models import Task, TaskStatus
from app.repositories.repository import TaskRepository
from app.schemas.schemas import (
    BulkStatusUpdateRequest,
    BulkStatusUpdateResponse,
    BulkStatusUpdateItemResponse,
    BulkTaskCreateRequest,
    BulkTaskCreateResponse,
    BulkTaskCreateItemResponse,
    SortOrder,
    TaskCreateRequest,
    TaskResponse,
    TaskSortBy,
    TaskUpdateRequest,
)
from app.tasks import process_task_completion
from app.utils.cache_key import task_key, tasks_user_key

"""
Business service layer for task management workflows.

Responsible for:
- validation
- orchestration
- caching
- transactional behavior
- state transitions
- background task dispatching
"""

repo = TaskRepository()
logger = logging.getLogger("task_status")

class TaskStateMachine:
    """
    Controls valid task lifecycle transitions.

    Prevents invalid workflow mutations such as:
    COMPLETED -> PENDING
    CANCELLED -> IN_PROGRESS
    """
    transitions = {
        TaskStatus.PENDING: {
            TaskStatus.IN_PROGRESS,
            TaskStatus.CANCELLED,
        },
        TaskStatus.IN_PROGRESS: {
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        },
        TaskStatus.COMPLETED: set(),
        TaskStatus.CANCELLED: set(),
    }
    
    @classmethod
    def can_transition(cls, from_status, to_status):
        """
        Checks whether task status transition is allowed.

        Args:
            from_status: Current task status.
            to_status: Requested next status.

        Returns:
            bool: True if transition is valid.
        """
        return to_status in cls.transitions.get(from_status, set())

def to_response(task: Task) -> TaskResponse:
    """
    Converts ORM Task model into API response schema.
    """
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
    """
    Service layer containing business logic for task management.

    Responsibilities:
    - validation
    - cache orchestration
    - state machine enforcement
    - transaction handling
    - async worker triggering
    """
    @staticmethod
    async def create(session: AsyncSession, payload: TaskCreateRequest):
        """
    Creates a new task and invalidates related cache entries.
    """
        task = Task(**payload.model_dump())

        task = await repo.create_task(session, task)
        await session.commit()

        if task.assigned_to:
            await delete_cache(tasks_user_key(task.assigned_to))

        return to_response(task)

    @staticmethod
    async def list(
        session: AsyncSession,
        status: TaskStatus | None = None,
        assigned_to: int | None = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: TaskSortBy = TaskSortBy.CREATED_AT,
        order: SortOrder = SortOrder.DESC,
    ):
        """
        Returns filtered and paginated task list.
        """
        tasks = await repo.list_tasks(
            session=session,
            status=status,
            assigned_to=assigned_to,
            limit=limit,
            offset=offset,
            sort_by=sort_by.value,
            order=order.value,
        )

        return [to_response(task) for task in tasks]

    @staticmethod
    async def get(session: AsyncSession, task_id: int):
        """
        Fetches task by ID using cache-first strategy.

        Falls back to database on cache miss.
        """
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
            ttl=300,
        )
        return response

    @staticmethod
    async def update(
        session: AsyncSession,
        task_id: int,
        payload: TaskUpdateRequest,
    ):
        """
        Updates task fields with lifecycle transition validation.

        Triggers asynchronous completion workflow when task
        moves into COMPLETED state.
        """
        data = payload.model_dump(exclude_unset=True)

        task = await repo.get_task(session, task_id)

        if not task:
            raise HTTPException(404, "Task not found")

        old_user = task.assigned_to
        old_status = task.status

        new_status = data.get("status")

        if new_status:

            if not TaskStateMachine.can_transition(
                old_status,
                new_status,
            ):
                raise HTTPException(
                    400,
                    detail=(
                        f"Invalid status transition "
                        f"from '{old_status}' to '{new_status}'"
                    ),
                )

        if new_status == TaskStatus.COMPLETED:

            updated_task = await repo.update_task(
                session,
                task_id,
                {"status": TaskStatus.COMPLETED},
            )

            await session.commit()
            await delete_cache(task_key(task_id))
            if old_user:
                await delete_cache(tasks_user_key(old_user))

            process_task_completion.delay(task.id)
            logger.info(
                f"[TASK QUEUED] task_id={task.id}"
            )
            return to_response(updated_task)

        updated = await repo.update_task(
            session,
            task_id,
            data,
        )

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
        """
        Deletes task and invalidates related cache entries.
        """
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
    async def assign_task_to_user(
        session: AsyncSession,
        task_id: int,
        user_id: int,
    ):
        """
        Assigns pending unassigned task to active user.

        Includes concurrency-safe assignment protection.
        """
        user = await repo.get_user(session, user_id)

        if not user or not user.is_active:
            raise HTTPException(400, "User invalid or inactive")

        task = await repo.get_task(session, task_id)

        if not task:
            raise HTTPException(404, "Task not found")

        if task.status != TaskStatus.PENDING:
            raise HTTPException(400, "Task not assignable")

        if task.assigned_to is not None:
            raise HTTPException(400, "Task already assigned")

        updated = await repo.assign_task_to_user(
            session,
            task_id,
            user_id,
        )

        if not updated:
            await session.rollback()
            raise HTTPException(
                409,
                "Task already assigned by another request",
            )

        await session.commit()

        await delete_cache(task_key(task_id))
        await delete_cache(tasks_user_key(user_id))

        return to_response(updated)

    @staticmethod
    async def bulk_create(
        session: AsyncSession,
        payload: BulkTaskCreateRequest,
    ):
        """
        Creates multiple tasks with partial failure handling.
        """
        results = []
        for item in payload.tasks:
            try:
                created = await TaskService.create(session, item)
                results.append(
                    BulkTaskCreateItemResponse(
                        success=True,
                        data=created,
                    )
                )

            except Exception as exc:
                results.append(
                    BulkTaskCreateItemResponse(
                        success=False,
                        error=str(exc),
                    )
                )
        return BulkTaskCreateResponse(results=results)

    @staticmethod
    async def bulk_update_status(
        session: AsyncSession,
        payload: BulkStatusUpdateRequest,
    ):
        """
        Updates status for multiple tasks independently.

        Failures in one task do not interrupt remaining updates.
        """
        results = []
        for item in payload.tasks:
            try:
                updated = await TaskService.update(
                    session=session,
                    task_id=item.task_id,
                    payload=TaskUpdateRequest(
                        status=item.status
                    ),
                )
                results.append(
                    BulkStatusUpdateItemResponse(
                        task_id=item.task_id,
                        success=True,
                        data=updated,
                    )
                )

            except Exception as exc:
                results.append(
                    BulkStatusUpdateItemResponse(
                        task_id=item.task_id,
                        success=False,
                        error=str(exc),
                    )
                )
        return BulkStatusUpdateResponse(results=results)