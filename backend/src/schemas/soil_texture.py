from pydantic import BaseModel


class SoilTextureRead(BaseModel):
    id: int
    texture_name: str

    class Config:
        from_attributes = True
