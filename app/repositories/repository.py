from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Task, User


class TaskRepository:
    
    async def create_task(self, session: AsyncSession, task: Task):
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

    async def get_task(self, session: AsyncSession, task_id: int):
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def list_tasks(self, session: AsyncSession):
        result = await session.execute(select(Task))
        return result.scalars().all()

    async def update_task(self, session: AsyncSession, task_id: int, values: dict):
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(**values)
            .returning(Task.id)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none()

    async def delete_task(self, session: AsyncSession, task_id: int):
        stmt = delete(Task).where(Task.id == task_id).returning(Task.id)
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none()