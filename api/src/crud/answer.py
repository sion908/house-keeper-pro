from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models import Answer, ImgAnswer, User
from schemas.report import AnswerBase


async def create(db: AsyncSession, answerBase: AnswerBase, user: User|int, form_id: int):
    if type(user)==User:
        user = user.id

    db_answer = Answer(
        user_id=user,
        form_id=form_id,
        start=answerBase.timeInputStart,
        end=answerBase.timeInputEnd
    )

    db.add(db_answer)
    await db.commit()

    await db.refresh(db_answer)
    return db_answer

async def create_with_stub(db: AsyncSession, form_id:int, user_id:int, form_data, img_keys:List[str]):
    """"""

    db_answer = Answer(
        form_id=form_id,
        user_id=user_id,
        start=form_data.timeInputStart,
        end=form_data.timeInputEnd
    )

    db.add(db_answer)
    await db.commit()

    await db.refresh(db_answer)

    img_answer_attrs = [{
        "key": f"{key}/{getattr(form_data,key,[])[0].filename}",
        "form_stub_id": key.split("-")[1],
        "answer_id": db_answer.id

    } for key in img_keys]
    await db.execute(
        ImgAnswer.__table__.insert(),
        img_answer_attrs
    )
    await db.commit()


    return db_answer
