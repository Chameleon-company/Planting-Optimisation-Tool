from pathlib import Path

import suitability_scoring

# from exclusion_rules.run_exclusion_core_logic import load_exclusion_config
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from suitability_scoring import load_yaml

from src.domains.suitability_scoring import SuitabilitySpecies
from src.models.agroforestry_type import AgroforestryType
from src.models.soil_texture import SoilTexture
from src.models.species import Species
from src.schemas.species import SpeciesCreate, SpeciesUpdate


def get_recommend_config():
    # This is a very ugly workaround, which i'm only committing so that I can get a successful test recommendation.
    # It desperately needs to be refactored to not be so ugly in future.
    # Start at .../datascience/src/suitability_scoring/__init__.py
    # Go up 3 levels to get to .../datascience/
    base_path = Path(suitability_scoring.__file__).resolve().parent.parent.parent
    config_path = base_path / "config" / "recommend.yaml"

    if not config_path.exists():
        # This will say where it looked so it can be debugged if it fails
        raise FileNotFoundError(f"YAML not found! Looked in: {config_path}")

    return load_yaml(str(config_path))


async def get_all_species_for_engine(db: AsyncSession) -> list[SuitabilitySpecies]:
    stmt = select(Species).options(selectinload(Species.soil_textures))
    result = await db.execute(stmt)
    return [SuitabilitySpecies.from_db_model(sp) for sp in result.scalars().all()]


async def get_species_by_ids(db: AsyncSession, ids: list[int], order_by_id: bool = True) -> list[SuitabilitySpecies]:
    if not ids:
        return []

    stmt = select(Species).options(selectinload(Species.soil_textures)).where(Species.id.in_(ids))
    if order_by_id:
        stmt = stmt.order_by(Species.id)

    result = await db.execute(stmt)
    species_rows = result.scalars().all()
    return [SuitabilitySpecies.from_db_model(sp) for sp in species_rows]


async def create_species(db: AsyncSession, payload: SpeciesCreate) -> Species:
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

    if payload.soil_textures:
        res = await db.execute(select(SoilTexture).where(SoilTexture.id.in_(payload.soil_textures)))
        new_species.soil_textures = list(res.scalars().all())

    if payload.agroforestry_types:
        res = await db.execute(select(AgroforestryType).where(AgroforestryType.id.in_(payload.agroforestry_types)))
        new_species.agroforestry_types = list(res.scalars().all())

    db.add(new_species)
    await db.commit()

    result = await db.execute(select(Species).where(Species.id == new_species.id).options(selectinload(Species.soil_textures), selectinload(Species.agroforestry_types)))
    return result.scalar_one()


async def update_species(db: AsyncSession, species_id: int, payload: SpeciesUpdate) -> Species | None:
    result = await db.execute(select(Species).where(Species.id == species_id).options(selectinload(Species.soil_textures), selectinload(Species.agroforestry_types)))
    species = result.scalar_one_or_none()

    if species is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    soil_texture_ids = update_data.pop("soil_textures", None)
    agroforestry_type_ids = update_data.pop("agroforestry_types", None)

    for field, value in update_data.items():
        setattr(species, field, value)

    if soil_texture_ids is not None:
        res = await db.execute(select(SoilTexture).where(SoilTexture.id.in_(soil_texture_ids)))
        species.soil_textures = list(res.scalars().all())

    if agroforestry_type_ids is not None:
        res = await db.execute(select(AgroforestryType).where(AgroforestryType.id.in_(agroforestry_type_ids)))
        species.agroforestry_types = list(res.scalars().all())

    await db.commit()

    refreshed = await db.execute(select(Species).where(Species.id == species_id).options(selectinload(Species.soil_textures), selectinload(Species.agroforestry_types)))
    return refreshed.scalar_one()


async def delete_species(db: AsyncSession, species_id: int) -> bool:
    result = await db.execute(select(Species).where(Species.id == species_id))
    species = result.scalar_one_or_none()

    if species is None:
        return False

    await db.delete(species)
    await db.commit()
    return True


async def get_species_for_dropdown(db: AsyncSession):
    """
    Fetches a lightweight list of species IDs and names.
    Optimised to only query the required columns.
    """
    # Select only the needed columns and order alphabetically by common name
    stmt = select(Species.id, Species.name, Species.common_name).order_by(Species.common_name)

    result = await db.execute(stmt)

    return result.all()


def get_recommendation_features() -> list[str]:
    """
    Returns only the 'short' names of features for frontend display.
    Example: ['Rinfall', 'Temperature', 'pH']
    """
    # Use existing config loader
    config_data = get_recommend_config()

    features_dict = config_data.get("features", {})

    # Extract only the 'short' string from each feature config
    short_names = []
    for feature_cfg in features_dict.values():
        if "short" in feature_cfg:
            raw_short = str(feature_cfg["short"])

            # Check for pH case-insensitively
            if raw_short.lower() == "ph":
                short_names.append("pH")
            else:
                short_names.append(raw_short.title())

    return short_names
