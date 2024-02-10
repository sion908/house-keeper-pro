import logging
import os
from enum import Enum


class Tags(str, Enum):
    # https://fastapi.tiangolo.com/tutorial/metadata/#use-your-tags
    user = "user"


DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
LINE_ACCESS_SECRET = os.environ.get("LINE_ACCESS_SECRET")

logging.basicConfig(level=logging.INFO if DEBUG else logging.DEBUG)
