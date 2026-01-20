from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime


class RecommendationReportEntry(BaseModel):
    """Represents a single species recommendation within a report."""

    model_config = ConfigDict(from_attributes=True)

    species_id: int
    species_name: str
    species_common_name: str
    rank_overall: int
    score_mcda: float
    key_reasons: List[str]


class FarmReportMetadata(BaseModel):
    """Basic farm details to include in the report header."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    rainfall_mm: int
    temperature_celsius: int
    ph: float
    soil_texture: str


class FarmReportContract(BaseModel):
    """
    The 'Contract' for reporting.py.
    Contains everything needed to generate a comprehensive farm summary.
    """

    model_config = ConfigDict(from_attributes=True)

    farm: FarmReportMetadata
    recommendations: List[RecommendationReportEntry]
    generated_at: datetime

    @classmethod
    def from_db_data(cls, farm_obj, recommendation_objs):
        """
        Adapter to assemble the report from multiple DB entities.
        """
        recs = [
            RecommendationReportEntry(
                species_id=r.species_id,
                species_name=r.species.name,
                species_common_name=r.species.common_name,
                rank_overall=r.rank_overall,
                score_mcda=r.score_mcda,
                key_reasons=r.key_reasons,
            )
            for r in recommendation_objs
        ]

        return cls(
            farm=FarmReportMetadata.model_validate(farm_obj),
            recommendations=recs,
            generated_at=datetime.now(),
        )
