from datetime import datetime
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models import Form, FormClassArea, FormClassFloor, FormStub


async def get_by_pk(
    db: AsyncSession,
    form_id: str=None,
    form: Form=None
) -> AsyncIterator[Form]:

    if form_id is None and form is not None:
        form_id = form.id
    form = await db.scalar(
        select(Form)
            .where(Form.id == form_id)
            .options(
                joinedload(Form.class_floors),
                joinedload(Form.class_floors).joinedload(FormClassFloor.class_areas),
                joinedload(Form.class_floors).joinedload(FormClassFloor.class_areas).joinedload(FormClassArea.form_stubs)
            ).limit(1)
    )

    # FormStub を FormStub.order でソート
    form.class_floors.sort(key=lambda class_floor: class_floor.order)
    for class_floor in form.class_floors:
        for class_area in class_floor.class_areas:
            class_area.form_stubs.sort(key=lambda form_stub: form_stub.order)
        class_floor.class_areas.sort(key=lambda class_area: class_area.order)


    return form
