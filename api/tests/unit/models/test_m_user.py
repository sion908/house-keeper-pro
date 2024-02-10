import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User

@pytest.mark.asyncio()
class TestUserModel:

    async def test_create_user(self, async_db: AsyncSession) -> None:

        user = User(lineUserID="lineUserID")
        async_db.add(user)

        await async_db.commit()
        await async_db.refresh(user)

        db_user = (
            await async_db.execute(select(User).filter_by(id=user.id))
        ).scalar_one()

        assert db_user.id == user.id
        assert db_user.lineUserID == user.lineUserID
        assert db_user.is_active == True
