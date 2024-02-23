from fastapi import HTTPException
from linebot.models import FlexSendMessage, LocationSendMessage, QuickReply, TextSendMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.card import create_with_stamps, update as update_card
from crud.stamp import update as update_stamp
from crud.place import get_active_places
from crud.rallyconfigration import get_one as get_one_rc
from crud.user import get_by_lineUserID, get_with_card
from database.db import session_aware
from models import AttainmentType, AwardType, Place, RallyConfiguration, User
from dependencies import line_bot_api
from setting import logger

logger.name = __name__


class CardService():
    async def async_init(self, db:AsyncSession, user:User, rally_configuration:RallyConfiguration=None) -> None:
        self.db = db
        self.rally_configuration = rally_configuration or (await get_one_rc(db=db))
        self.user = user
        card = getattr(user, "card", None)
        if card:
            self.card = card
        else:
            await self._crate_stamprally_card()

    async def _crate_stamprally_card(self):
        """create Card with Stamps"""
        places = await get_active_places(db=self.db, limit=self.rally_configuration.stamp_count, only_id=True)

        self.card = await create_with_stamps(db=self.db, user=self.user, places=places)

    def _get_stamped_card(self):
        if hasattr(self, "stamped_count"):
            return getattr(self, "stamped_count", 0)
        else:
            stamps = self.card.stamps
            _count = 0
            for stamp in stamps:
                if getattr(stamp, "is_stamped", False):
                    _count += 1
            self.stamped_count = _count
            return _count

    def _can_win_prize(self) -> tuple[list, bool]:
        setting = self.rally_configuration
        stamped = self._get_stamped_card()
        if self.card.attainment == AttainmentType.ATTAINMENT_NONE:
            if stamped == setting.stamp_count:
                if setting.half_complete_count:
                    return [AwardType.AWARD_MIDWAY, AwardType.AWARD_COMPLETE], True
                else:
                    return [AwardType.AWARD_COMPLETE], True
            elif setting.half_complete_count and stamped > setting.half_complete_count:
                return [AwardType.AWARD_MIDWAY], True
            else:
                return [], False
        elif setting.half_complete_count and self.card.attainment == AttainmentType.ATTAINMENT_MIDWAY:
            if stamped == setting.stamp_count:
                return [AwardType.AWARD_COMPLETE], True
            else:
                return [], False

        return [], False

    async def set_prize(self, awards:list) -> None:
        if AwardType.AWARD_COMPLETE in awards:
            self.card.attainment = AttainmentType.ATTAINMENT_COMPLETE
        elif AwardType.AWARD_MIDWAY in awards:
            self.card.attainment = AttainmentType.ATTAINMENT_MIDWAY
        else:
            return
        self.card = await update_card(db=self.db, card=self.card)

    async def seal_stamp(self, place_id:int) -> Place:

        sealed_stamp = None
        for stamp in self.card.stamps:
            if stamp.place.id == place_id:
                sealed_stamp = stamp
                break
        if not sealed_stamp:
            raise "Error"

        context = {
            "name": sealed_stamp.place.name
        }

        if sealed_stamp.is_stamped:
            context["already"] = True
        else:
            sealed_stamp.is_stamped = True
            await update_stamp(db=self.db, stamp=sealed_stamp)
            awards, prizable = self._can_win_prize()
            if prizable:
                context['awards'] = awards
                await self.set_prize(awards=awards)
        context["count"] = self._get_stamped_card()
        return context

    @classmethod
    @session_aware
    async def showCards(self, rep_token:str, luserid:str, db:AsyncSession=None):
        user = await get_with_card(db=db, lineUserID=luserid)

        if user and hasattr(user, "card"):
            service = self()
            await service.async_init(db=db, user=user)
            stamped_count = service._get_stamped_card()
            message = []
            (awards, had_awards) = service._can_win_prize()
            if had_awards:
                message = [TextSendMessage(f"{stamped_count}個達成!\n"+
                f"{ len(awards) }回抽選に参加できます")]
            message.append(FlexSendMessage(**service._makeCardBubble()))
        else:
            rally_configuration = await get_one_rc(db=db, is_active=True)
            if rally_configuration:
                service = self()
                await service.async_init(db=db, user=user, rally_configuration=rally_configuration)
                stamped_count = service._get_stamped_card()
                message = [
                    FlexSendMessage(**service._makeCardBubble())
                ]
            else:
                message = [TextSendMessage("開始までお待ちください")]
        line_bot_api.reply_message(rep_token, message)

    # def makeCardBubble(stamps: QuerySet, card: Card) -> dict:
    def _makeCardBubble(self) -> dict:
        card = self.card
        stamps = card.stamps
        setting = self.rally_configuration
        contents = []
        items = []
        offsetList = [["14%","23%"],["58.5%","6.5%"],["58.5%","40%"],["14%","56.5%"],["58.5%","73.5%"]]
        for i, stamp in enumerate(stamps):
            if stamp.is_stamped:
                contents.append({
                    "type": "image",
                    "url": setting.stamp_img,
                    "position": "absolute",
                    "aspectRatio": "1:1",
                    "aspectMode": "fit",
                    "size": "xs",
                    "offsetTop": offsetList[i][0],
                    "offsetStart": offsetList[i][1]
                })
            # else:
            #     place = stamp.place
            #     if place.access:
            #         items.append({
            #             "type": "action",
            #             "action": {
            #                 "type": "postback",
            #                 "label": place.altname,
            #                 "data": f"place={place.id}",
            #                 "displayText": f"{place.name}の地図を表示する",
            #             }
            #         })

        alt_text = "抽選に参加できます" if self._can_win_prize()[1] else f"のこり{setting.stamp_count-self._get_stamped_card()}つ"

        if card.attainment == AttainmentType.ATTAINMENT_COMPLETE:
            contents.append({
                "type": "image",
                "url": setting.complete_img,
                "aspectRatio": "1:1",
                "size": "80%"
            })

        elif card.attainment == AttainmentType.ATTAINMENT_MIDWAY:
            contents.append({
                "type": "image",
                "url": setting.half_complete_img,
                "aspectRatio": "1:1",
                "size": "80%"
            })

        bubble= {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "image",
                    "url": setting.card_img,
                    "size": "full",
                    "aspectMode": "cover",
                    "aspectRatio": "2:3",
                    "gravity": "top"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": contents,
                    "position": "absolute",
                    "offsetBottom": "0px",
                    "offsetStart": "0px",
                    "offsetEnd": "0px",
                    "paddingAll": "none",
                    "paddingTop": "none",
                    "height": "50%"
                }
                ],
                "paddingAll": "0px"
            },
            "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"#{card.id}",
                    "align": "end",
                    "offsetEnd": "xxl",
                    "position": "absolute",
                    "offsetBottom": "none",
                    "color": "#ffffff"
                }
            ],
            "backgroundColor":"#085A34"
            }
        }
        # if card._can_win_prize()[1]:
        #     bubble["body"]["contents"].append({
        #         "type": "box",
        #         "layout": "vertical",
        #         "contents": [],
        #         "position": "absolute",
        #         "height": "25%",
        #         "offsetTop": "0px",
        #         "offsetStart": "0px",
        #         "offsetEnd": "0px",
        #         "action": {
        #             "type": "uri",
        #             "label": "action",
        #             "uri": f"https://liff.line.me/{LIFF_ID_STAMP}/complete"
        #         },
        #     })
        flexDatas = {"alt_text": alt_text, "contents": bubble}
        if items:
            flexDatas["quick_reply"] = QuickReply(items=items)
        return flexDatas
