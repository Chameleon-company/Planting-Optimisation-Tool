from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.farm import FarmCreate
from src.models import Farm


async def create_farm_record(db: AsyncSession, farm_data: FarmCreate, user_id: int):
    """
    Creates a new Farm record in the database.
    """
    # Prepare the data
    farm_data_dict = farm_data.model_dump()

    # Add the Foreign Key
    farm_data_dict["user_id"] = user_id

    # Create the ORM object
    db_farm = Farm(**farm_data_dict)

    # 4. Add to session and commit
    db.add(db_farm)
    await db.commit()

    # Refresh the object (essential for getting the new ID and relationships)
    await db.refresh(db_farm)

    return db_farm
