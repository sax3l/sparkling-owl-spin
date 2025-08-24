from pydantic import BaseModel

class TemplateCreate(BaseModel):
    name: str
    yaml: str

class TemplateOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True
