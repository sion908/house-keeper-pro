from __future__ import annotations

from enum import IntEnum

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import SMALLINT, TINYINT
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types.choice import ChoiceType

from database.base_class import Base

from .mixins import TimeStampMixin


class AwardType(IntEnum):
    AWARD_NONE = 0
    AWARD_MIDWAY = 1
    AWARD_COMPLETE = 2


class AttainmentType(IntEnum):
    ATTAINMENT_NONE = 0
    ATTAINMENT_MIDWAY = 1
    ATTAINMENT_COMPLETE = 2


class Card(Base, TimeStampMixin):

    @declared_attr
    def __table_args__(self):  # noqa:U100
        args = Base.__table_args__[0]
        return (
            {**args, "comment": "カード"},
        )

    id: Mapped[int] = mapped_column(SMALLINT(unsigned=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(SMALLINT(unsigned=True),
        ForeignKey('user.id'),
        comment="所有者")
    attainment: Mapped[int] = mapped_column(
        ChoiceType(AttainmentType, impl=TINYINT(unsigned=True)),
        default=AttainmentType.ATTAINMENT_NONE,
        comment="達成状況")

    stamps = relationship("Stamp", backref="card")
