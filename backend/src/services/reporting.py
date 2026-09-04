from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domains.reporting import FarmReportContract, FarmReportMetadata, RecommendationReportEntry, SaplingReportSummary
from src.models.farm import Farm
from src.models.recommendations import Recommendation
from src.services import farm as farm_service
from src.services.sapling_estimation import SaplingEstimationService

# Intended to match DEFAULT_CALC_PARAMS in frontend/src/hooks/useCalculator.ts,
# so report sapling numbers match what a user would see running the calculator
# themselves. There is no shared backend source of truth for these values yet,
# both sides hardcode them independently, so keep this comment and that file
# in sync manually if either default ever changes.
DEFAULT_SPACING_X = 3.0
DEFAULT_SPACING_Y = 3.0
DEFAULT_MAX_SLOPE = 15.0


async def get_farm_report(db: AsyncSession, farm_id: int, user_id: int | None = None) -> FarmReportContract | None:
    """Retrieves a farm and its saved recommendations by farm_id.
    Returns None if the farm does not exist or the user does not have access.
    """
    stmt = select(Farm).options(selectinload(Farm.soil_texture), selectinload(Farm.farm_supervisor)).where(Farm.id == farm_id)
    if user_id is not None:
        stmt = stmt.where(Farm.user_id == user_id)
    farm_result = await db.execute(stmt)
    farm = farm_result.scalar_one_or_none()

    if farm is None:
        return None

    recs_result = await db.execute(
        select(Recommendation).options(selectinload(Recommendation.species)).where(Recommendation.farm_id == farm_id).where(Recommendation.rank_overall >= 0).order_by(Recommendation.rank_overall)
    )
    recommendations = list(recs_result.scalars().all())

    excl_result = await db.execute(select(Recommendation).options(selectinload(Recommendation.species)).where(Recommendation.farm_id == farm_id).where(Recommendation.rank_overall == -1))
    exclusions = list(excl_result.scalars().all())

    report = _assemble_report(farm, recommendations, exclusions)

    boundary = await farm_service.get_farm_boundary(db, farm.id)
    sapling = await _build_sapling_summary(db, farm.id) if boundary is not None else None
    planting_guidance = _build_planting_guidance(report.recommendations, sapling)

    return report.model_copy(update={"boundary": boundary, "sapling": sapling, "planting_guidance": planting_guidance})


async def get_all_farms_report(db: AsyncSession, user_id: int | None = None) -> list[FarmReportContract]:
    """Retrieves all farms and their saved recommendations.
    If user_id is provided, only farms belonging to that user are included.
    """
    farm_stmt = select(Farm).options(selectinload(Farm.soil_texture), selectinload(Farm.farm_supervisor))
    # Admins see all farms, supervisors see only their own
    if user_id is not None:
        farm_stmt = farm_stmt.where(Farm.user_id == user_id)

    farm_result = await db.execute(farm_stmt)
    farms = list(farm_result.scalars().all())

    reports = []
    for farm in farms:
        recs_result = await db.execute(
            select(Recommendation).options(selectinload(Recommendation.species)).where(Recommendation.farm_id == farm.id).where(Recommendation.rank_overall >= 0).order_by(Recommendation.rank_overall)
        )
        recommendations = list(recs_result.scalars().all())

        excl_result = await db.execute(select(Recommendation).options(selectinload(Recommendation.species)).where(Recommendation.farm_id == farm.id).where(Recommendation.rank_overall == -1))
        exclusions = list(excl_result.scalars().all())

        reports.append(_assemble_report(farm, recommendations, exclusions))

    return reports


def _assemble_report(farm: Farm, recommendations: list[Recommendation], exclusions: list[Recommendation]) -> FarmReportContract:
    """Builds the base report contract from farm and recommendation data.

    Deliberately does not fetch the boundary or run sapling estimation here:
    this is also used by get_all_farms_report, which can return every farm in
    the system, and per-farm boundary/DEM lookups at that scale are too
    expensive to run in a loop. Only get_farm_report (a single farm) enriches
    the contract with that data after calling this.
    """
    farm_metadata = FarmReportMetadata(
        id=farm.id,
        user_name=farm.farm_supervisor.name,
        rainfall_mm=farm.rainfall_mm,
        temperature_celsius=farm.temperature_celsius,
        elevation_m=farm.elevation_m,
        ph=farm.ph,
        soil_texture=farm.soil_texture.name,
        area_ha=farm.area_ha,
        latitude=farm.latitude,
        longitude=farm.longitude,
    )

    recs = [
        RecommendationReportEntry(
            species_id=r.species_id,
            species_name=r.species.name,
            species_common_name=r.species.common_name,
            rank_overall=r.rank_overall,
            score_mcda=r.score_mcda,
            key_reasons=r.key_reasons,
        )
        for r in recommendations
    ]

    excl = [
        RecommendationReportEntry(
            species_id=r.species_id,
            species_name=r.species.name,
            species_common_name=r.species.common_name,
            rank_overall=r.rank_overall,
            score_mcda=r.score_mcda,
            key_reasons=r.key_reasons,
        )
        for r in exclusions
    ]

    return FarmReportContract(
        farm=farm_metadata,
        recommendations=recs,
        exclusions=excl,
        generated_at=datetime.now(timezone.utc),
    )


async def _build_sapling_summary(db: AsyncSession, farm_id: int) -> SaplingReportSummary | None:
    """Runs the sapling estimation for a single farm using the product's default
    spacing and slope settings. Returns None if the estimation could not run
    (e.g. no DEM coverage for the farm's location).

    Runs with persist=False: viewing a report must never overwrite the farm's
    saved PlantingEstimate records, since the report always uses the default
    spacing/slope regardless of what the farm's actual calculator grid used.
    """
    result = await SaplingEstimationService().run_estimation(
        db,
        farm_ids=[farm_id],
        spacing_x=DEFAULT_SPACING_X,
        spacing_y=DEFAULT_SPACING_Y,
        max_slope=DEFAULT_MAX_SLOPE,
        persist=False,
    )
    items = result.get("results", [])
    if not items or items[0].get("status") != "success":
        return None

    item = items[0]
    return SaplingReportSummary(
        aligned_count=item.get("aligned_count"),
        baseline_tree_count=item.get("baseline_tree_count"),
        additional_sapling_count=item.get("additional_sapling_count"),
    )


def _build_planting_guidance(recommendations: list[RecommendationReportEntry], sapling: SaplingReportSummary | None) -> str | None:
    """Builds a short planting guidance sentence from the top recommendation and sapling capacity."""
    if not recommendations:
        return "No suitable species were identified for this farm's current conditions."

    top = recommendations[0]
    guidance = f"Plant {top.species_name} ({top.species_common_name}) first, it is the highest-ranked match for this farm's conditions."

    if sapling is not None and sapling.additional_sapling_count is not None:
        guidance += f" This farm has capacity for {sapling.additional_sapling_count} additional saplings at {DEFAULT_SPACING_X:g}m x {DEFAULT_SPACING_Y:g}m spacing"
        if sapling.baseline_tree_count:
            guidance += f", alongside its {sapling.baseline_tree_count} existing trees."
        else:
            guidance += "."

    return guidance
