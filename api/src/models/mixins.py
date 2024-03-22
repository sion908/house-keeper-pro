from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import DateTime


class CreatedAtMixin(object):
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_bin'}  # noqa:E501,E800

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="作成日時",
    )


class TimeStampMixin(CreatedAtMixin):
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_bin'}  # noqa:E501,E800

    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
        comment="更新日時",
    )
