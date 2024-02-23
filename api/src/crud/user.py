from datetime import datetime
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models import Card, Stamp, User
from schemas.user import UserCreate


async def get_by_pk(
    db: AsyncSession,
    user_id: str
) -> AsyncIterator[User]:
    user = await db.scalar(
        select(User).where(User.id == user_id).limit(1)
    ).scalar_one()

    return user


async def get_by_lineUserID(
    db: AsyncSession,
    lineUserID: str
) -> AsyncIterator[User] | None:
    user = await db.scalar(
        select(User).where(User.lineUserID == lineUserID).limit(1)
    )

    return user


async def get_with_card(
    db: AsyncSession,
    lineUserID: str = None,
    id: int = None
) -> AsyncIterator[User] | None:
    stmt = select(User)
    if lineUserID:
        stmt = stmt.where(User.lineUserID == lineUserID)
    elif id:
        stmt = stmt.where(User.id == id)
    user = await db.scalar(
        stmt
            .options(
                joinedload(User.card),
                joinedload(User.card).joinedload(Card.stamps),
                joinedload(User.card).joinedload(Card.stamps).joinedload(Stamp.place)
            )
            .limit(1)
    )
    if user and user.card and user.card.stamps:
        # Stamp を Place.id でソートし、Place の id と name のみを抽出
        user.card.stamps.sort(key=lambda stamp: stamp.place.id)

    return user


async def upsert(
    db: AsyncSession,
    values: dict,
    no_create: bool = False
) -> User | None:
    user = await get_by_lineUserID(db=db, lineUserID=values["lineUserID"])
    if user:
        for (k, v) in values.items():
            setattr(user, k, v)
        user.updated_at = datetime.now()

    else:
        if no_create:
            return None
        user = User(**values)

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user
    # なんか動かないのであきらめた パフォーマンス的にはこれをすべきなので，あとで頑張る  # noqa:E800
    # まだ一個分なのでいいでしょう  # noqa:E800
    # user = await db.execute(  # noqa:E800
    #     text(  # noqa:E800
    #         "INSERT `user` (`lineUserID`,`username`,`is_active`,`updated_at`,`created_at`) "+  # noqa:E800
    #         "VALUE (:lineUserID,:username,:is_active,NOW(),NOW()) "+  # noqa:E800
    #         "ON DUPLICATE KEY UPDATE `username`=VALUES(username),`is_active`=VALUES(is_active),`updated_at`=VALUES(updated_at);"  # noqa:E800, E501
    #     ),  # noqa:E800
    #     values  # noqa:E800
    # )  # noqa:E800
    return user


async def update_username(
    db: AsyncSession,
    user: User,
    username: str
) -> User:
    user.username = username
    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


async def create(db: AsyncSession, user: UserCreate) -> User:
    """create user by email and password"""
    db_user = User(**user.model_dump())

    db.add(db_user)
    await db.commit()

    await db.refresh(db_user)
    return db_user


async def get_or_create(db: AsyncSession, lineUserID: str) -> User:
    user = db.scalar(
        select(User).where(User.lineUserID == lineUserID).limit(1)
    ).scalar_one()

    if user:
        return user
    else:
        user = User(lineUserID=lineUserID)
        db.add(user)

        await db.commit()
        await db.refresh(user)

        return user
