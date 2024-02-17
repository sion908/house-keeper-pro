import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
import freezegun
from datetime import (datetime, timedelta)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Card, Stamp, Place
from crud.place import get_active_places

@pytest.mark.asyncio()
class TestGetActivePlaces:

    async def test_main(self, async_db: AsyncSession, create_places: 'function') -> None:
        place_count=5
        init_places = await create_places(count=place_count)
        places = await get_active_places(db=async_db)

        assert len(places) == place_count
        assert type(places[0]) == Place
        assert type(places[0].id) == int

    async def test_with_limit(self, async_db: AsyncSession, create_places: 'function') -> None:
        place_count=5
        limit=5
        init_places = await create_places(count=place_count)
        places = await get_active_places(db=async_db, limit=5)

        assert len(places) == limit
        assert type(places[0]) == Place
        assert type(places[0].id) == int

    async def test_with_only_id(self, async_db: AsyncSession, create_places: 'function') -> None:
        place_count=5
        limit=5
        init_places = await create_places(count=place_count)
        places = await get_active_places(db=async_db, limit=5, only_id=True)

        assert len(places) == limit
        assert type(places[0]) == Place
        assert type(places[0].id) == int

    # async def test_with_no_data(self, async_db: AsyncSession) -> None:
    #     user = await get_by_lineUserID(db=async_db, lineUserID="lineID")
    #     assert user == None
