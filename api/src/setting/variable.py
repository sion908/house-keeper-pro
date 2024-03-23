import os
from enum import Enum
from functools import lru_cache
from logging import RootLogger

from pydantic import ValidationError
from pydantic_settings import BaseSettings

from .log import log_setting


class Tags(str, Enum):
    # https://fastapi.tiangolo.com/tutorial/metadata/#use-your-tags
    user = "user"
    report = "report"


class LineSettings(BaseSettings):
    CHANNEL_ACCESS_TOKEN: str = os.environ.get("CHANNEL_ACCESS_TOKEN")
    LINE_ACCESS_SECRET: str = os.environ.get("LINE_ACCESS_SECRET")


class CsrfSettings(BaseSettings):
    CSRF_SECRET_KEY: str = os.environ.get("CSRF_SECRET_KEY")


@lru_cache
def load_settings() -> (
    tuple[
        bool,
        LineSettings,
        CsrfSettings,
        bool,
        RootLogger,
        str
    ]
):
    try:
        DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
        line_settings: LineSettings = LineSettings()
        csrf_settings: CsrfSettings = CsrfSettings()

        STAGE_NAME = os.environ.get("STAGE_NAME")
        is_local = (STAGE_NAME == "local")
        custom_logger = log_setting(stage=STAGE_NAME)
        HKPLinehandlerName = os.environ.get("HKP_LINEHANDLER_NAME")  # noqa: N806
        pass
    except ValidationError as e:
        import logging
        logging.error("Could not load settings: ", e)
        raise

    return (
        DEBUG,
        line_settings,
        csrf_settings,
        is_local,
        custom_logger,
        HKPLinehandlerName
    )


(
    DEBUG,
    line_settings,
    csrf_settings,
    is_local,
    logger,
    HKPLinehandlerName
) = load_settings()
