from pydantic import BaseModel, ConfigDict, Field


class SoilTextureBase(BaseModel):
    name: str = Field(..., description="The human-readable name of the soil texture.")


class SoilTextureCreate(SoilTextureBase):
    pass


class SoilTextureRead(SoilTextureBase):
    id: int = Field(..., description="The unique ID of the soil texture.")

    model_config = ConfigDict(from_attributes=True)


class SoilTextureUpdate(SoilTextureBase):
    pass
