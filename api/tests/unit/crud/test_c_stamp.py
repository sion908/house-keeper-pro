import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
import freezegun
import copy
from datetime import (datetime, timedelta)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Card, Stamp, RallyConfiguration
from crud.user import get_by_lineUserID, upsert, get_with_card
from crud.stamp import update



@pytest.mark.asyncio()
class TestUpdate:

    async def test_main(self, async_db: AsyncSession, create_user: User, create_rally_configuration:RallyConfiguration, create_place, create_card_with_another) -> None:
        await create_card_with_another(owner=create_user, stamp_count=1, places=[create_place])
        stamp = (
            await async_db.execute(select(Stamp).limit(1))
        ).scalar_one()

        stamp_be = copy.deepcopy(stamp)

        stamp.is_stamped=True
        with freezegun.freeze_time('2015-10-21'):
            stamp = await update(db=async_db, stamp=stamp)
            db_stamp = (
                await async_db.execute(select(Stamp).limit(1))
            ).scalar_one()

        assert stamp_be.is_stamped != db_stamp.is_stamped
        assert stamp_be.id == db_stamp.id

    async def test_5_in_3(self, async_db: AsyncSession, create_user: User, create_rally_configuration:RallyConfiguration, create_places, create_card_with_another) -> None:
        stamp_id=3
        places = await create_places(count=5)
        await create_card_with_another(owner=create_user, stamp_count=5, places=places)

        stamp = (
            await async_db.execute(select(Stamp).where(Stamp.id==stamp_id).limit(1))
        ).scalar_one()
        stamp_be = copy.deepcopy(stamp)

        stamp.is_stamped=True
        with freezegun.freeze_time('2015-10-21'):
            stamp = await update(db=async_db, stamp=stamp)
        db_stamp = (
            await async_db.execute(select(Stamp).where(Stamp.id==stamp_id).limit(1))
        ).scalar_one()


        assert stamp_be.is_stamped != db_stamp.is_stamped
        assert stamp_be.id == db_stamp.id
