from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import TEXT, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base_class import Base

from .mixins import TimeStampMixin


class FormClassArea(Base, TimeStampMixin):

    @declared_attr
    def __table_args__(self):  # noqa:U100
        args = Base.__table_args__[0]
        return (
            {**args, 'comment': 'formの中項目, エリア'},
        )

    id: Mapped[int] = mapped_column(TINYINT(unsigned=True), primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(255), comment='タイトル', nullable=True)
    description: Mapped[str] = mapped_column(TEXT, comment='説明', nullable=True)
    order: Mapped[int] = mapped_column(TINYINT(unsigned=True), comment='表示順')
    form_class_floor_id: Mapped[int] = mapped_column(
        TINYINT(unsigned=True),
        ForeignKey('formclassfloor.id'),
        nullable=True
    )

    form_stubs = relationship("FormStub", backref="form_class_area")
