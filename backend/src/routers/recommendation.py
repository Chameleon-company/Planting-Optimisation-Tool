from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# Project Imports
from src.database import get_db_session
from src.schemas.user import Role, UserRead
from src.services.authentication import require_role
from src.services.farm import get_farm_by_id
from src.services.species import get_all_species_for_engine, get_recommend_config
from src.services.recommendation import run_recommendation_pipeline


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{farm_id}")
async def get_farm_recs(
    farm_id: int,
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieves species recommendations for a farm, verifying ownership.
    Requires OFFICER role or higher.
    """
    # Fetch the farm and verify ownership
    # Pass current_user (which is a UserRead schema) to the service
    farms = await get_farm_by_id(
        db, [farm_id], current_user.id, user_role=current_user.role
    )

    if not farms:
        raise HTTPException(status_code=404, detail="Farm not found or access denied")

    # Prepare data for the engine
    all_species = await get_all_species_for_engine(db)
    cfg = get_recommend_config()

    # Run the pipeline
    results = await run_recommendation_pipeline(db, farms, all_species, cfg)

    return results[0]


@router.post("/batch")
async def get_batch_recs(
    farm_ids: list[int],  # Expects JSON body like [1, 2, 3]
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieves species recommendations for multiple farms in batch.
    Requires OFFICER role or higher.
    """
    farms = await get_farm_by_id(
        db, farm_ids, current_user.id, user_role=current_user.role
    )

    if not farms:
        raise HTTPException(status_code=404, detail="No valid farms found")

    all_species = await get_all_species_for_engine(db)
    cfg = get_recommend_config()

    # Process all at once
    return await run_recommendation_pipeline(db, farms, all_species, cfg)
