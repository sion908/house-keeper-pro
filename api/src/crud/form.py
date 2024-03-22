from datetime import datetime
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models import Form
from schemas.user import UserCreate


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
                joinedload(Form.form_stubs)
            ).limit(1)
    )

    # FormStub を FormStub.order でソート
    form.form_stubs.sort(key=lambda form_stub: form_stub.order)

    return form
