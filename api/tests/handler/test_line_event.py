import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from linebot.models import Profile

from models import User
from line_event import line_handler
from services.line import line_bot_api
from crud.user import get_by_lineUserID
from services.line import handler

# @pytest.mark.asyncio()
# class TestReadUser:

#     async def test_line_handler(self,  async_db: AsyncSession, mocker) -> None:
#         # mocker.patch()
#         mock_some_class = mocker.patch("services.line.async_session")
#         mock_some_class.return_value.__enter__.return_value = async_db
#         mocker_get_profile = mocker.patch.object(line_bot_api, "get_profile", lambda _:Profile(display_name="display_name"))
#         mocker_reply_message = mocker.patch.object(line_bot_api, "reply_message", return_value="l")
#         lineUserID = "Uf75f473c756d4b64d9d2106034706130"
#         handler.do_each_event({
#                 "type": "follow",
#                 "webhookEventId": "01HP2N99BFDBKRJFA3FSN7HWYA",
#                 "deliveryContext": {"isRedelivery": False},
#                 "timestamp": 1707338933105,
#                 "source": {"type": "user", "userId": lineUserID},
#                 "mode": "active"
#             },
#             {"destination": "U4fd733d4734d228a16d700bf7b104458"})
#         breakpoint()
#         mocker_get_profile.assert_called_once()

#         user = get_by_lineUserID(db=async_db, lineUserID=lineUserID)

#         assert user.is_active==True
