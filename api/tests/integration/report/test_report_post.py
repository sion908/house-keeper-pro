import pytest
import json
from pytest_mock import MockerFixture
from fastapi import status
from httpx import AsyncClient

from models import User

@pytest.mark.asyncio()
class TestSealStampDisp:

    async def test_main(self, async_client: AsyncClient, mocker: MockerFixture,
        create_user: User,
        create_form_with_another: 'function',) -> None:
        form_stub_attrs = [{
            "description": f"説明-{i}",
            "order": i+1,
            "type": i%2
        } for i in range(3)]
        init_form = await create_form_with_another(form_stub_attrs)

        data = {
            "timeInputStart": "2023/01/02T10:10",
            "timeInputEnd": "2023/01/02T10:11",
            "lineToken":"lineToken"
        }
        response = await async_client.post(
            f'/report/1',
            data=json.dumps(data)
        )
        breakpoint()

        assert response.status_code == status.HTTP_200_OK
        # assert (
        #     await async_db.execute(select(User).filter_by(id=user_id))
        # ).scalar_one().id == user_id

    # async def test_get_user_with_no_auth(self, async_client: AsyncClient, async_db: AsyncSession,
    #                         async_user_orm: User) -> None:

    #     user_id = async_user_orm.id
    #     response = await async_client.get(
    #         f'/users/{user_id}'
    #     )

    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED
