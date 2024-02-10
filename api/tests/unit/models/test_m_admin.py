import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Admin

@pytest.mark.asyncio()
class TestAdminModel:

    async def test_create_admin_with_no_data(self, async_db: AsyncSession) -> None:
        admin = Admin()
        async_db.add(admin)

        await async_db.commit()
        await async_db.refresh(admin)

        db_admin = (
            await async_db.execute(select(Admin).filter_by(id=admin.id).limit(1))
        ).scalar_one()

        assert db_admin.id == admin.id
        assert db_admin.username == None
        assert db_admin.password == None
        assert db_admin.user_id == None

    async def test_create_admin(
            self,
            async_db: AsyncSession,
            create_user: User
        ) -> None:
        admin_attr = {
            "username": "user",
            "password": "password",
            "user": create_user
        }
        admin = Admin(**admin_attr)
        async_db.add(admin)

        await async_db.commit()
        await async_db.refresh(admin)

        db_admin = (
            await async_db.execute(select(Admin).filter_by(id=admin.id, password=admin.password).limit(1))
        ).scalar_one()

        assert db_admin.id == admin.id
        assert db_admin.username == admin.username
        assert db_admin.user == create_user
        assert type(db_admin.user) == User
