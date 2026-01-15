from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# Project Imports
from src.database import get_db_session
from src.dependencies import CurrentActiveUser
from src.services.farm import get_farm_by_id
from src.services.species import get_all_species_for_engine, get_recommend_config
from src.services.recommendation import run_recommendation_pipeline
from src.schemas.user import UserRead

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{farm_id}")
async def get_farm_recs(
    farm_id: int,
    current_user: UserRead = CurrentActiveUser,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Endpoint to get species recommendations for a specific farm.
    """
    # Fetch the farm and verify ownership
    # Pass current_user (which is a UserRead schema) to the service
    farm = await get_farm_by_id(db, farm_id, current_user.id)

    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found or access denied")

    # Prepare data for the engine
    all_species = await get_all_species_for_engine(db)
    cfg = get_recommend_config()

    # Run the pipeline
    results = await run_recommendation_pipeline(db, [farm], all_species, cfg)

    return results[0]
