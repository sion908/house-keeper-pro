from asyncio import get_event_loop

from services.lineHandler import handler
from setting import logger

logger.name = __name__


def line_handler(event, contex):  # noqa:U100
    try:
        logger.info(f"{event['event']},{event['payload']}")
        return get_event_loop().run_until_complete(
            handler.do_each_event(event["event"], event["payload"])
        )
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
