import suitability_scoring
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from suitability_scoring import load_yaml
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


async def get_all_species_for_engine(db: AsyncSession) -> list[SuitabilitySpecies]:
    stmt = select(Species).options(selectinload(Species.soil_textures))
    result = await db.execute(stmt)
    return [SuitabilitySpecies.from_db_model(sp) for sp in result.scalars().all()]
