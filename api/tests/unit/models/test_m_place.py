import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from decimal import Decimal

from models import User, Card, Place, RallyConfiguration
from crud.user import create as create_user
from schemas.user import UserCreate

@pytest.mark.asyncio()
class TestPlaceModel:

    async def test_create_place_with_no_attr(self, async_db: AsyncSession) -> None:
        # breakpoint()
        place = Place()
        async_db.add(place)

        await async_db.commit()
        await async_db.refresh(place)

        db_place = (
            await async_db.execute(select(Place).filter_by(id=place.id).limit(1) )
        ).scalar_one()

        assert db_place.id == place.id
        assert db_place.is_active == False
        assert db_place.is_base == False
        assert db_place.name == None
        assert db_place.altname == None
        assert db_place.access == None
        assert db_place.gpsLatitude == None
        assert db_place.gpsLongitude == None
        assert db_place.rally_configuration_id == None

    async def test_create_place(self, async_db: AsyncSession, create_rally_configuration: RallyConfiguration) -> None:

        place_attr = {
            "is_active"            : True,
            "is_base"              : True,
            "name"                 : "名前",
            "altname"              : "表示名",
            "access"               : "住所",
            "rally_configuration"  : create_rally_configuration,
            "gpsLatitude"          : "32.754748896659805",
            "gpsLongitude"         : "129.88197322470594",
        }
        place = Place(**place_attr)
        async_db.add(place)

        await async_db.commit()
        await async_db.refresh(place)

        db_place = (
            await async_db.execute(select(Place).filter_by(id=place.id).limit(1) )
        ).scalar_one()

        assert db_place.id == place.id
        assert db_place.is_active == place_attr["is_active"]
        assert db_place.is_base == place_attr["is_base"]
        assert db_place.name == place_attr["name"]
        assert db_place.altname == place_attr["altname"]
        assert db_place.access == place_attr["access"]
        assert db_place.gpsLatitude == Decimal(place_attr["gpsLatitude"]).quantize(Decimal('.000001'))
        assert db_place.gpsLongitude == Decimal(place_attr["gpsLongitude"]).quantize(Decimal('.000001'))
        assert db_place.rally_configuration_id == create_rally_configuration.id

    async def test_create_places(self, async_db: AsyncSession, create_rally_configuration: RallyConfiguration) -> None:

        place_attrs = [{
            "is_active"    : True,
            "is_base"      : True,
            "name"         : f"names_{i}",
            "altname"      : f"表示名_{i}",
            "access"       : "住所",
            "rally_configuration"  : create_rally_configuration,
            "gpsLatitude"  : 32.754748896659805 + i,
            "gpsLongitude" : 129.88197322470594 + i,
        } for i in range(3)]

        await async_db.execute(
            Place.__table__.insert(),
            place_attrs
        )
        await async_db.commit()

        db_places = (
            await async_db.execute(select(Place).filter(Place.name.startswith("names_")))
        ).all()

        assert len(db_places) == len(place_attrs)
        assert db_places[0][0].name == "names_0"
