import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from src.models.farm import Farm
from src.models.soil_texture import SoilTexture
from src.models.user import User


@pytest.mark.asyncio
async def test_foreign_key_cascade_delete(async_session: AsyncSession):
    """
    Verifies that deleting a SoilTexture record automatically cascades
    and deletes dependent Farm records.
    """
    session = async_session

    # Insert Parent and Child Records
    # 1a Create user
    test_user = User(email="test_user@test.com", hashed_password="password999999")
    session.add(test_user)
    await session.flush()
    user_id = test_user.id

    # 1b Create soil testure
    soil_texture = SoilTexture(texture_name="Loam")
    session.add(soil_texture)
    await session.flush()
    soil_id = soil_texture.id

    # 1b. Insert Child (Farm) referencing the Parent
    farm = Farm(
        rainfall_mm=1000053400,
        temperature_celsius=222135.08686,
        elevation_m=51123120,
        ph=63.65,
        soil_texture_id=soil_id,
        area_ha=10.02,
        latitude=5234523.42342,
        longitude=3452.3,
        coastal=False,
        riparian=True,
        nitrogen_fixing=True,
        shade_tolerant=False,
        bank_stabilising=True,
        slope=32.556,
        user_id=user_id,
    )
    session.add(farm)
    await session.flush()

    # 2. ACTION: Delete the Parent Record
    await session.execute(delete(SoilTexture).where(SoilTexture.id == soil_id))

    # 3. VERIFICATION: Check Child Record
    farm_check = await session.execute(
        select(Farm).where(Farm.soil_texture_id == soil_id)
    )

    # If CASCADE is working, the result list must be empty.
    assert farm_check.scalars().first() is None, (
        "CASCADE delete failed: Farm record still exists after parent SoilTexture was deleted."
    )
