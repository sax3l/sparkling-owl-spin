from pydantic import BaseModel
from typing import Any

class JobCreate(BaseModel):
    template_id: int
    params: dict[str, Any] | None = None

class JobOut(BaseModel):
    id: int
    status: str
    total_pages: int | None = None
    total_items: int | None = None
    error: str | None = None
    class Config:
        from_attributes = True
