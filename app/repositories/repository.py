from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Task, TaskStatus, User


class TaskRepository:

    async def create_task(self, session: AsyncSession, task: Task):
        session.add(task)
        await session.flush()
        return task

    async def get_task(self, session: AsyncSession, task_id: int):
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def list_tasks(self, session: AsyncSession, user_id: int):
        result = await session.execute(
            select(Task).where(Task.assigned_to == user_id)
        )
        return result.scalars().all()

    async def update_task(
        self,
        session: AsyncSession,
        task_id: int,
        values: dict,
    ):
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(**values)
            .returning(Task)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_task(
        self,
        session: AsyncSession,
        task_id: int,
    ):
        stmt = (
            delete(Task)
            .where(Task.id == task_id)
            .returning(Task.id)
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_user(
        self,
        session: AsyncSession,
        user_id: int,
    ):
        result = await session.execute(
            select(User).where(User.id == user_id)
        )

        return result.scalar_one_or_none()

    async def assign_task_to_user(
        self,
        session: AsyncSession,
        task_id: int,
        user_id: int,
    ):
        stmt = (
            update(Task)
            .where(
                Task.id == task_id,
                Task.status == TaskStatus.PENDING,
                Task.assigned_to.is_(None),
            )
            .values(assigned_to=user_id)
            .returning(Task)
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()