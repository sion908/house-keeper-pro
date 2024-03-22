import json

from linebot.models import (
    FollowEvent,
    MessageEvent,
    PostbackEvent,
    TextMessage,
    TextSendMessage,
    UnfollowEvent,
)
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user import upsert as upsert_user
from database.db import session_aware
from dependencies import line_bot_api
from dependencies.line import handler
from setting import logger

logger.name = __name__

# addメソッドの引数にはイベントのモデルを入れる
# 関数名は自由

# メッセージイベントの場合の処理
# かつテキストメッセージの場合
# @handler.add(MessageEvent, message=TextMessage)
# async def handle_text_message(event):
#     if event.message.text == "こんにちは":
#         pass
        # await CardService.showCards(rep_token=event.reply_token, luserid=event.source.user_id)

# メッセージイベントの場合の処理
# かつスタンプメッセージの場合
# @handler.add(MessageEvent, message=StickerMessage)
# def handle_text_message(event):
#     delStamp(event.reply_token, event.source.user_id)
    # line_introS.showTickets(event.reply_token)


# ポストバックイベントの場合の処理
# @handler.add(PostbackEvent)
# async def handle_postback_message(event):

#     pb_mess = event.postback.data
#     if pb_mess == 'StartQA':
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text="準備中です")
#         )


@handler.add(FollowEvent)
@session_aware
async def handle_follow(event, db:AsyncSession=None):
    upsert_values = {
        "lineUserID": event.source.user_id,
        "is_active": True
    }
    try:
        profile = line_bot_api.get_profile(event.source.user_id)
        if profile:
            upsert_values["username"] = profile.display_name
    except Exception as e:
        logger.error(e)
    await upsert_user(db=db, values=upsert_values)
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(
                text="フォローありがとうございます"
            ),
        ]
    )


@handler.add(UnfollowEvent)
@session_aware
async def handle_unfollow(event, db:AsyncSession=None):
    await upsert_user(
        db=db,
        values={
            "lineUserID": event.source.user_id,
            "is_active": False
        },
        no_create=True)
