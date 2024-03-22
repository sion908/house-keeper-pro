from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import SMALLINT, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column

from database.base_class import Base

from .mixins import CreatedAtMixin


class ImgAnswer(Base, CreatedAtMixin):

    @declared_attr
    def __table_args__(self):  # noqa:U100
        args = Base.__table_args__[0]
        return (
            {**args, "comment": "画像回答収集"},
        )

    id: Mapped[int] = mapped_column(SMALLINT(unsigned=True), primary_key=True)
    key_be: Mapped[str] = mapped_column(VARCHAR(128))
    key_af: Mapped[str] = mapped_column(VARCHAR(128))
    form_stub_id: Mapped[int] = mapped_column(
        TINYINT(unsigned=True),
        ForeignKey('formstub.id')
    )
    answer_id: Mapped[int] = mapped_column(
        SMALLINT(unsigned=True),
        ForeignKey('answer.id')
    )
