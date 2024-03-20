from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import BOOLEAN, DOUBLE, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types.url import URLType

from database.base_class import Base

from .mixins import TimeStampMixin


class Place(Base, TimeStampMixin):

    @declared_attr
    def __table_args__(self):  # noqa: U100
        args = Base.__table_args__[0]
        return (
            {**args, "comment": "スタンプの設置場所"},
        )

    id: Mapped[int] = mapped_column(TINYINT(unsigned=True), primary_key=True)
    is_active: Mapped[bool] = mapped_column(BOOLEAN(), default=False, comment="active")
    is_base: Mapped[bool] = mapped_column(BOOLEAN(), default=False, comment="base")
    name: Mapped[str] = mapped_column(VARCHAR(48), nullable=True, comment="店名")
    altname: Mapped[str] = mapped_column(VARCHAR(48), nullable=True, comment="表示名")
    access: Mapped[str] = mapped_column(VARCHAR(48), nullable=True, comment="住所")
    gpsLatitude: Mapped[int] = mapped_column(DOUBLE(9, 6), nullable=True, comment="Latitude")
    gpsLongitude: Mapped[int] = mapped_column(DOUBLE(9, 6), nullable=True, comment="Longtitude")
    stamp_img:Mapped[str] = mapped_column(URLType, nullable=True, comment="スタンプ用の画像URL")
    rally_configuration_id: Mapped[int] = mapped_column(
        TINYINT(unsigned=True),
        ForeignKey('rallyconfiguration.id'),
        nullable=True
    )

    stamps = relationship("Stamp", backref="place")
