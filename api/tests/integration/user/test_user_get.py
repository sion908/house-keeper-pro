import pytest
from pytest_mock import MockerFixture
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, RallyConfiguration

@pytest.mark.asyncio()
class TestSealStampDisp:

    async def test_main(self, async_client: AsyncClient, mocker: MockerFixture) -> None:

        mock_rep_mess = mocker.patch("routers.seal.csrf_protect.generate_csrf_tokens", return_value="")
        mock_rep_mess = mocker.patch("routers.seal.set_csrf_cookie", return_value="")
        mock_rep_mess = mocker.patch("routers.seal.get_one", return_value=RallyConfiguration(liff_id="liff_id"))
        mock_rep_mess = mocker.patch("routers.seal.csrf_protect.get_place_by_id", return_value="")
        from dependencies import CsrfProtect
        response = await async_client.get(
            f'/seal/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert (
            await async_db.execute(select(User).filter_by(id=user_id))
        ).scalar_one().id == user_id

    # async def test_get_user_with_no_auth(self, async_client: AsyncClient, async_db: AsyncSession,
    #                         async_user_orm: User) -> None:

    #     user_id = async_user_orm.id
    #     response = await async_client.get(
    #         f'/users/{user_id}'
    #     )

    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED
