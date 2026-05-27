import fakeredis
import pytest
import logging
import os

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.redis import init_redis
from app.db.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "pytest_structured.log")

logger = logging.getLogger("pytest_runner")
logger.setLevel(logging.INFO)

if not logger.handlers:
    os.makedirs(LOG_DIR, exist_ok=True)

    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


def pytest_sessionstart(session):
    """
    Log the start of the pytest session.
    """
    logger.info("===== TEST SESSION STARTED =====")


def pytest_sessionfinish(session, exitstatus):
    """
    Log the completion of the pytest session and exit status.
    """
    logger.info(f"===== TEST SESSION FINISHED | exit={exitstatus} =====")


def pytest_runtest_logreport(report):
    """
    Log the result of each executed test case.
    """
    if report.when == "call":
        if report.passed:
            logger.info(f"PASSED: {report.nodeid}")
        elif report.failed:
            logger.error(f"FAILED: {report.nodeid}")
        elif report.skipped:
            logger.warning(f"SKIPPED: {report.nodeid}")


@pytest.fixture
async def test_db_engine():
    """
    Create an in-memory SQLite test database engine.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine):
    """
    Provide an isolated async database session for tests.
    """
    session_factory = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session


@pytest.fixture
def client(test_db_session):
    """
    Create a FastAPI test client with overridden database and Redis dependencies.
    """

    async def override_get_db():
        yield test_db_session

    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async def override_redis():
        return fake_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[init_redis] = override_redis

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def celery_worker():
    """
    Start an in-memory Celery worker for task execution during tests.
    """
    from celery.contrib.testing.worker import start_worker
    from app.core.celery_app import celery_app

    celery_app.conf.update(
        broker_url="memory://",
        backend="cache+memory://",
        task_always_eager=True,
        task_eager_propagates=True,
    )

    with start_worker(
        celery_app,
        quiet=True,
        without_heartbeat=True,
        perform_ping_check=False,
    ) as worker:
        yield worker