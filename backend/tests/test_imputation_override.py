from src.models.farm import Farm
from src.schemas.farm import FarmUpdate
from src.services.farm import update_farm_record


async def test_manual_environmental_override_clears_imputation_flag(
    async_session,
    setup_soil_texture,
):
    farm = Farm(
        rainfall_mm=1500,
        temperature_celsius=22,
        elevation_m=300,
        ph=6.2,
        soil_texture_id=1,
        area_ha=5.0,
        latitude=-8.5,
        longitude=126.5,
        coastal=False,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
        slope=10.5,
        rainfall_mm_imputed=False,
        temperature_celsius_imputed=False,
        elevation_m_imputed=False,
        ph_imputed=True,
        slope_imputed=False,
    )

    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    farm_id = farm.id

    updated = await update_farm_record(
        db=async_session,
        farm_id=farm_id,
        farm_data=FarmUpdate(ph=6.5),
    )

    assert updated is not None
    assert float(updated.ph) == 6.5
    assert updated.ph_imputed is False


async def test_unchanged_environmental_value_keeps_imputation_flag(
    async_session,
    setup_soil_texture,
):
    farm = Farm(
        rainfall_mm=1500,
        temperature_celsius=22,
        elevation_m=300,
        ph=6.2,
        soil_texture_id=1,
        area_ha=5.0,
        latitude=-8.5,
        longitude=126.5,
        coastal=False,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
        slope=10.5,
        rainfall_mm_imputed=False,
        temperature_celsius_imputed=False,
        elevation_m_imputed=False,
        ph_imputed=True,
        slope_imputed=False,
    )

    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    farm_id = farm.id

    updated = await update_farm_record(
        db=async_session,
        farm_id=farm_id,
        farm_data=FarmUpdate(ph=6.2),
    )

    assert updated is not None
    assert float(updated.ph) == 6.2
    assert updated.ph_imputed is True
