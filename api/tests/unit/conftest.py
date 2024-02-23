import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import User, Card, Place, RallyConfiguration, LineConfiguration, Stamp

@pytest.fixture()
async def create_line_configuration(async_db: AsyncSession):
    lc = LineConfiguration()
    async_db.add(lc)

    await async_db.commit()
    await async_db.refresh(lc)
    yield lc

@pytest.fixture()
async def create_user(async_db: AsyncSession):
    user = User(lineUserID="userID", username="initName")
    async_db.add(user)

    await async_db.commit()
    await async_db.refresh(user)
    yield user

@pytest.fixture()
async def create_card(async_db: AsyncSession):
    async def _create_card(owner: User):
        card = Card(owner=owner)
        async_db.add(card)

        await async_db.commit()
        await async_db.refresh(card)
        return card

    yield _create_card

@pytest.fixture()
async def create_rally_configuration(async_db: AsyncSession):
    rally_configuration = RallyConfiguration(is_active=True)
    async_db.add(rally_configuration)

    await async_db.commit()
    await async_db.refresh(rally_configuration)

    yield rally_configuration

@pytest.fixture()
async def create_card(async_db: AsyncSession):
    async def _create_card(owner: User):
        card = Card(owner=owner)
        async_db.add(card)

        await async_db.commit()
        await async_db.refresh(card)
        return card

    yield _create_card

@pytest.fixture()
async def create_place(async_db: AsyncSession):
    place_attr = {
        "is_active"    : True,
        "is_base"      : True,
        "name"         : "名前",
        "altname"      : "表示名",
        "access"       : "住所",
        "gpsLatitude"  : "32.754748896659805",
        "gpsLongitude" : "129.88197322470594",
    }
    place = Place(**place_attr)
    async_db.add(place)

    await async_db.commit()
    await async_db.refresh(place)

    yield place

@pytest.fixture()
async def create_places(async_db: AsyncSession):
    async def _create_places(count=2):
        place_attrs = [{
            "is_active"    : True,
            "is_base"      : True,
            "name"         : f"names_{i}",
            "altname"      : f"表示名_{i}",
            "access"       : "住所",
            "gpsLatitude"  : 32.754748896659805 + i,
            "gpsLongitude" : 129.88197322470594 + i,
        } for i in range(count)]

        await async_db.execute(
            Place.__table__.insert(),
            place_attrs
        )
        await async_db.commit()
        db_places = (
            await async_db.execute(select(Place).filter(Place.name.startswith("names_")))
        ).scalars().all()

        return db_places

    yield _create_places

@pytest.fixture()
async def create_card_with_another(async_db: AsyncSession):
    async def _create_card_with_another(
        owner: User,
        stamp_count: int=5,
        places: list[Place]=None
    ):
        if not places:
            places = await create_places(count=stamp_count)

        card = Card(owner=owner)

        async_db.add(card)

        await async_db.commit()
        await async_db.refresh(card)
        stamp_attrs = [{
            "card_id":card.id,
            "place_id":p.id
        } for p in places]

        await async_db.execute(
            Stamp.__table__.insert(),
            stamp_attrs
        )
        await async_db.commit()
        return card

    yield _create_card_with_another
