from __future__ import annotations

import uuid
from enum import IntEnum
from typing import Union

from sqlalchemy import select
from sqlalchemy.dialects.mysql import BOOLEAN, SMALLINT, VARCHAR
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base_class import Base

from .mixins import TimeStampMixin


class User(Base, TimeStampMixin):

    @declared_attr
    def __table_args__(self):  # noqa:U100
        args = Base.__table_args__[0]
        return (
            {**args, "comment": "ユーザー"},
        )

    id: Mapped[int] = mapped_column(SMALLINT(unsigned=True), primary_key=True)
    lineUserID: Mapped[str] = mapped_column(VARCHAR(40), unique=True)
    username: Mapped[str] = mapped_column(VARCHAR(48), nullable=True)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True, nullable=False)
    card = relationship("Card", backref="owner", uselist=False)
    admin = relationship("Admin", backref="user")

    def convert_output(self):
        self.id = str(self.id)
        self.password = "*****"
        return self

    @classmethod
    async def read_by_id(
        cls, db: AsyncSession, user_id: int
    ) -> 'User' | None:
        stmt = select(cls).where(cls.id == user_id)
        return await db.scalar(stmt.order_by(cls.id))
