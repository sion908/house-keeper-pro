
from __future__ import annotations

import uuid
from enum import IntEnum
from typing import Union

from sqlalchemy import Column, ForeignKey, Integer, String, select
from sqlalchemy.dialects.mysql import BOOLEAN, SMALLINT, TINYINT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import UUIDType
from sqlalchemy_utils.types.choice import ChoiceType

from database.base_class import Base

from .mixins import TimeStampMixin


class Stamp(Base, TimeStampMixin):

    @declared_attr
    def __table_args__(self):  # noqa:U100
        args = Base.__table_args__[0]
        return (
            {**args, "comment": "カード"},
        )

    id:Mapped[int] = mapped_column(SMALLINT(unsigned=True), primary_key=True)
    is_stamped:Mapped[bool] = mapped_column(BOOLEAN, default=False, comment="スタンプが押されているか")
    card_id:Mapped[int] = mapped_column(SMALLINT(unsigned=True),
                  ForeignKey('card.id'),
                  comment="カード")
    place_id:Mapped[int] = mapped_column(TINYINT(unsigned=True),
                  ForeignKey('place.id'),
                  comment="場所")
