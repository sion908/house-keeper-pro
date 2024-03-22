from __future__ import annotations

from sqlalchemy.dialects.mysql import TEXT, TINYINT
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base_class import Base

from .mixins import TimeStampMixin


class Form(Base, TimeStampMixin):

    @declared_attr
    def __table_args__(self):  # noqa:U100
        args = Base.__table_args__[0]
        return (
            {**args, "comment": "フォーム"},
        )

    id: Mapped[int] = mapped_column(TINYINT(unsigned=True), primary_key=True)
    title: Mapped[str] = mapped_column(TEXT,comment="タイトル")
    description: Mapped[str] = mapped_column(TEXT,comment="説明")

    form_stubs = relationship("FormStub", backref="form")
