from sqlalchemy.ext.asyncio import AsyncSession
from suitability_scoring import (
    build_rules_dict,
    build_species_params_dict,
    calculate_suitability,
)

from src.domains.suitability_scoring import SuitabilityFarm
from src.services.farm import get_farm_by_id
from src.services.species import get_species_by_ids
from src.services.species_parameters import get_species_parameters_as_dicts


async def get_raw_scores(
    db: AsyncSession,
    farm_id_list: list[int],
    cfg: dict,
    target_species_ids: list[int] | None = None,
):
    """
    Service-layer orchestrator to compute raw feature scores
    for a batch of farms and species.

    Returns raw (per-feature) scores without exclusions,
    ranking, or persistence.

    Used for determining global weights.
    """
    # === Fetch configuration-dependent inputs =========================================

    # Species parameters (override / defaults)
    species_params_rows = await get_species_parameters_as_dicts(db)
    params_dict = build_species_params_dict(species_params_rows, cfg)

    # Species list
    if target_species_ids:
        species_to_score = await get_species_by_ids(db, target_species_ids)
    else:
        species_to_score = await get_species_by_ids(db)  # or get_all_species()

    # Build rules ONCE
    optimised_rules = build_rules_dict(
        species_to_score,
        params_dict,
        cfg,
        global_weights=None,  # We don't use the MCDA so this can be None
    )

    # === Fetch farms ==================================================================
    farms = await get_farm_by_id(db, farm_id_list)

    # === Scoring per farm to get raw scores ===========================================
    all_raw_scores = []

    for f in farms:
        # Convert DB model → domain model
        farm_profile = SuitabilityFarm.from_db_model(f)

        # Score species list against this farm
        _, farm_scores = calculate_suitability(
            farm_data=farm_profile,
            species_list=species_to_score,
            optimised_rules=optimised_rules,
            cfg=cfg,
        )

        all_raw_scores.extend(farm_scores)

    return all_raw_scores
