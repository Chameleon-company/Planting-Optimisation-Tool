from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.suitability_scoring import SuitabilityFarm
from src.services.species import get_species_by_ids, get_exclusion_config
from src.services.species_parameters import get_species_parameters_as_dicts
from suitability_scoring import (
    calculate_suitability,
    build_species_params_dict,
    build_rules_dict,
    build_species_recommendations,
)
from exclusion_rules.exclusion_core_logic import run_exclusion_rules_records
from exclusion_rules.dummy_run import run_exclusion_rules
from src.models.recommendations import Recommendation


async def run_recommendation_pipeline(db: AsyncSession, farms, all_species, cfg):
    # TODO: still need to convert Species objects to dicts for the DS engine until it accepts objects.
    species_dicts = [s.model_dump() for s in all_species]

    # Pre-calculate rules
    # Get species (over-ride) parameters from database
    species_params_rows = await get_species_parameters_as_dicts(db)
    params_dict = build_species_params_dict(species_params_rows, cfg)
    optimised_rules = build_rules_dict(species_dicts, params_dict, cfg)

    # Select the exclusion function
    # Place here and not in the recommendation router because this config file should
    # be merged with the recommendation config file
    exclusion_cfg = get_exclusion_config()

    enable_exclusion = cfg.get("enable_exclusions", True)
    exclusion_runner = (
        run_exclusion_rules_records if enable_exclusion else run_exclusion_rules
    )

    # Get timestamp of execution
    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    batch_results = []
    all_db_recs = []

    for f in farms:
        # Using the domain model
        farm_profile = SuitabilityFarm.from_db_model(f)

        # Determine which trees are valid candidates vs excluded
        exclusions = exclusion_runner(
            farm_profile.model_dump(), species_dicts, exclusion_cfg
        )

        # Get species information from database
        candidate_species = await get_species_by_ids(db, exclusions["candidate_ids"])
        candidate_species_dicts = [s.model_dump() for s in candidate_species]

        # Run the engine
        result_list, _ = calculate_suitability(
            farm_data=farm_profile.model_dump(),
            species_list=candidate_species_dicts,
            optimised_rules=optimised_rules,
            cfg=cfg,
        )

        formatted_recs = build_species_recommendations(result_list)
        for rec in formatted_recs:
            db_rec = Recommendation(
                farm_id=f.id,
                species_id=rec["species_id"],
                rank_overall=rec["rank_overall"],
                score_mcda=rec["score_mcda"],
                key_reasons=rec["key_reasons"],
                # exclusions=rec.get("exclusions", []) # Not completed
            )
            all_db_recs.append(db_rec)
        batch_results.append(
            {
                "farm_id": f.id,
                "timestamp_utc": timestamp_utc,
                "recommendations": formatted_recs,
                "excluded_species": exclusions["excluded_species"],
            }
        )

    if all_db_recs:
        db.add_all(all_db_recs)
        await db.commit()
    return batch_results
