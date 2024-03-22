import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
import freezegun
from datetime import (datetime, timedelta)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.form import get_by_pk
from models import Form, FormStub


@pytest.mark.asyncio()
class TestGetById:
    async def test_main(
            self,
            async_db: AsyncSession,
            create_form_with_another: 'function',
        ) -> None:
        form_stub_attrs = [{
            "description": f"説明-{i}",
            "order": i+1,
            "type": i%2
        } for i in range(3)]

        init_form = await create_form_with_another(form_stub_attrs)

        form = await get_by_pk(db=async_db, form=init_form)
        breakpoint()
        assert type(form) == Form
        assert len(form.form_stubs) == 3
        for i, form_stub_attr in enumerate(form_stub_attrs):
            assert type(form.form_stubs[i]) == FormStub
            assert form.form_stubs[i].form_id == form.id
            assert form.form_stubs[i].description == form_stub_attr["description"]
            assert form.form_stubs[i].order == form_stub_attr["order"]
            assert form.form_stubs[i].type == form_stub_attr["type"]
