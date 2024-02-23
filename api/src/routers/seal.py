from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db

from crud.place import get_by_id as get_place_by_id
from crud.card import create_with_stamps
from crud.user import get_with_card
from crud.rallyconfigration import get_one
from schemas.seal import StampSealForm
from services.card import CardService
from setting import Tags
from dependencies import CsrfProtect, templates, get_lineuser_by_token
from setting import logger, STAGE_NAME

logger.name = __name__

router = APIRouter()


@router.get(
    "/",
    response_class=HTMLResponse,
    tags=[Tags.seal]
)
async def seal_stamp_disp(
    request: Request,
    place_id: int = None,
    db: AsyncSession = Depends(get_db),
    csrf_protect: CsrfProtect = Depends()
):
    """
    return seal dispray:

    - **username**(str):
    - **password**(str):
    - **sex**(int): [男性:0,女性:1,その他2]
    - **age**(int):
    """
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    rally_configuration = await get_one(db=db, is_active=True)
    context = {
        "request": request,
        "csrf_token": csrf_token,
        "liff_id": rally_configuration.liff_id,
        "STAGE_NAME": STAGE_NAME
    }

    if place_id:
        place = await get_place_by_id(db=db, place_id=place_id)
        context["place"] = place
    response = templates.TemplateResponse(
        "seal.html",
        context
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.post(
    "/",
    response_class=JSONResponse,
    tags=[Tags.seal]
)
async def seal_stamp_post(
    request: Request,
    stamp_seal: StampSealForm,
    db: AsyncSession = Depends(get_db),
    csrf_protect: CsrfProtect = Depends()
):
    """
    Creates a new Post
    """
    await csrf_protect.validate_csrf(request)

    user, _ = await get_lineuser_by_token(db=db, token=stamp_seal.lineToken, create=True)

    user = await get_with_card(db=db, id=user.id)
    card_service = CardService()
    await card_service.async_init(db=db, user=user)

    context = await card_service.seal_stamp(place_id=stamp_seal.place_id)

    # response: JSONResponse = JSONResponse(status_code=200, content={"detail": "OK"})
    # csrf_protect.unset_csrf_cookie(response)  # prevent token reuse
    return JSONResponse(context)
