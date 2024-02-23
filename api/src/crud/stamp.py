from typing import AsyncIterator
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from models import Stamp


async def update(
    db: AsyncSession,
    stamp: Stamp
) -> AsyncIterator[Stamp]:
    # stamp.place=None
    # stamp.place_id=None
    stamp.updated_at = datetime.now()
    db.add(stamp)

    await db.commit()
    await db.refresh(stamp)

    return stamp
