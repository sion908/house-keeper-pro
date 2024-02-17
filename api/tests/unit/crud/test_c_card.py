import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
import freezegun
from datetime import (datetime, timedelta)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Card, Stamp, Place
from crud.card import get_by_id, create_with_stamps


@pytest.mark.asyncio()
class TestGetById:
    async def test_main(
            self,
            async_db: AsyncSession,
            create_user: User,
            create_places: 'function',
            create_card_with_another: 'function',
        ) -> None:

        stamp_count = 5
        places = await create_places(count=stamp_count)
        init_card = await create_card_with_another(owner=create_user,stamp_count=stamp_count,places=places)

        card = await get_by_id(db=async_db, card=init_card)

        assert type(card) == Card
        assert len(card.stamps) == stamp_count
        assert type(card.stamps[0]) == Stamp
        assert type(card.stamps[0].place) == Place
        assert type(card.stamps[0].place.name) == str

@pytest.mark.asyncio()
class TestCreateWithStamps:

    async def test_main(
            self,
            async_db: AsyncSession,
            create_user: User,
            create_places: 'function'
        ) -> None:

        stamp_count = 5
        places = await create_places(count=stamp_count)

        card = await create_with_stamps(db=async_db, user=create_user, places=places)

        assert type(card) == Card
        assert len(card.stamps) == stamp_count
        assert type(card.stamps[0]) == Stamp
        assert type(card.stamps[0].place) == Place
        assert type(card.stamps[0].place.name) == str
