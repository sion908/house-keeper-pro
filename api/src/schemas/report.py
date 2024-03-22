from datetime import datetime

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field, validator

from dependencies import get_lineuser_by_token
from models import User


class AnswerBase(BaseModel):
    timeInputStart: datetime = Field(..., title="業務開始時間")
    timeInputEnd: datetime = Field(..., title="業務終了時間")
    lineToken: str = Field(..., title="lineのユーザートークン")

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        populate_by_name = True

    @validator('timeInputStart')
    def validate_timeInputStart(cls, value):
        cls.start = value
        return value

    @validator('timeInputEnd')
    def validate_timeInputEnd(cls, value):
        cls.end = value
        return value


class ImagePair(BaseModel):
    beforeImage: UploadFile = File(...)
    afterImage: UploadFile = File(...)

    class Config:
        arbitrary_types_allowed = True
