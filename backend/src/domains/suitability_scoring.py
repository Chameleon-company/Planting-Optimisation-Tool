from pydantic import BaseModel, ConfigDict


class SuitabilityFarm(BaseModel):
    """
    The 'Contract' for the Recommendation Engine.
    Only includes fields necessary for scoring.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    rainfall_mm: int
    temperature_celsius: int
    elevation_m: int
    ph: float  # Pydantic will auto-convert Decimal to float
    soil_texture: str

    @classmethod
    def from_db_model(cls, farm_obj):
        """
        An 'Adapter' method to flatten the complex SQLAlchemy object.
        """
        return cls(
            id=farm_obj.id,
            rainfall_mm=farm_obj.rainfall_mm,
            temperature_celsius=farm_obj.temperature_celsius,
            elevation_m=farm_obj.elevation_m,
            ph=float(farm_obj.ph),
            # Flattening the nested soil_texture object to a simple string
            soil_texture=farm_obj.soil_texture.name.lower()
            if farm_obj.soil_texture
            else "unknown",
        )


class SuitabilitySpecies(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    common_name: str
    rainfall_mm_min: int
    rainfall_mm_max: int
    temperature_celsius_min: int
    temperature_celsius_max: int
    elevation_m_min: int
    elevation_m_max: int
    ph_min: float
    ph_max: float
    soil_textures: list[str]

    @classmethod
    def from_db_model(cls, sp):
        return cls(
            id=sp.id,
            name=sp.name,
            common_name=sp.common_name,
            rainfall_mm_min=sp.rainfall_mm_min,
            rainfall_mm_max=sp.rainfall_mm_max,
            temperature_celsius_min=sp.temperature_celsius_min,
            temperature_celsius_max=sp.temperature_celsius_max,
            elevation_m_min=sp.elevation_m_min,
            elevation_m_max=sp.elevation_m_max,
            ph_min=float(sp.ph_min),
            ph_max=float(sp.ph_max),
            soil_textures=[s.name.lower() for s in sp.soil_textures],
        )
