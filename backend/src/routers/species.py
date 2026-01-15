from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.database import get_db_session
from src.models.species import Species
from src.models.soil_texture import SoilTexture
from src.models.user import User
from src.models.agroforestry_type import AgroforestryType
from src.schemas.species import SpeciesCreate
from src.dependencies import CurrentActiveUser

router = APIRouter(prefix="/species", tags=["Species"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_species(
    payload: SpeciesCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = CurrentActiveUser,
):
    # Instantiate the new_species object first
    new_species = Species(
        name=payload.name,
        common_name=payload.common_name,
        rainfall_mm_min=payload.rainfall_mm_min,
        rainfall_mm_max=payload.rainfall_mm_max,
        temperature_celsius_min=payload.temperature_celsius_min,
        temperature_celsius_max=payload.temperature_celsius_max,
        elevation_m_min=payload.elevation_m_min,
        elevation_m_max=payload.elevation_m_max,
        ph_min=payload.ph_min,
        ph_max=payload.ph_max,
        coastal=payload.coastal,
        riparian=payload.riparian,
        nitrogen_fixing=payload.nitrogen_fixing,
        shade_tolerant=payload.shade_tolerant,
        bank_stabilising=payload.bank_stabilising,
    )

    # Resolve IDs to objects
    if payload.soil_textures:
        res = await db.execute(
            select(SoilTexture).where(SoilTexture.id.in_(payload.soil_textures))
        )
        new_species.soil_textures = list(res.scalars().all())

    if payload.agroforestry_types:
        res = await db.execute(
            select(AgroforestryType).where(
                AgroforestryType.id.in_(payload.agroforestry_types)
            )
        )
        new_species.agroforestry_types = list(res.scalars().all())

    # Save to database
    db.add(new_species)
    await db.commit()

    result = await db.execute(
        select(Species)
        .where(Species.id == new_species.id)
        .options(
            selectinload(Species.soil_textures),
            selectinload(Species.agroforestry_types),
        )
    )
    species_final = result.scalar_one()

    return species_final
