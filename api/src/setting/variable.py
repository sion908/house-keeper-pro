import logging
import os
from enum import Enum


class Tags(str, Enum):
    # https://fastapi.tiangolo.com/tutorial/metadata/#use-your-tags
    user = "user"
    seal = "seal"


DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
LINE_ACCESS_SECRET = os.environ.get("LINE_ACCESS_SECRET")

STAGE_NAME = os.environ.get("STAGE_NAME")

SRLinehandlerName = os.environ.get("SRLinehandlerName")

logging.getLogger().setLevel(level=logging.INFO if DEBUG else logging.WARNING)

loggin_format = "%(levelname)-9s  %(asctime)s [%(filename)s:%(lineno)d] %(message)s"

st_handler = logging.StreamHandler()
# StreamHandlerによる出力フォーマットを先で定義した'format'に設定
st_handler.setFormatter(logging.Formatter(loggin_format))
logger = logging.getLogger("stamprally")
logger.addHandler(st_handler)
