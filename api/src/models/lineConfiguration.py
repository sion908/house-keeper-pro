from __future__ import annotations

import uuid
from enum import IntEnum
from typing import Union

from sqlalchemy import Column, ForeignKey, Integer, String, select
from sqlalchemy.dialects.mysql import BOOLEAN, DOUBLE, SMALLINT, TINYINT, VARCHAR
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy_utils.types.password import PasswordType
from sqlalchemy_utils.types.url import URLType

from database.base_class import Base

from .mixins import TimeStampMixin


class LineConfiguration(Base, TimeStampMixin):

    @declared_attr
    def __table_args__(self):  # noqa:U100
        args = Base.__table_args__[0]
        return (
            {**args, "comment": "line構成"},
        )

    id:Mapped[int] = mapped_column(TINYINT(unsigned=True), primary_key=True)
    # 後でいい感じの運用方法を見つける
    # channel_access_token:Mapped[str] = mapped_column(VARCHAR(24), nullable=True)
    # line_access_secret:Mapped[str] = mapped_column(VARCHAR(24), nullable=True)
    liff_id_owner:Mapped[str] = mapped_column(VARCHAR(24), nullable=True)

    rally_configuration = relationship("RallyConfiguration", backref="line_configuration")
