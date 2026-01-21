import suitability_scoring
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from suitability_scoring import load_yaml
from exclusion_rules.run_exclusion_core_logic import load_exclusion_config
from src.models.species import Species
from src.domains.suitability_scoring import SuitabilitySpecies


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


def get_exclusion_config():
    # TODO The exclusion config file should be merged with the recommend config file, then this function can be removed
    # See comment for get_recommend_config()
    base_path = Path(suitability_scoring.__file__).resolve().parent.parent.parent
    config_path = base_path / "config" / "exclusion_config.json"

    if not config_path.exists():
        # This will say where it looked so it can be debugged if it fails
        raise FileNotFoundError(f"JSON not found! Looked in: {config_path}")

    return load_exclusion_config(str(config_path))


async def get_all_species_for_engine(db: AsyncSession) -> list[SuitabilitySpecies]:
    stmt = select(Species).options(selectinload(Species.soil_textures))
    result = await db.execute(stmt)
    return [SuitabilitySpecies.from_db_model(sp) for sp in result.scalars().all()]


async def get_species_by_ids(
    db: AsyncSession, ids: list[int], order_by_id: bool = True
) -> list[SuitabilitySpecies]:
    if not ids:
        return []

    stmt = (
        select(Species)
        .options(selectinload(Species.soil_textures))
        .where(Species.id.in_(ids))
    )
    if order_by_id:
        stmt = stmt.order_by(Species.id)

    result = await db.execute(stmt)
    species_rows = result.scalars().all()
    return [SuitabilitySpecies.from_db_model(sp) for sp in species_rows]
