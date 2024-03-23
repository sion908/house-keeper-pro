import pytest
from typing import Dict, List
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import User, Form, FormStub, FormClassFloor, FormClassArea


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
        class_area_id, class_floor_id = 1, 1
        form_attrs, form_class_floor_attrs, form_class_area_attrs, form_stub_attrs = [], [], [], []
        for facility_index, (facility, form_class_floor_setting) in enumerate(form_setting.items(), start=1):
            for class_floor_index, (class_floor, form_class_area_setting) in enumerate(form_class_floor_setting.items(), start=1):
                for class_area_index, (class_area, form_stub_setting) in enumerate(form_class_area_setting.items(), start=1):

                    for form_stub_index, (form_stub, form_stub_type) in enumerate(form_stub_setting.items(), start=1):
                        form_stub_attrs.append({
                            "description": f"{form_stub}-description",
                            "title": f"{form_stub}",
                            "order": form_stub_index,
                            "type": form_stub_type,
                            "form_class_area_id": class_area_id
                        })
                    form_class_area_attrs.append({
                        "id": class_area_id,
                        "description": f"{class_area}-description",
                        "title": f"{class_area}",
                        "order": class_area_index,
                        "form_class_floor_id": class_floor_id
                    })
                    class_area_id += 1
                form_class_floor_attrs.append({
                    "id": class_floor_id,
                    "description": f"{class_floor}-description",
                    "title": f"{class_floor}",
                    "order": class_floor_index,
                    "form_id": facility_index
                })
                class_floor_id += 1
            form_attrs.append({
                "id": facility_index,
                "title": f"{facility}",
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
        # await async_db.refresh()

    yield _create_form_with_another
