from fastapi import APIRouter, Header, HTTPException, Request
from linebot.exceptions import InvalidSignatureError

from services.lineHandler import handler

router = APIRouter()

@router.post(
    "/callback",
    description="ユーザーからメッセージが送信された際、LINE Message APIからこちらのメソッドが呼び出されます。",
)
async def line_messaging(
    request: Request,
    x_line_signature=Header(None)
):
    # リクエストボディを取得
    body = await request.body()
    try:
        # 署名を検証し、問題なければhandleに定義されている関数を呼び出す
        handler.custom_handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        # 署名検証で失敗したときは例外をあげる
        HTTPException(status_code=404, detail="InvalidSignature")
    # handleの処理を終えればOK
    return HTTPException(status_code=200, detail="OK")
