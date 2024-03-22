from __future__ import annotations

from enum import IntEnum

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import SMALLINT, TEXT, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, reconstructor
from sqlalchemy_utils.types.choice import ChoiceType

from database.base_class import Base

from .mixins import TimeStampMixin


class StubType(IntEnum):
    IMG = 0
    CHECKBOX = 1

class FormStub(Base, TimeStampMixin):

    @declared_attr
    def __table_args__(self):  # noqa:U100
        args = Base.__table_args__[0]
        return (
            {**args, 'comment': '画像用のフォームの一部'},
        )

    id: Mapped[int] = mapped_column(TINYINT(unsigned=True), primary_key=True)
    description: Mapped[str] = mapped_column(TEXT, comment='説明', nullable=True)
    title: Mapped[str] = mapped_column(VARCHAR(255), comment='タイトル', nullable=True)
    order: Mapped[int] = mapped_column(SMALLINT(unsigned=True), comment='formの順番')
    type: Mapped[int] = mapped_column(
        ChoiceType(StubType, impl=TINYINT(unsigned=True)),
        default=StubType.IMG,
        comment='formの種類'
    )
    form_id: Mapped[int] = mapped_column(
        TINYINT(unsigned=True),
        ForeignKey('form.id'),
        nullable=True
    )

    @reconstructor
    def init_on_load(self):
        templates = {
            StubType.IMG: "form_dom/img.html",
            StubType.CHECKBOX: "form_dom/checkbox.html"
        }
        self.template = templates[self.type]
        name = {
            StubType.IMG: "img",
            StubType.CHECKBOX: "check"
        }
        self.name = f"{name[self.type]}-{self.order}-{self.id}"
