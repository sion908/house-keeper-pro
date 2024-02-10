import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import User, Card, Place, Stamp
from crud.user import create as create_user
from schemas.user import UserCreate


@pytest.mark.asyncio()
class TestStampModel:

    async def test_create_stamp_def(
            self,
            async_db: AsyncSession,
            create_user: User,
            create_card: 'function',
            create_place: Place
    ) -> None:
        card = await create_card(owner = create_user)

        stamp = Stamp(
            card=card,
            place=create_place
        )
        async_db.add(stamp)

        await async_db.commit()
        await async_db.refresh(stamp)

        db_stamp = (
            await async_db.execute(select(Stamp).filter_by(id=stamp.id).options(selectinload(Stamp.card),selectinload(Stamp.place)).limit(1))
        ).scalar_one()

        assert db_stamp.id == stamp.id
        assert db_stamp.is_stamped == False
        assert db_stamp.card_id == card.id
        assert type(db_stamp.card) == Card
        assert db_stamp.place_id == create_place.id
        assert type(db_stamp.place) == Place

    async def test_create_stamp(
            self,
            async_db: AsyncSession,
            create_user: User,
            create_card: 'function',
            create_place: Place
    ) -> None:
        card = await create_card(owner = create_user)

        stamp = Stamp(
            is_stamped=True,
            card=card,
            place=create_place
        )
        async_db.add(stamp)

        await async_db.commit()
        await async_db.refresh(stamp)

        db_stamp = (
            await async_db.execute(select(Stamp).filter_by(id=stamp.id).options(selectinload(Stamp.card),selectinload(Stamp.place)).limit(1))
        ).scalar_one()

        assert db_stamp.id == stamp.id
        assert db_stamp.is_stamped == True
        assert db_stamp.card_id == card.id
        assert type(db_stamp.card) == Card
        assert db_stamp.place_id == create_place.id
        assert type(db_stamp.place) == Place

    async def test_create_stamps(
            self,
            async_db: AsyncSession,
            create_user: User,
            create_card: 'function',
            create_places: 'function'
    ) -> None:
        count = 3
        card = await create_card(owner = create_user)
        places = await create_places(count=count)

        stamp_attrs = [{
            "is_stamped":True,
            "card_id":card.id,
            "place_id":p[0].id
        } for p in places]

        await async_db.execute(
            Stamp.__table__.insert(),
            stamp_attrs
        )
        await async_db.commit()
        db_stamps = (
            await async_db.execute(select(Stamp).options(selectinload(Stamp.card),selectinload(Stamp.place)))
        ).all()

        assert len(db_stamps) == count
        for i, (db_stamp, place) in enumerate(zip(db_stamps, places)):
            # breakpoint()
            assert db_stamp[0].id == i+1
            assert db_stamp[0].is_stamped == True
            assert db_stamp[0].card_id == card.id
            assert type(db_stamp[0].card) == Card
            assert db_stamp[0].place_id == place[0].id
            assert type(db_stamp[0].place) == Place
