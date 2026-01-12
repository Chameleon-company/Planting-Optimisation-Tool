from fastapi import APIRouter
from datetime import datetime
from src.schemas.report import FarmReportResponse

router = APIRouter(tags=["Report"])

@router.get("/report/{farm_id}", response_model=FarmReportResponse)
def get_report(farm_id: int):
    # Stub for now (we’ll connect real recommendation outputs next)
    return FarmReportResponse(
        farm_id=farm_id,
        generated_at=datetime.utcnow(),
        suitable_species=[],
        cautionary_species=[],
        excluded_species=[],
        limiting_factors_summary=[],
        sapling_estimate={}
    )

