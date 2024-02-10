import asyncio

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.pool import NullPool
from unittest.mock import MagicMock

from database.base_class import Base
from database.db import get_db
from main import app
from models import *  # noqa:F401, F403

@pytest.fixture
def anyio_backend():
    return 'asyncio'

async_engine = create_async_engine(
    url='mysql+aiomysql://hy:ia@stamp_rally_db:3306/local_test_db?charset=utf8mb4',
    echo=True,
    poolclass=NullPool
)
SQLModel = Base


# drop all database every time when test complete
@pytest.fixture(scope='session')
async def async_db_engine():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# truncate all table to isolate tests
@pytest.fixture()
async def async_db(async_db_engine, monkeypatch):
    async_session = sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession,
    )

    async with async_session() as session:
        monkeypatch.setattr('database.db.get_db', MagicMock(return_value=session))
        await session.begin()

        yield session

        await session.rollback()

        for table in reversed(SQLModel.metadata.sorted_tables):
            await session.execute(text('SET SESSION FOREIGN_KEY_CHECKS = 0'))
            await session.execute(text(f'TRUNCATE {table.name};'))
            await session.execute(text('SET SESSION FOREIGN_KEY_CHECKS = 1'))
            await session.commit()


async def override_get_db():
    async_session = sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
    )
    async with async_session() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# pytestmark = pytest.mark.anyio

@pytest.fixture(scope='session')
async def async_client() -> AsyncClient:
    # return AsyncClient(app=app, base_url='http://localhost')
    async with AsyncClient(app=app, base_url="http://test") as client:
        print("Client is ready")
        yield client


# let test session to know it is running inside event loop
# @pytest.fixture(scope='session')
# def event_loop():
#     policy = asyncio.get_event_loop_policy()
#     loop = policy.new_event_loop()
#     yield loop
#     loop.close()


class MockResponse:
    def __init__(self, json_data=None, status_code=None, content=None):
        self.json_data = json_data
        self.status_code = status_code
        self.content = content

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code!=200:
            raise


@pytest.fixture()
def mock_response():
    return MockResponse
