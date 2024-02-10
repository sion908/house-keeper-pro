import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
import freezegun
from datetime import (datetime, timedelta)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from crud.user import get_by_lineUserID, upsert

@pytest.mark.asyncio()
class TestUserCrud:

    async def test_get_by_lineUserID(self, async_db: AsyncSession, create_user: User) -> None:
        user = await get_by_lineUserID(db=async_db, lineUserID=create_user.lineUserID)
        assert type(user) == User
        assert user.is_active == True

    async def test_get_by_lineUserID_with_no_data(self, async_db: AsyncSession) -> None:
        user = await get_by_lineUserID(db=async_db, lineUserID="lineID")
        assert user == None

    async def test_upsert(self, async_db: AsyncSession, create_user: User) -> None:

        db_user_be = (
            await async_db.execute(select(User).limit(1))
        ).scalar_one()
        user_attr = {
            "lineUserID": "userID",
            "username": "username",
            "is_active": True
        }
        with freezegun.freeze_time('2015-10-21'):
            user = await upsert(db=async_db, values=user_attr)
            db_user = (
                await async_db.execute(select(User).limit(1))
            ).scalar_one()

        for u in [user, db_user]:
            assert u.lineUserID == user_attr["lineUserID"]
            assert u.username == user_attr["username"]
            assert u.is_active == user_attr["is_active"]
        assert db_user.updated_at != db_user.created_at
        assert db_user.id == db_user_be.id

    async def test_upsert_only_is_active(self, async_db: AsyncSession, create_user: User) -> None:

        user_attr = {
            "lineUserID": "userID",
            "is_active": True
        }
        with freezegun.freeze_time('2015-10-21'):
            user = await upsert(db=async_db, values=user_attr)
            db_user = (
                await async_db.execute(select(User).limit(1))
            ).scalar_one()

        for u in [user, db_user]:
            assert u.lineUserID == user_attr["lineUserID"]
            assert u.username == create_user.username
            assert u.is_active == user_attr["is_active"]
        assert db_user.updated_at != db_user.created_at
        assert db_user.id == create_user.id

    async def test_upsert_no_data(self, async_db: AsyncSession) -> None:

        user_attr = {
            "lineUserID": "userID",
            "username": "username",
            "is_active": True
        }
        user = await upsert(db=async_db, values=user_attr)
        db_user = await async_db.scalar(
            select(User).limit(1)
        )

        for u in [user, db_user]:
            assert u.lineUserID == user_attr["lineUserID"]
            assert u.username == user_attr["username"]
            assert u.is_active == user_attr["is_active"]
        assert db_user.updated_at == db_user.created_at

    async def test_upsert_no_data_only_is_active(self, async_db: AsyncSession) -> None:

        user_attr = {
            "lineUserID": "userID",
            "is_active": True
        }
        user = await upsert(db=async_db, values=user_attr)
        db_user = await async_db.scalar(
            select(User).limit(1)
        )

        for u in [user, db_user]:
            assert u.lineUserID == user_attr["lineUserID"]
            assert u.username == None
            assert u.is_active == user_attr["is_active"]
        assert db_user.updated_at == db_user.created_at

    async def test_upsert_no_data_not_create(self, async_db: AsyncSession) -> None:

        user_attr = {
            "lineUserID": "userID",
            "username": "username",
            "is_active": True
        }
        user = await upsert(db=async_db, values=user_attr, no_create=True)
        db_user = await async_db.scalar(
            select(User).limit(1)
        )

        assert user == None
        assert db_user == None
