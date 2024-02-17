from setting import logger

logger.name = __name__

from fastapi import Request
from fastapi.responses import JSONResponse

from .exceptions import SimpleException


def add_exception_handlers(app):

    @app.exception_handler(SimpleException)
    async def simple_exception_handler(request: Request, exc: SimpleException):  # noqa: U100
        logger.warning(f"MyException occured!!! {exc.msg}")
        return JSONResponse(status_code=exc.status_code, content=exc.msg)
