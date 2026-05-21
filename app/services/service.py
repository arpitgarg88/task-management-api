from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Task
from app.repositories.repository import TaskRepository
from app.schemas.schemas import TaskCreateRequest, TaskUpdateRequest, TaskResponse

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
        task = Task(
            title=payload.title,
            description=payload.description,
            status=payload.status,
            assigned_to=payload.assigned_to,
        )

        task = await repo.create_task(session, task)
        return to_response(task)

    @staticmethod
    async def get(session: AsyncSession, task_id: int):
        task = await repo.get_task(session, task_id)

        if not task:
            raise HTTPException(404, "Task not found")

        return to_response(task)

    @staticmethod
    async def list(session: AsyncSession):
        tasks = await repo.list_tasks(session)
        return [to_response(t) for t in tasks]

    @staticmethod
    async def update(session: AsyncSession, task_id: int, payload: TaskUpdateRequest):
        data = payload.model_dump(exclude_unset=True)

        if not data:
            raise HTTPException(400, "No update fields provided")

        updated = await repo.update_task(session, task_id, data)

        if not updated:
            raise HTTPException(404, "Task not found")

        task = await repo.get_task(session, task_id)
        return to_response(task)

    @staticmethod
    async def delete(session: AsyncSession, task_id: int):
        deleted = await repo.delete_task(session, task_id)

        if not deleted:
            raise HTTPException(404, "Task not found")