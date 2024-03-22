from sqlalchemy.ext.asyncio import AsyncSession

from models import ImgAnswer


async def create(
        db: AsyncSession,
        key_be: str,
        key_af: str,
        form_stub_id: int,
        answer_id: int,
    ):

    db_img_answer = ImgAnswer(
        key_be=key_be,
        key_af=key_af,
        form_stub_id=form_stub_id,
        answer_id=answer_id
    )

    db.add(db_img_answer)
    await db.commit()

    await db.refresh(db_img_answer)
    return db_img_answer
