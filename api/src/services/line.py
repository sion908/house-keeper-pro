# flake8: noqa: E800,F401
import boto3
# from django.shortcuts import get_object_or_404
import requests
# from django.http import Http404
from fastapi import Depends, HTTPException
# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    FlexSendMessage,
    FollowEvent,
    JoinEvent,
    MessageEvent,
    PostbackEvent,
    StickerMessage,
    TextMessage,
    TextSendMessage,
    UnfollowEvent,
)
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user import create as create_user
from crud.user import get_by_lineUserID, update_username
from crud.user import upsert as upsert_user
from database.db import async_session, get_db, session_aware
from schemas.user import UserCreate
from setting import CHANNEL_ACCESS_TOKEN, LINE_ACCESS_SECRET, logging

from .lineHandler import MyWebhookHandler

line_bot_api = LineBotApi(channel_access_token=CHANNEL_ACCESS_TOKEN)
handler = MyWebhookHandler(channel_secret=LINE_ACCESS_SECRET)


def get_lineuser_by_token(token, create=False):
    """
        tokenによって,
        User    -> <class 'apps.core.models.User'>
        createflagで作るかどうかの確認
        created -> すでにあった場合にTrue
        を得る.
        tokenからユーザーIDが取れる場合はとにかくUserを 作る
    """
    # getでエラーようにtryしてるけどエラーはいたときは何をすればいいんだ？
    if not token:
        print("get_lineuser_by_token:not token")
        raise HTTPException(status_code=404, detail="accestoken not found.")
        # raise Http404("時間が経ちすぎました．もう一度お試しください")
    try:
        res = requests.get(f"https://api.line.me/oauth2/v2.1/verify?access_token={token}")
        res.raise_for_status()  # ステータスコード見て200番台以外だと例外発生するらしい
    except requests.exceptions.RequestException as e:
        print("get_lineuser_by_token:invalid token", e.response.text)
        raise HTTPException(status_code=404, detail="invalid accesstoken")

    # valid_token_url = 'https://api.line.me/oauth2/v2.1/verify?access_token=' + token
    # is_valid_token = requests.get(valid_token_url)

    # if not is_valid_token.status_code == 200:
    #     return

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    try:
        req = requests.get('https://api.line.me/v2/profile', headers=headers)
        req.raise_for_status()  # ステータスコード見て200番台以外だと例外発生するらしい
    except requests.exceptions.RequestException:
        try:
            req = requests.get('https://api.line.me/v2/profile', headers=headers)
            req.raise_for_status()  # ステータスコード見て200番台以外だと例外発生するらしい
        except requests.exceptions.RequestException as e:
            print("get_lineuser_by_token:not permission", e.response.text)
            raise HTTPException(status_code=404, detail="not permission to view profile")

    # ここはない場合を考える必要があるのか？
    lineUserID = req.json().get('userId')
    user = get_by_lineUserID(lineUserID=lineUserID)
    disp_name=req.json().get("displayName")
    created = True
    if user:
        user = update_username(username=disp_name)
        created = False
    else:
        if create:
            user = create_user(user=UserCreate(
                lineUserID=lineUserID,
                username=disp_name
            ))
        else:
            raise HTTPException(status_code=404, detail="user not found")

    return [user, created]


# addメソッドの引数にはイベントのモデルを入れる
# 関数名は自由

# メッセージイベントの場合の処理
# かつテキストメッセージの場合
@handler.add(MessageEvent, message=TextMessage)
async def handle_text_message(event):
    # メッセージでもテキストの場合はオウム返しする
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )

# メッセージイベントの場合の処理
# かつスタンプメッセージの場合
# @handler.add(MessageEvent, message=StickerMessage)
# def handle_text_message(event):
#     delStamp(event.reply_token, event.source.user_id)
    # line_introS.showTickets(event.reply_token)


# ポストバックイベントの場合の処理
# @handler.add(PostbackEvent)
# def handle_postback_message(event):

#     pb_mess = event.postback.data
#     if pb_mess == 'ShowTickets':
#         # print(event.reply_token, event.source.user_id)
#         line_message.showTickets(event.reply_token, event.source.user_id)
#     elif pb_mess == 'ShowCard':
#         showCards(event.reply_token, event.source.user_id)
#     elif "place=" in pb_mess:
#         getPlaceMap(event.reply_token, int(pb_mess.replace("place=","")))
#     elif pb_mess == 'StartQA':
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text="準備中です")
#         )
#     # # メッセージでもテキストの場合はオウム返しする
#     # line_bot_api.reply_message(
#     #     event.reply_token,
#     #     TextSendMessage(text=event.message.text)
#     # )


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
        logging.error(e)
    await upsert_user(db=db, values=upsert_values)
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text="こんにちは"),
            # FlexSendMessage(alt_text="チラシ", contents=stampPanf())
            # # TextSendMessage(text='画面下のメニューより、BAR-GAIチケットの購入・利用、お持ちのチケットの確認ができます。\n'
            #                 # + 'チャットは自動返信となります。ご不明点はメニュー「Q&A」よりお問合せください')
            # TextSendMessage(text=
            #     "友達追加ありがとうございます！\n"+
            #     "長崎居留地アベニュー実行委員会です。\n"+s
            #     "\n"+
            #     "この公式LINEアカウントでは、「長崎居留地プレミアムクーポン2023」のオンラインクーポン購入から、店舗での決済まで使うことができます。\n"+
            #     "\n"+
            #     "◎期間：2023年9月16日（土）〜12月31日（日）\n"+
            #     "1,000部限定の発行です。売り切れ次第、終了となりますので、お早めにお買い求めください。\n"+
            #     "\n"+
            #     "◎購入方法：\n"+
            #     "下部に表示されるメニュー画面の「買う」ボタンをタップすると、購入画面に移動します。\n"+
            #     "※販売開始は9月16日（土）10時からです。\n"+
            #     "\n"+
            #     "◎使用方法：\n"+
            #     "下部に表示されるメニュー画面の「使う」ボタンをタップすると、決済画面に移動します。カメラが起動しますので、店舗に設置してあるQRコードを読み取りください。\n"+
            #     "\n"+
            #     "「確認」ボタンより、クーポンの残高（残数）を確認することができます。\n"+
            #     "\n"+
            #     "\n"+
            #     "※ 「長崎居留地プレミアムクーポン2023」は紙クーポンもご用意しております。\n"+
            #     "加盟店舗で直接購入、もしくは9月16〜18日の特別販売会にてお買い求めください。"
            #     ),
            # FlexSendMessage(alt_text="長崎居留地プレミアムクーポン2023開催！！", contents=line_message.makefollowedCarousel())
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

# @handler.add(JoinEvent)
# def handle_join(event):
#     source = event.get("source")
#     memberIDs=0

#     if source.get("type") == "group":
#         tag = "groupId"
#         getIds = line_bot_api.get_group_member_ids
#         leaveFun = line_bot_api.leave_group
#     elif source.get("type") == "room":
#         tag = "roomId"
#         getIds = line_bot_api.get_room_member_ids
#         leaveFun = line_bot_api.leave_room
#     else:
#         return

#     id = source.get(tag)
#     memberIDs = getIds(id)
#     if not "U45a8486c1f11dacd2dc6c7abc8a74513" in memberIDs.member_ids:
#         leaveFun(id)
