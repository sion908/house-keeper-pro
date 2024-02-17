
import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import RallyConfiguration, LineConfiguration

@pytest.mark.asyncio()
class TestRallyConfigurations:

    async def test_create_rallyConfiguration_with_no_data(self, async_db: AsyncSession) -> None:

        rc = RallyConfiguration()
        async_db.add(rc)

        await async_db.commit()
        await async_db.refresh(rc)

        db_rc = (
            await async_db.execute(select(RallyConfiguration).filter_by(id=rc.id))
        ).scalar_one()

        assert db_rc.id == rc.id
        assert db_rc.name == None
        assert db_rc.description == None
        assert db_rc.stamp_count == 9
        assert db_rc.half_complete_count == None
        assert db_rc.is_active == False
        assert db_rc.card_img == None
        assert db_rc.stamp_img == None
        assert db_rc.half_complete_img == None
        assert db_rc.complete_img == None

    async def test_create_rallyConfiguration(
            self,
            async_db: AsyncSession,
            create_line_configuration: LineConfiguration
        ) -> None:
        rc_data = {
            "name": "name",
            "description": "rc description",
            "stamp_count": 6,
            "half_complete_count": 2,
            "is_active": True,
            "card_img": "https: //card_img",
            "stamp_img": "https: //stamp_img",
            "half_complete_img": "https: //half_complete_img",
            "complete_img": "https: //complete_img",
            "line_configuration": create_line_configuration
        }
        rc = RallyConfiguration(**rc_data)
        async_db.add(rc)

        await async_db.commit()
        await async_db.refresh(rc)

        db_rc = (
            await async_db.execute(select(RallyConfiguration).filter_by(id=rc.id))
        ).scalar_one()

        assert db_rc.id == rc.id
        assert type(db_rc.id) == int
        assert db_rc.name == rc_data["name"]
        assert type(db_rc.name) == str
        assert db_rc.description == rc_data["description"]
        assert type(db_rc.description) == str
        assert db_rc.stamp_count == rc_data["stamp_count"]
        assert type(db_rc.stamp_count) == int
        assert db_rc.half_complete_count == rc_data["half_complete_count"]
        assert type(db_rc.half_complete_count) == int
        assert db_rc.is_active == rc_data["is_active"]
        assert type(db_rc.is_active) == bool
        assert db_rc.card_img == rc_data["card_img"]
        assert type(db_rc.card_img) == str
        assert db_rc.stamp_img == rc_data["stamp_img"]
        assert type(db_rc.stamp_img) == str
        assert db_rc.half_complete_img == rc_data["half_complete_img"]
        assert type(db_rc.half_complete_img) == str
        assert db_rc.complete_img == rc_data["complete_img"]
        assert type(db_rc.complete_img) == str
        assert db_rc.line_configuration == create_line_configuration
        assert type(db_rc.line_configuration) == LineConfiguration
