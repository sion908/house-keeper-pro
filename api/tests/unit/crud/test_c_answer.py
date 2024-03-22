import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
import freezegun
from datetime import (datetime, timedelta)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile

from crud.answer import create_with_stub
from services.report import ReportService
from models import User


@pytest.mark.asyncio()
class TestCreateWithStub:
    async def test_main(
        self,
        async_db: AsyncSession,
        create_user: User,
        create_form_with_another: 'function',
    ) -> None:
        form_stub_attrs = [{
            "description": f"説明-{i}",
            "order": i+1,
            "type": i%2
        } for i in range(3)]
        init_form = await create_form_with_another(form_stub_attrs)

        report_service = ReportService()

        await report_service.async_init(db=async_db,user=create_user,form_id=init_form.id)
        UploadImagesRequest = report_service.form_scheme()
        form_data = UploadImagesRequest(**{
            "timeInputStart": datetime(2024, 3, 20, 18, 53, 23),
            "timeInputEnd": datetime(2024, 3, 20, 19, 53, 23),
            "img-1-be": [UploadFile(file=None,filename="img-1-be.png")],
            "img-1-af": [UploadFile(file=None,filename="img-1-af.png")],
            "img-3-be": [UploadFile(file=None,filename="img-3-be.png")],
            "img-3-af": [UploadFile(file=None,filename="img-3-af.png")]
        })
        db_answer = await create_with_stub(
            db=async_db,
            form_id=init_form.id,
            user_id=create_user.id,
            form_data=form_data,
            img_keys=[
                "img-1-be",
                "img-1-af",
            ],
        )



        # form = await get_by_pk(db=async_db, form=init_form)
        # breakpoint()
        # assert type(form) == Form
        # assert len(form.form_stubs) == 3
        # for i, form_stub_attr in enumerate(form_stub_attrs):
        #     assert type(form.form_stubs[i]) == FormStub
        #     assert form.form_stubs[i].form_id == form.id
        #     assert form.form_stubs[i].description == form_stub_attr["description"]
        #     assert form.form_stubs[i].order == form_stub_attr["order"]
        #     assert form.form_stubs[i].type == form_stub_attr["type"]
