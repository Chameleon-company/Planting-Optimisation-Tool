"""Integration tests for the Backend → Data Science recommendation pipeline (US-065)."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.farm import Farm
from src.models.recommendations import Recommendation
from src.models.soil_texture import SoilTexture
from src.models.species import Species
from src.models.user import User
from src.services import recommendation as recommendation_service
from src.services.species import get_all_species_for_engine, get_recommend_config

_FARM_PROFILE = {
    "rainfall_mm": 1500,
    "temperature_celsius": 22,
    "elevation_m": 500,
    "ph": 6.5,
    "soil_texture_id": 1,
    "area_ha": 5.0,
    "latitude": -8.5,
    "longitude": 126.5,
    "coastal": False,
    "riparian": False,
    "nitrogen_fixing": False,
    "shade_tolerant": False,
    "bank_stabilising": False,
    "slope": 10.0,
}

_SPECIES_IN_RANGE = {
    "name": "Tectona grandis",
    "common_name": "Teak",
    "rainfall_mm_min": 1000,
    "rainfall_mm_max": 2000,
    "temperature_celsius_min": 18,
    "temperature_celsius_max": 30,
    "elevation_m_min": 0,
    "elevation_m_max": 1000,
    "ph_min": 5.0,
    "ph_max": 8.0,
    "coastal": False,
    "riparian": False,
    "nitrogen_fixing": False,
    "shade_tolerant": False,
    "bank_stabilising": False,
}


async def _load_farm_with_relationships(db: AsyncSession, farm_id: int) -> Farm:
    """Load a farm with the relationships required by SuitabilityFarm.from_db_model."""
    result = await db.execute(select(Farm).options(selectinload(Farm.soil_texture), selectinload(Farm.agroforestry_type)).where(Farm.id == farm_id))
    return result.scalar_one()


@pytest.fixture
async def pipeline_species(async_session: AsyncSession, setup_soil_texture):
    """Seeds a species compatible with _FARM_PROFILE, associated with soil texture id=1."""
    result = await async_session.execute(select(SoilTexture).where(SoilTexture.id == 1))
    loam = result.scalar_one()

    species = Species(**_SPECIES_IN_RANGE)
    species.soil_textures = [loam]
    async_session.add(species)
    await async_session.flush()
    return species


# ---- Output structure tests ----


async def test_pipeline_returns_one_result_per_farm(
    async_session: AsyncSession,
    test_officer_user: User,
    pipeline_species: Species,
):
    """Pipeline returns exactly one result dict per farm passed in."""
    farm = Farm(**_FARM_PROFILE, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()

    farm_with_rels = await _load_farm_with_relationships(async_session, farm.id)
    all_species = await get_all_species_for_engine(async_session)
    cfg = get_recommend_config()

    results = await recommendation_service.run_recommendation_pipeline(async_session, [farm_with_rels], all_species, cfg)

    assert len(results) == 1


async def test_pipeline_result_contains_required_keys(
    async_session: AsyncSession,
    test_officer_user: User,
    pipeline_species: Species,
):
    """Each pipeline result contains farm_id, timestamp_utc, recommendations, and excluded_species."""
    farm = Farm(**_FARM_PROFILE, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()

    farm_with_rels = await _load_farm_with_relationships(async_session, farm.id)
    all_species = await get_all_species_for_engine(async_session)
    cfg = get_recommend_config()

    results = await recommendation_service.run_recommendation_pipeline(async_session, [farm_with_rels], all_species, cfg)

    result = results[0]
    assert result["farm_id"] == farm.id
    assert "timestamp_utc" in result
    assert "recommendations" in result
    assert "excluded_species" in result


async def test_pipeline_recommendation_fields_and_types(
    async_session: AsyncSession,
    test_officer_user: User,
    pipeline_species: Species,
):
    """Each recommendation entry has the required fields with correct types."""
    farm = Farm(**_FARM_PROFILE, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()

    farm_with_rels = await _load_farm_with_relationships(async_session, farm.id)
    all_species = await get_all_species_for_engine(async_session)
    cfg = get_recommend_config()

    results = await recommendation_service.run_recommendation_pipeline(async_session, [farm_with_rels], all_species, cfg)

    recommendations = results[0]["recommendations"]
    assert len(recommendations) > 0

    for rec in recommendations:
        assert "species_id" in rec
        assert "rank_overall" in rec
        assert "score_mcda" in rec
        assert "key_reasons" in rec
        assert isinstance(rec["species_id"], int)
        assert isinstance(rec["rank_overall"], int)
        assert isinstance(rec["score_mcda"], float)
        assert isinstance(rec["key_reasons"], list)


async def test_pipeline_farm_id_matches_input(
    async_session: AsyncSession,
    test_officer_user: User,
    pipeline_species: Species,
):
    """The farm_id in each result matches the corresponding input farm."""
    farm = Farm(**_FARM_PROFILE, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()

    farm_with_rels = await _load_farm_with_relationships(async_session, farm.id)
    all_species = await get_all_species_for_engine(async_session)
    cfg = get_recommend_config()

    results = await recommendation_service.run_recommendation_pipeline(async_session, [farm_with_rels], all_species, cfg)

    assert results[0]["farm_id"] == farm.id


# ---- Behaviour tests ----


async def test_pipeline_with_no_species_returns_empty_recommendations(
    async_session: AsyncSession,
    test_officer_user: User,
    setup_soil_texture,
):
    """Pipeline returns empty recommendations and excluded_species when given an empty species list."""
    farm = Farm(**_FARM_PROFILE, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()

    farm_with_rels = await _load_farm_with_relationships(async_session, farm.id)
    cfg = get_recommend_config()

    results = await recommendation_service.run_recommendation_pipeline(async_session, [farm_with_rels], [], cfg)

    assert results[0]["recommendations"] == []
    assert results[0]["excluded_species"] == []


async def test_pipeline_persists_recommendations_to_database(
    async_session: AsyncSession,
    test_officer_user: User,
    pipeline_species: Species,
):
    """Pipeline writes Recommendation records to the database after running."""
    farm = Farm(**_FARM_PROFILE, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()

    farm_with_rels = await _load_farm_with_relationships(async_session, farm.id)
    all_species = await get_all_species_for_engine(async_session)
    cfg = get_recommend_config()

    await recommendation_service.run_recommendation_pipeline(async_session, [farm_with_rels], all_species, cfg)

    saved = await async_session.execute(select(Recommendation).where(Recommendation.farm_id == farm.id))
    records = saved.scalars().all()
    assert len(records) > 0


async def test_pipeline_replaces_existing_recommendations_on_rerun(
    async_session: AsyncSession,
    test_officer_user: User,
    pipeline_species: Species,
):
    """Running the pipeline twice for the same farm replaces old recommendations without duplicating them."""
    farm = Farm(**_FARM_PROFILE, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()

    all_species = await get_all_species_for_engine(async_session)
    cfg = get_recommend_config()

    farm_with_rels = await _load_farm_with_relationships(async_session, farm.id)
    await recommendation_service.run_recommendation_pipeline(async_session, [farm_with_rels], all_species, cfg)

    farm_with_rels = await _load_farm_with_relationships(async_session, farm.id)
    await recommendation_service.run_recommendation_pipeline(async_session, [farm_with_rels], all_species, cfg)

    saved = await async_session.execute(select(Recommendation).where(Recommendation.farm_id == farm.id))
    records = saved.scalars().all()
    species_ids = [r.species_id for r in records]
    assert len(species_ids) == len(set(species_ids)), "No duplicate recommendations per farm after rerun"


async def test_pipeline_batch_returns_result_per_farm(
    async_session: AsyncSession,
    test_officer_user: User,
    pipeline_species: Species,
):
    """Pipeline processes multiple farms in a batch and returns one result per farm."""
    farm1 = Farm(**_FARM_PROFILE, user_id=test_officer_user.id)
    farm2 = Farm(**_FARM_PROFILE, user_id=test_officer_user.id)
    async_session.add_all([farm1, farm2])
    await async_session.flush()

    farms = [
        await _load_farm_with_relationships(async_session, farm1.id),
        await _load_farm_with_relationships(async_session, farm2.id),
    ]
    all_species = await get_all_species_for_engine(async_session)
    cfg = get_recommend_config()

    results = await recommendation_service.run_recommendation_pipeline(async_session, farms, all_species, cfg)

    assert len(results) == 2
    result_farm_ids = {r["farm_id"] for r in results}
    assert farm1.id in result_farm_ids
    assert farm2.id in result_farm_ids
