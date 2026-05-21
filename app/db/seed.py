from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, Task, UserRole, TaskStatus


async def seed_data(session: AsyncSession):

    result = await session.execute(select(User))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return

    users = [
        User(
            username="alice",
            email="alice@example.com",
            role=UserRole.ADMIN,
        ),
        User(
            username="bob",
            email="bob@example.com",
            role=UserRole.MANAGER,
        ),
        User(
            username="charlie",
            email="charlie@example.com",
            role=UserRole.USER,
        ),
    ]

    session.add_all(users)

    await session.flush()

    tasks = [
        Task(
            title="Build FastAPI CRUD",
            description="Create CRUD APIs",
            status=TaskStatus.TODO,
            assigned_to=users[0].id,
        ),
        Task(
            title="Write Documentation",
            description="Prepare Swagger examples",
            status=TaskStatus.IN_PROGRESS,
            assigned_to=users[1].id,
        ),
        Task(
            title="Setup Docker",
            description="Dockerize PostgreSQL",
            status=TaskStatus.DONE,
            assigned_to=users[2].id,
        ),
    ]

    session.add_all(tasks)

    await session.commit()