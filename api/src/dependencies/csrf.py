from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel


class CsrfSettings(BaseModel):
    secret_key: str = "asecrettoeverybody"
    cookie_samesite: str = "none"
    # HTTPSであることを必須とする
    cookie_secure: bool = True
    token_location: str = "body"
    token_key: str = "csrf-token"


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()
