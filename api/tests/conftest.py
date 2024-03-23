import asyncio

import pytest
from typing import Dict, List
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.pool import NullPool
from unittest import mock
from unittest.mock import MagicMock

from database.base_class import Base
from database.db import get_db
from main import app
from models import *  # noqa:F401, F403

@pytest.fixture
def anyio_backend():
    return 'asyncio'

async_engine_mock = create_async_engine(
    url='mysql+aiomysql://hy:ia@hkp_db:3306/local_test_db?charset=utf8mb4',
    echo=True,
    poolclass=NullPool
)
SQLModel = Base


# drop all database every time when test complete
@pytest.fixture(scope='session')
async def async_db_engine():
    async with async_engine_mock.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield async_engine_mock

    async with async_engine_mock.begin() as conn:
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

# truncate all table to isolate tests
# async def mock_session_aware(async_db_engine, monkeypatch):
@pytest.fixture(scope="session", autouse=True)
def mock_session_aware():
    def _mock_session_aware(func):
        async_session = sessionmaker(
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
            bind=async_engine_mock,
            class_=AsyncSession,
        )
        async def _wrapper(*args, **kwargs):
            async with async_session() as session:
                # デコレータ内で利用するために関数に値を渡す
                kwargs["db"] = session
                await session.begin()

                result = await func(*args, **kwargs)

                await session.rollback()

                for table in reversed(SQLModel.metadata.sorted_tables):
                    await session.execute(text('SET SESSION FOREIGN_KEY_CHECKS = 0'))
                    await session.execute(text(f'TRUNCATE {table.name};'))
                    await session.execute(text('SET SESSION FOREIGN_KEY_CHECKS = 1'))
                    await session.commit()
            return result
        return _wrapper
    # mock.patch("database.db.session_aware", _mock_session_aware).start()
    with mock.patch("database.db.session_aware", _mock_session_aware) as _mock:
        yield _mock



async def override_get_db():
    async_session = sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine_mock, class_=AsyncSession
    )
    async with async_session() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# pytestmark = pytest.mark.anyio

@pytest.fixture(scope='session')
async def async_client():
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

@pytest.fixture()
async def create_user(async_db: AsyncSession):
    user = User(lineUserID="userID", username="initName")
    async_db.add(user)

    await async_db.commit()
    await async_db.refresh(user)
    yield user


@pytest.fixture()
async def create_form_with_another(async_db: AsyncSession):
    async def _create_form_with_another(form_setting: Dict[str, Dict[str, Dict[str, List[str]]]]):
        form_attrs, form_class_floor_attrs, form_class_area_attrs, form_stub_attrs = [], [], [], []
        for facility_index, (facility, form_class_floor_setting) in enumerate(form_setting.items(), start=1):
            for class_floor_index, (class_floor, form_class_area_setting) in enumerate(form_class_floor_setting.items(), start=1):
                for class_area_index, (class_area, form_stub_setting) in enumerate(form_class_area_setting.items(), start=1):
                    for form_stub_index, (form_stub, form_stub_type) in enumerate(form_stub_setting.items(), start=1):
                        form_stub_attrs.append({
                            "description": f"{form_stub}-description",
                            "title": f"{form_stub}-title",
                            "order": form_stub_index,
                            "type": form_stub_type,
                            "form_class_area_id": class_area_index
                        })
                    form_class_area_attrs.append({
                        "id": class_area_index,
                        "description": f"{class_area}-description",
                        "title": f"{class_area}-title",
                        "order": class_area_index,
                        "form_class_floor_id": class_floor_index
                    })
                form_class_floor_attrs.append({
                    "id": class_floor_index,
                    "description": f"{class_floor}-description",
                    "title": f"{class_floor}-title",
                    "order": class_floor_index,
                    "form_id": facility_index
                })
            form_attrs.append({
                "id": facility_index,
                "title": f"{facility}-title",
                "description": f"{facility}-description"
            })

        await async_db.execute(
            Form.__table__.insert(),
            form_attrs
        )
        await async_db.execute(
            FormClassFloor.__table__.insert(),
            form_class_floor_attrs
        )
        await async_db.execute(
            FormClassArea.__table__.insert(),
            form_class_area_attrs
        )
        await async_db.execute(
            FormStub.__table__.insert(),
            form_stub_attrs
        )


        await async_db.commit()
        await async_db.refresh()

    yield _create_form_with_another
