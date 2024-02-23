from datetime import datetime
from typing import AsyncIterator

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import current_timestamp

from models import RallyConfiguration


async def get_one(
    db: AsyncSession,
    is_active:bool = None
) -> AsyncIterator[RallyConfiguration]:
    stmt = select(RallyConfiguration)
    if not is_active == None:
        stmt = stmt.where(RallyConfiguration.is_active==is_active)
    rally_configuration = await db.scalar(
        stmt.limit(1)
    )

    return rally_configuration
