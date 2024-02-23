from sqlalchemy.ext.asyncio import AsyncSession
import pytest
import random
from pytest_mock import MockerFixture

from services.card import CardService
from crud.user import get_with_card
from models import RallyConfiguration, User

@pytest.mark.asyncio()
class TestCardService():

    async def test_init_card_service(self):
        card_service = CardService()

        assert type(card_service) == CardService

    async def test_init_async_card_service(
            self,
            async_db: AsyncSession,
            create_rally_configuration: RallyConfiguration,
            create_user: User,
            create_places: 'function'
        ):
        places = await create_places(count=10)
        card_service = CardService()
        user = await get_with_card(db=async_db, lineUserID=create_user.lineUserID)

        await card_service.async_init(db=async_db,user=create_user,rally_configuration=create_rally_configuration)

@pytest.mark.asyncio()
class TestShowCards():

    async def test_main(
            self,
            mocker: MockerFixture,
            create_rally_configuration: RallyConfiguration,
            create_user: User,
            create_places: 'function'
        ):
        await create_places(count=5)
        rep_token = "rep_token"

        mock_rep_mess = mocker.patch("dependencies.line_bot_api.reply_message", return_value="")
        await CardService.showCards(rep_token=rep_token, luserid=create_user.lineUserID)
        assert mock_rep_mess.call_count == 1
        assert mock_rep_mess.call_args.args[0] == rep_token
        assert len(mock_rep_mess.call_args.args[1]) == 1

    # async def test_init_async_card_service(
    #     ):
    #     places = await create_places(count=10)
    #     card_service = CardService()
    #     user = await get_with_card(db=async_db, lineUserID=create_user.lineUserID)
    #     await card_service.async_init(db=async_db,user=create_user,rally_configuration=create_rally_configuration)

@pytest.mark.asyncio()
class TestSealStamp():

    async def test_main(
            self,
            async_db: AsyncSession,
            create_rally_configuration: RallyConfiguration,
            create_user: User,
            create_places: 'function'
        ):
        place_count=5
        places = await create_places(count=place_count)
        card_service = CardService()
        user = await get_with_card(db=async_db, lineUserID=create_user.lineUserID)

        await card_service.async_init(db=async_db,user=create_user,rally_configuration=create_rally_configuration)
        place_id = random.randint(1,place_count)
        await card_service.seal_stamp(place_id=place_id)

        user = await get_with_card(db=async_db, id=create_user.id)

        for stamp in user.card.stamps:
            if stamp.place.id == place_id:
                assert stamp.is_stamped
            else:
                assert not stamp.is_stamped


    # async def test_init_async_card_service(
    #     ):
    #     places = await create_places(count=10)
    #     card_service = CardService()
    #     user = await get_with_card(db=async_db, lineUserID=create_user.lineUserID)
    #     await card_service.async_init(db=async_db,user=create_user,rally_configuration=create_rally_configuration)
