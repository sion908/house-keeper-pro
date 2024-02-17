from fastapi import HTTPException
from linebot.models import FlexSendMessage, LocationSendMessage, QuickReply, TextSendMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.card import create_with_stamps
from crud.place import get_active_places
from crud.rallyconfigration import get_one as get_one_rc
from crud.user import get_by_lineUserID, get_by_lineUserID_with_card
from database.db import session_aware
from models import AttainmentType, AwardType, Card, RallyConfiguration, User
from services.line import line_bot_api


class PlaceService():
    def __init__(self, db:AsyncSession, user:User=None, card:Card=None, rally_configuration:RallyConfiguration=None) -> None:

        self.rally_configuration = rally_configuration if rally_configuration else get_one_rc(db=db)
        if user and user.card:
            self.card = card if card else user.card
        if not card:
            self._create_stamprally_card()
        self.db = db

    def _crate_stamprally_card(self):
        # create_Stamp_Card(self):
        """create Card with Stamps"""
        places = get_active_places(self.rally_configuration.stamp_count)

        self.card = create_with_stamps(db=self.db, user=self.user, places=places)
