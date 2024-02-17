# flake8: noqa: E800,F401
import boto3
# from django.shortcuts import get_object_or_404
import requests
# from django.http import Http404
from fastapi import Depends, HTTPException
# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi

from crud.user import create as create_user
from crud.user import get_by_lineUserID, update_username
from schemas.user import UserCreate
from services.lineEventHandler import MyWebhookHandler
from setting import CHANNEL_ACCESS_TOKEN, LINE_ACCESS_SECRET

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
