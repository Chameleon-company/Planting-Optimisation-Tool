from pydantic import BaseModel, Field


class EpiInputRow(BaseModel):
    farm_id: int = Field(
        title="Farm ID",
        description="Unique farm identifier",
        ge=1,
    )

    species_id: int = Field(
        title="Species ID",
        description="Unique species identifier",
        ge=1,
    )

    farm_mean_epi: float = Field(
        title="Farm Mean EPI",
        description="Mean EPI value for a given farm and species",
        ge=0.0,
    )
