import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
import freezegun
from datetime import (datetime, timedelta)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.form import get_by_pk
from models import Form, FormStub, StubType


@pytest.mark.asyncio()
class TestGetById:
    async def test_main(
            self,
            async_db: AsyncSession,
            create_form_with_another: 'function',
        ) -> None:
        form_setting = {
            "施設1": {
                "1階": {
                    "洗面所": {
                        "鏡": StubType.IMG
                    }
                },
                "2階": {
                    "キッチン": {
                        "床": StubType.CHECKBOX,
                        "扉": StubType.CHECKBOX
                    },
                    "リビング": {
                        "床": StubType.CHECKBOX,
                        "鏡": StubType.IMG,
                        "扉": StubType.CHECKBOX
                    }
                },
            }
        }

        await create_form_with_another(form_setting)

        form = await get_by_pk(db=async_db, form_id=1)
        breakpoint()
        assert type(form) == Form
        assert len(form.class_floors) == len(form_setting["施設1"].keys())
