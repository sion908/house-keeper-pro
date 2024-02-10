from __future__ import annotations

import uuid
from enum import IntEnum
from typing import Union

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.dialects.mysql import BOOLEAN, SMALLINT, TINYINT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import UUIDType
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy_utils.types.password import PasswordType

from database.base_class import Base

from .mixins import TimeStampMixin


class Admin(Base, TimeStampMixin):

    @declared_attr
    def __table_args__(self):  # noqa:U100
        args = Base.__table_args__[0]
        return (
            {**args, "comment": "管理者"},
        )

    id:Mapped[int] = mapped_column(TINYINT(unsigned=True), primary_key=True)
    username:Mapped[str] = mapped_column(
        String(255, collation="utf8mb4_bin"),
        unique=True,
        nullable=True
    )
    password:Mapped[str] = mapped_column(PasswordType(
        schemes=[
            'pbkdf2_sha512',
            'md5_crypt'
        ],
        deprecated=['md5_crypt']
        ),
        nullable=True)
    user_id:Mapped[int] = mapped_column(SMALLINT(unsigned=True),
                  ForeignKey('user.id'),
                  nullable=True, comment="ユーザー")
