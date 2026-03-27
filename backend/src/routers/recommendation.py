from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

# Project Imports
from src.database import get_db_session
from src.dependencies import get_user_id, limiter, require_role
from src.schemas.user import Role, UserRead
from src.services import farm as farm_service
from src.services import recommendation as recommendation_service
from src.services import species as species_service

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{farm_id}")
@limiter.limit("10/minute", key_func=get_user_id)
async def get_farm_recs(
    request: Request,
    farm_id: int,
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves species recommendations for a farm, verifying ownership.
    Requires OFFICER role or higher.
    """
    if current_user.role == Role.OFFICER:
        user_id_filter = current_user.id
    else:
        user_id_filter = None

    farms = await farm_service.get_farm_by_id(db, [farm_id], user_id=user_id_filter)

    if not farms:
        raise HTTPException(status_code=404, detail="Farm not found or access denied")

    # Prepare data for the engine
    all_species = await species_service.get_all_species_for_engine(db)
    cfg = species_service.get_recommend_config()

    # Run the pipeline
    results = await recommendation_service.run_recommendation_pipeline(db, farms, all_species, cfg)

    return results[0]


@router.post("/batch")
@limiter.limit("10/minute", key_func=get_user_id)
async def get_batch_recs(
    request: Request,
    farm_ids: list[int],  # Expects JSON body like [1, 2, 3]
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves species recommendations for multiple farms in batch.
    Requires OFFICER role or higher.
    """
    if current_user.role == Role.OFFICER:
        user_id_filter = current_user.id
    else:
        user_id_filter = None

    farms = await farm_service.get_farm_by_id(db, farm_ids, user_id=user_id_filter)

    if not farms:
        raise HTTPException(status_code=404, detail="No valid farms found")

    all_species = await species_service.get_all_species_for_engine(db)
    cfg = species_service.get_recommend_config()

    # Process all at once
    return await recommendation_service.run_recommendation_pipeline(db, farms, all_species, cfg)
