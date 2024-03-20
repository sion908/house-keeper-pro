from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi_csrf_protect.exceptions import CsrfProtectError

from setting import logger

from .exceptions import SimpleException

logger.name = __name__

def add_exception_handlers(app):

    @app.exception_handler(SimpleException)
    async def simple_exception_handler(request: Request, exc: SimpleException):  # noqa: U100
        logger.warning(f"MyException occured!!! {exc.msg}")
        return JSONResponse(status_code=exc.status_code, content=exc.msg)

    @app.exception_handler(CsrfProtectError)
    def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
