# flake8: noqa: E800,F401
import boto3
import requests
import inspect
import json
import boto3
from fastapi import HTTPException
from linebot import LineBotApi, WebhookHandler, WebhookPayload
from linebot.exceptions import InvalidSignatureError
from linebot.models.events import (
    AccountLinkEvent,
    BeaconEvent,
    FollowEvent,
    JoinEvent,
    LeaveEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
    MessageEvent,
    PostbackEvent,
    ThingsEvent,
    UnfollowEvent,
    UnknownEvent,
    UnsendEvent,
    VideoPlayCompleteEvent,
)
from sqlalchemy.ext.asyncio import AsyncSession


from crud.user import create as create_user
from crud.user import get_by_lineUserID, update_username
from models import User
from schemas.user import UserCreate
from setting import CHANNEL_ACCESS_TOKEN, LINE_ACCESS_SECRET, logger, SRLinehandlerName

logger.name = __name__

line_bot_api = LineBotApi(channel_access_token=CHANNEL_ACCESS_TOKEN)


async def get_lineuser_by_token(db:AsyncSession, token, create=False) -> list[User, bool]:
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
    user = await get_by_lineUserID(db=db, lineUserID=lineUserID)
    disp_name=req.json().get("displayName")
    created = True
    if user:
        user = await update_username(db=db, user=user, username=disp_name)
        created = False
    else:
        if create:
            user = await create_user(db=db, user=UserCreate(
                lineUserID=lineUserID,
                username=disp_name
            ))
        else:
            raise HTTPException(status_code=404, detail="user not found")

    return [user, created]



class MyWebhookHandler(WebhookHandler):

    def custom_handle(self, body, signature):
        """Handle webhook.

        :param str body: Webhook request body (as text)
        :param str signature: X-Line-Signature value (as text)
        :param bool use_raw_message: Using original Message key as attribute
        """
        if not self.parser.signature_validator.validate(body, signature):
            raise InvalidSignatureError(
                'Invalid signature. signature=' + signature)
        body_json = json.loads(body)

        for event in body_json['events']:
            Lambda = boto3.client("lambda")
            Lambda.invoke(
                FunctionName=SRLinehandlerName,
                InvocationType='Event',
                Payload=json.dumps({
                    "event": event,
                    "payload": {
                        "destination": body_json.get('destination')
                    }
                })
            )

    async def do_each_event(self, event, payload):

        event_type = event['type']
        each_event = {
            'message': MessageEvent,
            'follow': FollowEvent,
            'unfollow': UnfollowEvent,
            'join': JoinEvent,
            'leave': LeaveEvent,
            'postback': PostbackEvent,
            'beacon': BeaconEvent,
            'accountLink': AccountLinkEvent,
            'memberJoined': MemberJoinedEvent,
            'memberLeft': MemberLeftEvent,
            'things': ThingsEvent,
            'unsend': UnsendEvent,
            'videoPlayComplete': VideoPlayCompleteEvent
        }
        if event_type in each_event.keys():
            event = each_event[event_type].new_from_json_dict(event)
        else:
            logger.info('Unknown event type. type=' + event_type)
            event = UnknownEvent.new_from_json_dict(event)
        key = None
        func = None

        if isinstance(event, MessageEvent):
            key = self._WebhookHandler__get_handler_key(
                event.__class__, event.message.__class__)
            func = self._handlers.get(key, None)

        if func is None:
            key = self._WebhookHandler__get_handler_key(event.__class__)
            func = self._handlers.get(key, None)

        if func is None:
            func = self._default
        if func is not None:
            payload = WebhookPayload(destination=payload["destination"])
            arg_spec = inspect.getfullargspec(func)
            (has_varargs, args_count) = (arg_spec.varargs is not None, len(arg_spec.args))
            if "db" in arg_spec.args:
                args_count -= 1
            if has_varargs or args_count == 2:
                await func(event)
            elif args_count == 1:
                await func(event)
            else:
                await func()


handler = MyWebhookHandler(channel_secret=LINE_ACCESS_SECRET)
