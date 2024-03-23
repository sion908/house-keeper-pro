from fastapi import FastAPI
from mangum import Mangum

from exception import add_exception_handlers
from routers import line, report
from setting import DEBUG, Tags, logger

logger.name = __name__

app = FastAPI(debug=DEBUG)

app.include_router(
    line.router,
    prefix="/lineapi",
)

app.include_router(
    report.router,
    prefix="/report",
    tags=[Tags.report]
)

add_exception_handlers(app)

handler = Mangum(app)

if DEBUG:
    from fastapi import FastAPI, Request, Response
    from starlette.background import BackgroundTask
    from starlette.types import Message

    from setting.openapi import generate_openapi

    generate_openapi(app)

    async def set_body(request: Request, body: bytes):
        async def receive() -> Message:
            return {'type': 'http.request', 'body': body}
        request._receive = receive

    def log_info(res_body):
        # logging.info(f"res_body: {res_body}")

        # レスポンスボディがBlobファイルかどうかを判定する関数
        def is_blob(body):
            try:
                body.decode('utf-8')
                return False
            except UnicodeDecodeError:
                return True

        if is_blob(res_body):
            # Blobファイルの場合は内容を "[Binary data]" に置き換える
            # filename = os.path.basename(request.url.path)
            # logging.info(f"Response contains a binary file: {filename}")
            res_body = b"[Binary data]"

        logger.info(f"res_body: {res_body.decode('utf-8')}")

    @app.middleware('http')
    async def some_middleware(request: Request, call_next):
        req_body = await request.body()
        await set_body(request, req_body)
        logger.info(f"req_body: {req_body}")
        response = await call_next(request)

        res_body = b''
        async for chunk in response.body_iterator:
            res_body += chunk

        task = BackgroundTask(log_info, res_body)
        return Response(
            content=res_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
            background=task
        )

handler = Mangum(app)
