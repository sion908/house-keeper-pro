from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from models import Place


async def get_by_id(db: AsyncSession, place_id: int) -> AsyncIterator[Place]| None:
    place = await db.scalar(
        select(Place)
            .where(Place.id == place_id)
            .limit(1)
    )
    return place


async def get_active_places(
    db: AsyncSession,
    limit: int = None,
    only_id: bool = False
) -> AsyncIterator[list[Place]]:

    stmt = select(Place).filter(Place.is_active==True)
    if only_id:
        stmt = stmt.options(load_only(Place.id))
    if limit:
        stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    places = result.scalars().all()

    return places
