# import json

# import pytest
# from fastapi import status
# from httpx import AsyncClient
# from httpx_auth import Basic
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from models import User



# @pytest.mark.asyncio()
# class TestCreateUser:

#     async def test_create_user(self, async_client: AsyncClient, async_db: AsyncSession) -> None:
#         data = {
#             "username": "username",
#             "password": "password",
#             "sex": 1,
#             "age": 20
#         }
#         response = await async_client.post(
#             '/users/',
#             auth=Basic(username='user', password='pass'),
#             data=json.dumps(data)
#         )

#         assert response.status_code == status.HTTP_200_OK
#         content = json.loads(response.content)

#         user = (
#             await async_db.execute(select(User).filter_by(id=content.get("id")))
#         ).scalar_one()
#         assert data.get("username") == user.username
#         assert data.get("password") == user.password
#         assert data.get("sex") == user.sex
#         assert data.get("age") == user.age

#     async def test_create_user_with_no_data(self, async_client: AsyncClient, async_db: AsyncSession) -> None:
#         data = {}
#         response = await async_client.post(
#             '/users/',
#             auth=Basic(username='user', password='pass'),
#             data=json.dumps(data)
#         )

#         assert response.status_code == status.HTTP_200_OK
#         content = json.loads(response.content)

#         user = (
#             await async_db.execute(select(User).filter_by(id=content.get("id")))
#         ).scalar_one()
#         assert user

#     async def test_create_user_with_no_auth(self, async_client: AsyncClient, async_db: AsyncSession) -> None:
#         data = {}
#         response = await async_client.post(
#             '/users/',
#             data=json.dumps(data)
#         )

#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
