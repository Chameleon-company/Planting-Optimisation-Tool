from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime

class ReportSpeciesItem(BaseModel):
    species_id: Optional[int] = None
    species_name: Optional[str] = None
    score: Optional[float] = None
    limiting_factors: List[str] = []
    image_url: Optional[str] = None
    extra: Dict[str, Any] = {}

class FarmReportResponse(BaseModel):
    farm_id: int
    generated_at: datetime
    suitable_species: List[ReportSpeciesItem] = []
    cautionary_species: List[ReportSpeciesItem] = []
    excluded_species: List[ReportSpeciesItem] = []
    limiting_factors_summary: List[str] = []
    sapling_estimate: Dict[str, Any] = {}

