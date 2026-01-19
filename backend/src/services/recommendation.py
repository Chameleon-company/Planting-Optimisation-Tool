from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.suitability_scoring import SuitabilityFarm
from src.services.species_parameters import get_species_parameters_as_dicts
from suitability_scoring import (
    calculate_suitability,
    build_species_params_dict,
    build_rules_dict,
    build_species_recommendations,
)
from src.models.recommendations import Recommendation


async def run_recommendation_pipeline(db: AsyncSession, farms, all_species, cfg):
    # TODO: still need to convert Species objects to dicts for the DS engine until it accepts objects.
    species_dicts = [s.model_dump() for s in all_species]

    # Pre-calculate rules
    # Get species (over-ride) parameters from database
    species_params_rows = await get_species_parameters_as_dicts(db)
    params_dict = build_species_params_dict(species_params_rows, cfg)
    optimised_rules = build_rules_dict(species_dicts, params_dict, cfg)

    batch_results = []
    all_db_recs = []

    for f in farms:
        # Using the domain model
        farm_profile = SuitabilityFarm.from_db_model(f)

        # Run the engine
        result_list, _ = calculate_suitability(
            farm_data=farm_profile.model_dump(),
            species_list=species_dicts,
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

        batch_results.append({"farm_id": f.id, "recommendations": formatted_recs})
    if all_db_recs:
        db.add_all(all_db_recs)
        await db.commit()
    return batch_results
