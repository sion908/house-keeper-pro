from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel

from setting import csrf_settings, is_local


class CsrfSettings(BaseModel):
    secret_key: str = f"{csrf_settings.CSRF_SECRET_KEY}-tiovita"
    cookie_samesite: str = "strict"
    # HTTPSであることを必須とする
    cookie_secure: bool = not is_local
    token_location: str = "header"

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()
