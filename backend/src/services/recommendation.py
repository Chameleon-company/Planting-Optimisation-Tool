from collections import defaultdict
from datetime import datetime, timezone

from exclusion_rules.exclusion_core_logic import run_exclusion_rules
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from suitability_scoring import (
    build_rules_dict,
    build_species_params_dict,
    build_species_recommendations,
    calculate_suitability,
)

from src.domains.suitability_scoring import SuitabilityFarm
from src.models.exclusion_rules import SpeciesDependency, SpeciesExclusionRule
from src.models.recommendations import Recommendation
from src.services.species import get_species_by_ids
from src.services.species_parameters import get_species_parameters_as_dicts


async def run_recommendation_pipeline(db: AsyncSession, farms, all_species, cfg):
    # Pre-calculate suitability rules
    # Get species (over-ride) parameters from database
    species_params_rows = await get_species_parameters_as_dicts(db)
    params_dict = build_species_params_dict(species_params_rows, cfg)
    optimised_rules = build_rules_dict(all_species, params_dict, cfg)

    # This is here to allow exclusion to be disabled if scoring without exclusion is wanted
    enable_exclusion = cfg.get("enable_exclusions", True)

    # Fetch all exclusion rules from the database in one go, to avoid multiple queries inside the loop.
    rules_from_db = await db.execute(select(SpeciesExclusionRule))
    dep_from_db = await db.execute(select(SpeciesDependency))

    # In initialise to empty dict if exclusion is disabled, to avoid unnecessary processing in the loop.
    rules_lookup = defaultdict(list)
    dep_lookup = defaultdict(list)

    if enable_exclusion:
        # Organise rules by species_id for quick lookup during the farm loop

        for r in rules_from_db.scalars().all():
            rules_lookup[r.species_id].append(r)

        # Group by focal_species_id for lookup during the loop
        for d in dep_from_db.scalars().all():
            dep_lookup[d.focal_species_id].append(d.required_partner_id)

    # Get timestamp of execution
    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    batch_results = []

    for f in farms:
        # Nested transaction (SAVEPOINT). Safe regardless of outer transaction
        # If something fails for one farm, it rolls back just that farm’s changes, not others.
        async with db.begin_nested():  # outer transaction is open so cannot use db.begin()
            # Remove prior recommendations for this farm
            await db.execute(delete(Recommendation).where(Recommendation.farm_id == f.id))

            # Using the domain model
            farm_profile = SuitabilityFarm.from_db_model(f)

            # Determine which trees are valid candidates vs excluded
            exclusions = run_exclusion_rules(farm_profile, all_species, rules_lookup, dep_lookup)

            # Get species information from database
            candidate_species = await get_species_by_ids(db, exclusions["candidate_ids"])

            # Run the engine and compute fresh recommendations
            result_list, _ = calculate_suitability(
                farm_data=farm_profile,
                species_list=candidate_species,
                optimised_rules=optimised_rules,
                cfg=cfg,
            )

            # Create formatted recommendations
            formatted_recs = build_species_recommendations(result_list)

            # Insert new set of recommendations
            new_db_recs = []
            for rec in formatted_recs:
                db_rec = Recommendation(
                    farm_id=f.id,
                    species_id=rec["species_id"],
                    rank_overall=rec["rank_overall"],
                    score_mcda=rec["score_mcda"],
                    key_reasons=rec["key_reasons"],
                )
                new_db_recs.append(db_rec)

            # Excluded species are stored as recommendation with a rank=-1 and a score=-1
            for rec in exclusions["excluded_species"]:
                db_rec = Recommendation(
                    farm_id=f.id,
                    species_id=rec["id"],
                    rank_overall=-1,
                    score_mcda=-1,
                    key_reasons=rec["reasons"],
                )
                new_db_recs.append(db_rec)

            # Append to the output
            batch_results.append(
                {
                    "farm_id": f.id,
                    "timestamp_utc": timestamp_utc,
                    "recommendations": formatted_recs,
                    "excluded_species": exclusions["excluded_species"],
                }
            )

            if new_db_recs:
                db.add_all(new_db_recs)

    # No outer transaction managing the commit, commit here.
    await db.commit()

    return batch_results
