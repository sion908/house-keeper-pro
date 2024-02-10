from asyncio import get_event_loop

from services.line import handler
from setting import logging

logger = logging.getLogger(__name__)

def line_handler(event, contex):

    logger.info(event["event"])
    logger.info(event["payload"])
    return get_event_loop().run_until_complete(
        handler.do_each_event(event["event"], event["payload"])
    )
