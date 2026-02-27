from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from src.schemas.farm import FarmCreate
from src.models import Farm, AgroforestryType


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
        result = await db.execute(
            select(AgroforestryType).where(AgroforestryType.id.in_(agroforestry_ids))
        )
        selected_types = list(result.scalars().all())

        # Link them
        db_farm.agroforestry_type = selected_types

    # 5. Persist
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


async def get_farm_by_id(
    db: AsyncSession, farm_ids: list[int], user_id: int, user_role: str = "officer"
) -> list[Farm] | None:
    """
    Retrieves one or many Farm records, filtered by farm_id AND user_id
    to enforce ownership authorization.

    Includes selectinload for relationships to prevent MissingGreenlet errors
    during Pydantic serialization.
    """
    # We add .options(selectinload(...)) for every relationship
    # that the FarmRead schema needs to display.
    stmt = (
        select(Farm)
        .options(
            selectinload(Farm.soil_texture),
            selectinload(Farm.agroforestry_type),
            selectinload(Farm.farm_supervisor),
        )
        .where((Farm.id.in_(farm_ids)))
    )
    if user_role == "officer":
        stmt = stmt.where(Farm.user_id == user_id)

    result = await db.execute(stmt)

    return list(result.scalars().all())
