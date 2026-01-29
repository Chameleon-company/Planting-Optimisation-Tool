from pydantic import BaseModel, Field, ConfigDict


# Nested model for the User/supervisor
class UserReadNested(BaseModel):
    """Schema for displaying the farm supervisor's details in FarmRead."""

    id: int = Field(..., description="The unique ID of the farm supervisor.")
    email: str = Field(..., description="Email address of the farm supervisor.")

    model_config = ConfigDict(from_attributes=True)


# Nested model for Agroforestry Type
class AgroforestryTypeReadNested(BaseModel):
    """Schema for displaying M:M related agroforestry types."""

    id: int
    type_name: str = Field(..., description="Name of the agroforestry type.")

    model_config = ConfigDict(from_attributes=True)


# Nested model for Soil Texture type
class SoilTextureReadNested(BaseModel):
    """Schema for displaying the soil texture name."""

    id: int
    name: str = Field(
        ..., description="Name of the soil texture type (e.g., 'Clay', 'Loam')."
    )

    model_config = ConfigDict(from_attributes=True)
