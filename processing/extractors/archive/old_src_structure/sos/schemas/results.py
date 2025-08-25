from pydantic import BaseModel
from typing import Any

class ResultOut(BaseModel):
    id: int
    url: str
    data: dict[str, Any]
    class Config:
        from_attributes = True
