# import pytest
# from fastapi import status
# from httpx import AsyncClient
# from httpx_auth import Basic
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from models import User

# @pytest.mark.asyncio()
# class TestReadUser:

#     async def test_get_user(self, async_client: AsyncClient, async_db: AsyncSession,
#                             async_user_orm: User) -> None:
#         user_id = async_user_orm.id
#         response = await async_client.get(
#             f'/users/{user_id}',
#             auth=Basic(username='user', password='pass')
#         )

#         assert response.status_code == status.HTTP_200_OK
#         assert (
#             await async_db.execute(select(User).filter_by(id=user_id))
#         ).scalar_one().id == user_id

#     async def test_get_user_with_no_auth(self, async_client: AsyncClient, async_db: AsyncSession,
#                             async_user_orm: User) -> None:

#         user_id = async_user_orm.id
#         response = await async_client.get(
#             f'/users/{user_id}'
#         )

#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
