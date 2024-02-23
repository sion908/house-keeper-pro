from pydantic import BaseModel, Field


class StampSealForm(BaseModel):
    """スタンプの押印処理時に受け取るpostのform的なもの"""

    lineToken: str = Field(..., description="liff用のToken")
    place_id: int = Field(..., description="スタンプを押した場所")
