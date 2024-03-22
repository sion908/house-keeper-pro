from datetime import datetime
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models import User
from schemas.user import UserCreate


async def get_by_pk(
    db: AsyncSession,
    user_id: str
) -> AsyncIterator[User]:
    user = await db.scalar(
        select(User).where(User.id == user_id).limit(1)
    )

    return user


async def get_by_lineUserID(
    db: AsyncSession,
    lineUserID: str
) -> AsyncIterator[User] | None:
    user = await db.scalar(
        select(User).where(User.lineUserID == lineUserID).limit(1)
    )

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
