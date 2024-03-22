import datetime

from fastapi import APIRouter, Depends, Form, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession

from crud.answer import create as create_answer
from crud.form import get_by_pk
from crud.imgAnswer import create as create_img_answer
from crud.user import get_by_pk as get_user_by_pk
from database.db import get_db
from dependencies import CsrfProtect, get_lineuser_by_token, templates
from schemas.report import AnswerBase, ImagePair
from services.s3 import upload_file
from setting import STAGE_NAME, logger

logger.name = __name__

router = APIRouter()


@router.get("/{form_id}")
async def get_report_form(
    request: Request,
    form_id: int = Path(title="フォームのID"),
    db: AsyncSession = Depends(get_db),
    csrf_protect: CsrfProtect = Depends()
):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    form = await get_by_pk(db=db, form_id=form_id)
    context = {
        "request": request,
        "STAGE_NAME": STAGE_NAME,
        "csrf_token": csrf_token,
        "form": form,
        "liff_id": "2004221000-1rEmRmzE"
    }
    response = templates.TemplateResponse(
        "report.html",
        context
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response

@router.post("/{form_id}")
async def create_report_form(
    request: Request,
    answerBase: AnswerBase,
    form_id: int = Path(..., title="フォームのID"),
    db: AsyncSession = Depends(get_db),
    # csrf_protect: CsrfProtect = Depends()
):
    # await csrf_protect.validate_csrf(request)
    user, _ = await get_lineuser_by_token(db=db, token=answerBase.lineToken, create=True)

    answer = await create_answer(db=db, answerBase=answerBase, user=user, form_id=form_id)

    # S3にアップロードしたオブジェクトのパス
    # file_url = "https://%s.s3-%s.amazonaws.com/%s" % (s3_bucket, region_name, s3_dir+"/"+file.filename)

    return {"success": True, "answerId": answer.id}

@router.post("/{form_id}/answer/{answer_id}/order/{stub_id}")
async def create_report_img(
    request: Request,
    image_pair: ImagePair = Depends(),
    form_id: int = Path(title="フォームのID"),
    answer_id: int = Path(title="回答フォームのID"),
    stub_id: int = Path(title="回答のID"),
    lineToken: str = Form(..., title="lineのユーザートークン"),
    db: AsyncSession = Depends(get_db),
    # csrf_protect: CsrfProtect = Depends()
):
    # await csrf_protect.validate_csrf(request)
    user, _ = await get_lineuser_by_token(db=db, token=lineToken, create=True)
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    d = now.strftime('%Y%m%d%H%M%S')

    before_image_key = upload_file(
        f"img/{form_id}/{stub_id}/{d}-be.{image_pair.afterImage.filename.split('.')[-1]}",
        image_pair.beforeImage.file
    )
    after_image_key = upload_file(
        f"img/{form_id}/{stub_id}/{d}-af.{image_pair.afterImage.filename.split('.')[-1]}",
        image_pair.afterImage.file
    )

    img_answer = await create_img_answer(
        db=db,
        key_be=before_image_key,
        key_af=after_image_key,
        form_stub_id=stub_id,
        answer_id=answer_id,
    )

    # S3にアップロードしたオブジェクトのパス
    # file_url = "https://%s.s3-%s.amazonaws.com/%s" % (s3_bucket, region_name, s3_dir+"/"+file.filename)

    return {"success": True, "imgAnswer": img_answer}
