import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_URL = os.environ.get(
    "DB_URL",
    "mysql+aiomysql://as:os@stamp_rally_db:3306/local_db?charset=utf8mb4"
)

async_engine = create_async_engine(DB_URL, echo=True)
async_session = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)


class Base(DeclarativeBase):

    def __repr__(self):
        """Dump all columns and value automagically.

        This code is copied a lot from followings.
        See also:
            - https://gist.github.com/exhuma/5935162#file-representable_base-py
            - http://stackoverflow.com/a/15929677
        modelのデバッグ用,多分うざい
        """
        #: Columns.
        columns = ', '.join([
            '{0}={1}å'.format(k, repr(self.__dict__[k]))
            for k in self.__dict__.keys() if k[0] != '_'
        ])

        return '<{0}({1})>'.format(
            self.__class__.__name_å_, columns
        )


async def get_db():
    """
    fastapiのルーティングで使う用のdb処理
    """
    async with async_session() as session:
        yield session

def session_aware(func):
    """
    fastapiのルーティング外で行われる処理で使うラッパー
    """
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            # デコレータ内で利用するために関数に値を渡す
            kwargs["db"] = session
            result = await func(*args, **kwargs)
        return result
    return wrapper
