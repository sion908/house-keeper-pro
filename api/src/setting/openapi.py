from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

from .variable import Tags

tags_metadata = [
    {
        "name": Tags.user,
        "description": "ユーザーに関するAPI",
    },
    {
        "name": Tags.seal,
        "description": "スタンプを押す用のAPIとか",
    },
]


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    For API operation_id, use lowerCamelCase naming (e.g., functionName).
    For API summary, replace underscores with spaces (e.g., function name).
    """
    def to_camel_case(snake_str):
        return "".join(x.capitalize() for x in snake_str.lower().split("_"))

    def to_lower_camel_case(snake_str):
        camel_string = to_camel_case(snake_str)
        return snake_str[0].lower() + camel_string[1:]

    for _route in app.routes:
        if isinstance(_route, APIRoute):
            _route.operation_id = _route.operation_id or to_lower_camel_case(_route.name)
            _route.summary = _route.summary or _route.name.replace("_", " ")


def add_custom_openapi(app: FastAPI) -> None:
    def custom_openapi() -> None:
        if app.openapi_schema:
            return app.openapi_schema
        servers = [
            {
                "url": "http://127.0.0.1:3000",
                "description": "local sam"
            },
        ]
        openapi_schema = get_openapi(
            title="stamp-rally",
            version="0.1.1",
            openapi_version="3.0.3",
            description="stamp-rallyのAPI設計",
            tags=tags_metadata,
            routes=app.routes,
            servers=servers
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi


def generate_openapi(app: FastAPI) -> None:
    use_route_names_as_operation_ids(app)
    add_custom_openapi(app)
