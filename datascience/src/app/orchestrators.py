import timeit
from datetime import datetime, timezone
from app import repository

from suitability_scoring.scoring.scoring import calculate_suitability
from suitability_scoring.utils.params import build_rules_dict
from suitability_scoring.recommend import build_species_recommendations


########################################################################################
# Exclusion Logic (Service Level)
########################################################################################
def get_valid_tree_ids_and_reasons(farm_data, species_list):
    """
    Apply hard exclusion rules to determine which trees are valid candidates.

    :param farm_data: Dictionary of farm features.
    :param species_list: List of dictionaries (species profile), each representing a valid
     candidate species.
    :returns: Tuple (valid_ids_list, excluded_records_list)
    """
    valid_ids = list(range(1, 21))
    return valid_ids, []


########################################################################################
# Service Orchestrators
########################################################################################
def get_batch_recommendations_service(farm_id_list):
    """
    This function acts as an orchestration layer that combines upstream exclusion logic
    with a weighted Multi-Criteria Decision Analysis (MCDA) scoring engine. The function
    returns a list of payloads, one per farm_id (in the order provided).

    Overview
    The function iterates through every farm in in the provided list of ids. For each farm,
    it retrieves a shortlist of candidate species and evaluates them feature-by-feature. Unlike
    vectorized operations, this iterative approach allows for species-specific parameter
    overrides (via `params_index`) and generates detailed textual explanations for every
    scoring decision.

    Exclusion Logic
    Before scoring, the function invokes `get_valid_tree_ids_and_reasons` to retrieve a
    list of viable species IDs for the current farm. Only these "valid" species are passed
    to the scoring engine.

    Output example:
      [
        { 'farm_id': 1, 'timestamp_utc': '...', 'recommendations': [...], 'excluded_species' : [...]},
        { 'farm_id': 2, 'timestamp_utc': '...', 'recommendations': [...], 'excluded_species' : [...]},
        ...
      ]

    :param farm_id_list: List of farm IDs to process
    :returns: List of JSON-ready payload dictionaries
    """
    # Fetch species parameter overrides
    params = repository.get_params_dict()

    # Fetch configuration dictionary
    cfg = repository.get_config()

    species_id_col = cfg.get("ids", {}).get("species", "id")

    # Fetch species data from repository (list of dicts)
    all_species = repository.get_all_species()

    # Create a map for quick lookups during exclusion/formatting
    all_species_map = {sp[species_id_col]: sp for sp in all_species}

    # Fetch all requested farms
    farms_data_list = repository.get_farms_by_ids(farm_id_list)

    results = []

    # Build dictionary of rules for optimisation
    optimised_rules = build_rules_dict(all_species, params, cfg)

    # Calculate start time
    start = timeit.default_timer()

    # Process each farm one by one
    for farm_data in farms_data_list:
        farm_id = farm_data.get(cfg["ids"]["farm"])

        # EXCLUSION GOES HERE
        # Determine which trees are valid candidates vs excluded
        candidate_species_ids, excluded_results = get_valid_tree_ids_and_reasons(
            farm_data, all_species
        )

        # If candidate_species_ids is not empty, create candidate list
        if candidate_species_ids:
            # Filter the master list to create a candidate list for this farm
            candidate_species = [
                all_species_map[sp_id]
                for sp_id in candidate_species_ids
                if sp_id in all_species_map
            ]

        # Score these candidate species for this farm
        scored_results, _ = calculate_suitability(
            farm_data, candidate_species, optimised_rules, cfg
        )

        # Format recommendations and rank
        formatted_recs = build_species_recommendations(scored_results)

        # Get timestamp of execution
        timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Add to batch results
        results.append(
            {
                "farm_id": farm_id,
                "timestamp_utc": timestamp_utc,
                "recommendations": formatted_recs,
                "excluded_species": excluded_results,
            }
        )

    # Calculate Stop time
    stop = timeit.default_timer()
    exec_time = stop - start
    print(f"Time taken: {exec_time}")

    # Return the results list
    return results


def get_recommendations_service(farm_id):
    """
    Returns a JSON-ready payload for ONE farm_id:
      {
        'farm_id': <farm_id>,
        'timestamp_utc': <iso8601>,
        'recommendations': [...],
        'excluded_species' : [...]
      }

    :param farm_id: Id for farm to build payload for.
    :returns: JSON-ready dictionary
    """
    batch_result = get_batch_recommendations_service([farm_id])

    return batch_result[0]
