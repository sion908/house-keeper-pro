import os
import secrets

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

security = HTTPBasic()


def auth_basic(credentials: HTTPBasicCredentials):
    basic_user = os.environ.get("BASIC_USER", 'user')
    basic_password = os.environ.get("BASIC_PASSWORD", 'pass')
    correct_username = secrets.compare_digest(
        credentials.username, basic_user)
    correct_password = secrets.compare_digest(
        credentials.password, basic_password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect basicAuth",
            headers={"WWW-Authenticate": "Basic"},
        )


def verify_from_api(credentials: HTTPBasicCredentials = Depends(security)):
    auth_basic(credentials)


class AuthStaticFiles(StaticFiles):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def __call__(self, scope, receive, send) -> None:
        assert scope["type"] == "http"

        request = Request(scope, receive)
        credentials = await security(request)
        auth_basic(credentials)
        await super().__call__(scope, receive, send)
