from __future__ import annotations

from enum import IntEnum

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import DATETIME, SMALLINT, TINYINT
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils.types.choice import ChoiceType

from database.base_class import Base

from .mixins import CreatedAtMixin


class Answer(Base, CreatedAtMixin):

    @declared_attr
    def __table_args__(self):  # noqa:U100
        args = Base.__table_args__[0]
        return (
            {**args, "comment": "回答収集のマスタ"},
        )

    id: Mapped[int] = mapped_column(SMALLINT(unsigned=True), primary_key=True)
    start: Mapped[int] = mapped_column(DATETIME(timezone=True))
    end: Mapped[int] = mapped_column(DATETIME(timezone=True))

    user_id: Mapped[int] = mapped_column(
        SMALLINT(unsigned=True),
        ForeignKey('user.id')
    )
    form_id: Mapped[int] = mapped_column(
        TINYINT(unsigned=True),
        ForeignKey('form.id')
    )
