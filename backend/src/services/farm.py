from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import AgroforestryType, Farm
from src.schemas.farm import FarmCreate


async def create_farm_record(db: AsyncSession, farm_data: FarmCreate, user_id: int):
    # Convert Pydantic to Dict
    farm_data_dict = farm_data.model_dump()

    # Extract the Agroforestry IDs
    # We remove them from the dict so SQLAlchemy doesn't crash
    agroforestry_ids = farm_data_dict.pop("agroforestry_type_ids", [])

    # Create the Base Farm Object
    db_farm = Farm(**farm_data_dict, user_id=user_id)

    # FETCH AND ATTACH (The logic for the end-user)
    if agroforestry_ids:
        # Find the actual 'AgroforestryType' objects in the DB
        # that match the IDs the user sent
        result = await db.execute(select(AgroforestryType).where(AgroforestryType.id.in_(agroforestry_ids)))
        selected_types = list(result.scalars().all())

        # Link them
        db_farm.agroforestry_type = selected_types

    # Commit to db
    db.add(db_farm)
    await db.commit()

    result = await db.execute(
        select(Farm)
        .options(
            selectinload(Farm.farm_supervisor),
            selectinload(Farm.soil_texture),
            selectinload(Farm.agroforestry_type),
        )
        .where(Farm.id == db_farm.id)
    )
    return result.scalar_one()


async def get_farm_by_id(db: AsyncSession, farm_ids: list[int], user_id: int | None = None) -> list[Farm]:
    """Retrieves one or many Farm records by ID.
    If user_id is provided, results are filtered to that owner only.
    """
    stmt = (
        select(Farm)
        .options(
            selectinload(Farm.soil_texture),
            selectinload(Farm.agroforestry_type),
            selectinload(Farm.farm_supervisor),
        )
        .where(Farm.id.in_(farm_ids))
    )
    if user_id is not None:
        stmt = stmt.where(Farm.user_id == user_id)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_farms_by_user(db: AsyncSession, user_id: int) -> list[Farm]:
    """Retrieves all Farm records belonging to a specific user."""
    stmt = (
        select(Farm)
        .options(
            selectinload(Farm.soil_texture),
            selectinload(Farm.agroforestry_type),
            selectinload(Farm.farm_supervisor),
        )
        .where(Farm.user_id == user_id)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
