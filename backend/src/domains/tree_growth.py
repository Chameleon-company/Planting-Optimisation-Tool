from pydantic import BaseModel, ConfigDict
from typing import List


class TreeGrowth(BaseModel):
    """
    Contract for calculating tree growth rate.
    """

    model_config = ConfigDict(from_attributes=True)

    farm_id: int
    species_id: int
    key_reasons: List[str]
    rainfall_mm: int
    temperature_celsius: int

    @classmethod
    def from_db_models(cls, recommendation_obj, farm_obj):
        return cls(
            farm_id=recommendation_obj.farm_id,
            species_id=recommendation_obj.species_id,
            key_reasons=recommendation_obj.key_reasons,
            rainfall_mm=farm_obj.rainfall_mm,
            temperature_celsius=farm_obj.temperature_celsius,
        )
