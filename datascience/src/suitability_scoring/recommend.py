import timeit
from datetime import datetime, timezone

from suitability_scoring import repository
from suitability_scoring.scoring.scoring import calculate_suitability
from suitability_scoring.utils.params import build_rules_dict


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
    valid_ids = list(range(0, 2))
    return valid_ids, []


########################################################################################
# Ranking & Formatting (Presentation Logic)
########################################################################################
def assign_dense_ranks(sorted_items, score_key="mcda_score"):
    """
    Function to assign dense ranks for handling ties to the recommended species.
    Dense ranking provides ranking with no gaps.

    Example:
      Scores [0.82, 0.76, 0.76, 0.70] -> Ranks [1, 2, 2, 3]

    :param sorted_items: Sorted recommendations.
    :param score_key: Key to sort on.
    :returns: List of ranks
    """
    ranks = []
    last_score = None
    current_rank = 0
    for item in sorted_items:
        score = item.get(score_key, 0)
        if score != last_score:
            current_rank += 1
            last_score = score
        ranks.append(current_rank)
    return ranks


def build_species_recommendations(species_list):
    """
    Function to take a list of species with scores and explanations and
    return a list of dictionaries ordered by the highest score.

    :param species_list: List of dictionaries.
    :returns: List of dictionaries ordered by the highest weighted score.
    """
    # Primary: total_score (desc), Secondary: species_id (asc)
    ranked = sorted(
        species_list, key=lambda x: (-x.get("mcda_score", 0), x.get("species_id", 0))
    )

    # Add tie breaking policy
    dense_ranks = assign_dense_ranks(ranked)

    # Create empty list to hold recommendations
    recommendations = []

    # Loop over each specie
    for idx, sp in enumerate(ranked):
        # Get dictionary of features for current specie
        features = sp.get("features", {}) or {}

        # Create an empty list for the key reasons for the current specie
        key_reasons = []

        # Loop over each feature
        for feature_val in features.values():
            # Get the reason for the feature score
            reason = feature_val.get("reason").lower()

            # Get the short name for the feature
            short = feature_val.get("short_name")

            # Add the reason to the key reasons for this specie
            key_reasons.append(f"{short}:{reason}")

        # Append a dictionary to hold the specie specific information
        recommendations.append(
            {
                "species_id": sp.get("species_id"),
                "species_name": sp.get("species_name", "missing"),
                "species_common_name": sp.get("species_common_name", "missing"),
                "score_mcda": round(sp.get("mcda_score", 0), 3),
                "rank_overall": dense_ranks[idx],
                "key_reasons": key_reasons,
            }
        )
    return recommendations


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
