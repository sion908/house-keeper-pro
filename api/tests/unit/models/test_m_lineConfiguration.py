
import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import LineConfiguration

@pytest.mark.asyncio()
class TestLineConfigurations:

    async def test_create_lineConfiguration_with_no_data(self, async_db: AsyncSession) -> None:

        lc = LineConfiguration()
        async_db.add(lc)

        await async_db.commit()
        await async_db.refresh(lc)

        db_lc = (
            await async_db.execute(select(LineConfiguration).filter_by(id=lc.id))
        ).scalar_one()

        assert db_lc.id == lc.id
        # assert db_lc.channel_access_token == None
        # assert db_lc.line_access_secret == None
        assert db_lc.liff_id_owner == None

    async def test_create_rallyConfiguration(
            self,
            async_db: AsyncSession
        ) -> None:
        lc_data = {
            # "channel_access_token": "channel_access_token",
            # "line_access_secret": "line_access_secret",
            "liff_id_owner": "liff_id_owner"
        }
        lc = LineConfiguration(**lc_data)
        async_db.add(lc)

        await async_db.commit()
        await async_db.refresh(lc)

        db_lc = (
            await async_db.execute(select(LineConfiguration).filter_by(id=lc.id))
        ).scalar_one()

        assert db_lc.id == lc.id
        # assert db_lc.channel_access_token == lc.channel_access_token
        # assert db_lc.line_access_secret == lc.line_access_secret
        assert db_lc.liff_id_owner == lc.liff_id_owner
