import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import User, Form, FormStub


@pytest.fixture()
async def create_user(async_db: AsyncSession):
    user = User(lineUserID="userID", username="initName")
    async_db.add(user)

    await async_db.commit()
    await async_db.refresh(user)
    yield user


@pytest.fixture()
async def create_form_with_another(async_db: AsyncSession):
    async def _create_card_with_another(form_stub_attrs):
        form = Form(
            title="title",
            description="description"
        )

        async_db.add(form)

        await async_db.commit()
        await async_db.refresh(form)
        for i in range(len(form_stub_attrs)):
            form_stub_attrs[i]["form_id"] = form.id

        await async_db.execute(
            FormStub.__table__.insert(),
            form_stub_attrs
        )
        await async_db.commit()
        return form

    yield _create_card_with_another
