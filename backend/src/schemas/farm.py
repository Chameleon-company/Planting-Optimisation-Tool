from pydantic import BaseModel, Field

from src.schemas.constants import SoilTextureID

# from soil_texture import SoilTextureRead


class FarmBase(BaseModel):
    # WIP - Not finished
    rainfall_mm: int = Field(
        title="Annual rainfall in millimetres",
        description="Annual rainfall in millimetres - Accepted range 1000-3000.",
        ge=1000,  # ge means greater than or equal to, >=
        le=3000,  # le means less than or equal to, <=
    )
    temperature_celsius: int = Field(
        title="Annual average temperature",
        description="",
        ge=15,
        le=30,
    )
    elevation_m: int = Field(
        title="Elevation above sea level",
        description="",
        ge=0,
        le=2963,
    )
    ph: float = Field(
        title="Soil acidity/alkalinity",
        ge=4.0,
        le=8.5,
        max_digits=2,
        decimal_places=1,
    )
    soil_texture_id: SoilTextureID = Field(
        title="Soil texture ID",
        description="",
    )
    area_ha: float = Field(
        title="",
        description="",
        ge=0,
        le=100,
        decimal_places=3,
    )
    latitude: float = Field(
        title="",
        description="",
        ge=-90,
        le=90,
        decimal_places=5,
    )
    longitude: float = Field(
        title="",
        description="",
        ge=-180,
        le=180,
        decimal_places=3,
    )
    coastal: bool = Field()
    riparian: bool = Field()
    nitrogen_fixing: bool = Field()
    shade_tolerant: bool = Field()
    bank_stabilising: bool = Field()
    slope: float = Field(decimal_places=2)


"""
WIP
Notes for building model, taken from SQLAlchemy model.

area_ha: Mapped[float] = mapped_column()  # 3 decimal points
    latitude: Mapped[float] = mapped_column()  # 5 decimal points
    longitude: Mapped[float] = mapped_column()  # 5 decimal points


    coastal: Mapped[bool] = mapped_column()
    riparian: Mapped[bool] = mapped_column()
    nitrogen_fixing: Mapped[bool] = mapped_column()
    shade_tolerant: Mapped[bool] = mapped_column()
    bank_stabilising: Mapped[bool] = mapped_column()
    """


class FarmCreate(FarmBase):
    # WIP
    pass


class FarmRead(FarmBase):
    # WIP
    pass
