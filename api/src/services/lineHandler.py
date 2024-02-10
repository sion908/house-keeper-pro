import inspect
import json

import boto3
from linebot import WebhookHandler, WebhookPayload
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

from setting import logging

logger = logging.getLogger(__name__)


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
                FunctionName=f"SRLinehandler-{'dev'}",
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
