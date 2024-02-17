from fastapi import FastAPI
from mangum import Mangum

from exception import add_exception_handlers
from routers import line
from setting import DEBUG

app = FastAPI(debug=DEBUG)

app.include_router(
    line.router,
    prefix="/lineapi",
)

add_exception_handlers(app)

handler = Mangum(app)

if DEBUG:
    import logging

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
        logging.basicConfig(level=logging.DEBUG)
        logging.info(f"res_body: {res_body}")

    @app.middleware('http')
    async def some_middleware(request: Request, call_next):
        req_body = await request.body()
        await set_body(request, req_body)
        logging.info(f"req_body: {req_body}")
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
