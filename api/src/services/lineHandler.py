import json

from linebot.models import (
    FollowEvent,
    ImagemapSendMessage,
    MessageEvent,
    PostbackEvent,
    TextMessage,
    TextSendMessage,
    UnfollowEvent,
)
from linebot.models.imagemap import BaseSize, ImagemapArea, URIImagemapAction
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user import upsert as upsert_user
from database.db import session_aware
from dependencies import line_bot_api
from dependencies.line import handler
from services.card import CardService
from setting import logger

logger.name = __name__

# addメソッドの引数にはイベントのモデルを入れる
# 関数名は自由

# メッセージイベントの場合の処理
# かつテキストメッセージの場合
@handler.add(MessageEvent, message=TextMessage)
async def handle_text_message(event):
    if event.message.text == "スタンプカードを確認する":
        await CardService.showCards(rep_token=event.reply_token, luserid=event.source.user_id)

# メッセージイベントの場合の処理
# かつスタンプメッセージの場合
# @handler.add(MessageEvent, message=StickerMessage)
# def handle_text_message(event):
#     delStamp(event.reply_token, event.source.user_id)
    # line_introS.showTickets(event.reply_token)


# ポストバックイベントの場合の処理
@handler.add(PostbackEvent)
async def handle_postback_message(event):

    pb_mess = event.postback.data
    if pb_mess == 'ShowCard':
        await CardService.showCards(rep_token=event.reply_token, luserid=event.source.user_id)
    # elif "place=" in pb_mess:
    #     getPlaceMap(event.reply_token, int(pb_mess.replace("place=","")))
    elif pb_mess == 'StartQA':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="準備中です")
        )
    # # メッセージでもテキストの場合はオウム返しする
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text)
    # )


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
                text="・Barの楽しみ方塾です。バーに行ったことが無い人でも気軽に行けるバーのスタンプラリー開催中。\n"+
                     "・５エリア中、３エリアのバーを巡ったら、抽選で景品をプレゼント！\n"+
                     "  スタンプがそろったら表示されるURLから応募してね！\n"+
                     "・スタンプラリー対象店舗は、配布している冊子か、Barの楽しみ方塾のSNS（旧Twitter、Instagram）を参照ください。"
                ),
            ImagemapSendMessage(
                base_url = "https://stamprally-sake.s3.ap-northeast-1.amazonaws.com/helloMapImg",
                alt_text = "Bar巡りをお楽しみください．各種リンクはこちらより．",
                base_size = BaseSize(1024, 1024),
                actions = [
                    URIImagemapAction(
                        link_uri="https://www.google.com/maps/d/u/0/edit?mid=11BB3QUD3YAmgEOandosNejMn97KZahA&usp=sharing",
                        area=ImagemapArea(
                            x=512,
                            y=0,
                            width=512,
                            height=512,
                        )
                    ),
                    URIImagemapAction(
                        link_uri="https://twitter.com/BAR_nagasaki",
                        area=ImagemapArea(
                            x=0,
                            y=512,
                            width=512,
                            height=512,
                        )
                    ),
                    URIImagemapAction(
                        link_uri="https://www.instagram.com/cowbeff11?utm_source=qr&igsh=dXpmY3MyOG1nODJ5",
                        area=ImagemapArea(
                            x=512,
                            y=512,
                            width=512,
                            height=512,
                        )
                    )
                ]
            )
                # https://res.cloudinary.com/djutwrn9m/image/upload/v1709456291/imageMap_mbvgob.png
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
