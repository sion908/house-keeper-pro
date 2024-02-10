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


class RallyConfiguration(Base, TimeStampMixin):

    @declared_attr
    def __table_args__(self):  # noqa:U100
        args = Base.__table_args__[0]
        return (
            {**args, "comment": "スタンプラリーイベント構成"},
        )

    id:Mapped[int] = mapped_column(TINYINT(unsigned=True), primary_key=True)
    name:Mapped[str] = mapped_column(VARCHAR(48), nullable=True, comment="名前")
    description:Mapped[str] = mapped_column(VARCHAR(48), nullable=True, comment="説明")
    liff_id:Mapped[str] = mapped_column(VARCHAR(24), nullable=True, comment="スタンプラリー用のliffID")
    stamp_count:Mapped[int] = mapped_column(TINYINT(unsigned=True), default=9, comment="スタンプの数")
    half_complete_count:Mapped[int] = mapped_column(TINYINT(unsigned=True), default=6, comment="中間達成スタンプの数")
    is_active:Mapped[bool] = mapped_column(BOOLEAN, default=False, comment="active")

    card_img:Mapped[str] = mapped_column(URLType, nullable=True, comment="スタンプカード用の画像URL")
    stamp_img:Mapped[str] = mapped_column(URLType, nullable=True, comment="スタンプ用の画像URL")
    half_complete_img:Mapped[str] = mapped_column(URLType, nullable=True, comment="中間達成用の画像URL")
    complete_img:Mapped[str] = mapped_column(URLType, nullable=True, comment="達成用の画像URL")

    line_configuration_id:Mapped[int] = mapped_column(TINYINT(unsigned=True),
                  ForeignKey('lineconfiguration.id'),
                  nullable=True, comment="組織")

    places = relationship("Place", backref="rally_configuration")
