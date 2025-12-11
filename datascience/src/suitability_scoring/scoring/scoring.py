import pandas as pd
from suitability_scoring.utils.params import get_feature_params
from suitability_scoring.utils.config import load_yaml
from suitability_scoring.utils.params import build_species_params_dict


########################################################################################
# Helper functions
########################################################################################
def parse_prefs(prefs_raw):
    """
    Parse preferences ensuring they are a list.

    :param prefs_raw: The raw value of the preferences read from the dataframe.
    :returns:
    """
    # If None return empty list
    if prefs_raw is None:
        return []

    # If a list then do nothing and return the original list
    if isinstance(prefs_raw, list):
        return prefs_raw

    # If a string then try to convert to a Python literal and return as a list
    if isinstance(prefs_raw, str):
        return [s.strip() for s in prefs_raw.split(",")]


########################################################################################
# Scoring functions
########################################################################################
def numerical_range_score(value, min_val, max_val):
    """
    Function for scoring numeric values within a range. Returns 1.0 if value is within
    [min_val, max_val], 0.0 if outside, None if missing.

    :param value: Farm's value of the feature.
    :param min_val: Species minimum preferred value.
    :param max_val: Species maximum preferred value.
    :returns: Score value between 0 and 1 or None.
    """
    if pd.isna(value) or pd.isna(min_val) or pd.isna(max_val):
        return None
    return 1.0 if float(min_val) <= float(value) <= float(max_val) else 0.0


def categorical_exact_score(value, preferred_list, exact_score=1.0):
    """
    Function for scoring categorical values with an exact match.
    Returns exact_score if the value is in the preferred_list, else 0.0 and None for
    missing or no preferences.

    :param val: Farm's value of the feature.
    :param preferred_list: List of preferred values.
    :param exact_score: Score to return if exact match found.
    :returns: Score value between 0 and 1 or None.
    """
    if pd.isna(value) or not preferred_list:
        return None
    return exact_score if (value in preferred_list) else 0.0


def score_farms_species_by_id_list(
    farms_df,
    species_df,
    cfg,
    get_valid_tree_ids,
    params_index,
):
    """
    This function performs a granular, non-vectorized suitability assessment to score
    specific tree species against farm profiles. This function acts as an orchestration
    layer that combines upstream exclusion logic with a weighted Multi-Criteria Decision
    Analysis (MCDA) scoring engine.

    Overview
    The function iterates through every farm in `farms_df`. For each farm, it retrieves
    a shortlist of candidate species and evaluates them feature-by-feature. Unlike
    vectorized operations, this iterative approach allows for species-specific parameter
    overrides (via `params_index`) and generates detailed textual explanations for every
    scoring decision.

    Exclusion Logic
    Before scoring, the function invokes `get_valid_tree_ids` to retrieve a list of
    viable species IDs for the current farm. Only these "valid" species are passed to
    the scoring engine. If the exclusion function returns IDs not present in `species_df`
    , they are logged as "unknown species" in the explanations output but skipped for
    scoring.

    Scoring Methodology
    Scoring is performed using a weighted arithmetic mean of individual feature scores.
    Feature behaviour is defined in `cfg['features']` and applied as follows:

    * Numerical features: Evaluated using range logic (e.g., `num_range`). A score of
        1.0 is awarded if the farm's value falls between the species' min/max
        requirements. Zero scores are assigned for values outside this range or missing
        data.

    * Categorical features: Evaluated using preference matching (e.g., `cat_exact`).
        Checks if the farm's attribute (e.g., soil texture) exists within the species'
        list of preferred types. A score of 1.0 is returned is an exact match is found
        and zero if no match is found.

    Traceability and Explanations
    In addition to the raw scores, the function generates a `explanations` dictionary.
    This structure maps every farm-species pair to a breakdown of how each feature
    contributed to the final score, including the raw values used, the specific scoring
    rule triggered (e.g., "below minimum", "exact match"), and any missing data warnings.

    :param farms_df: DataFrame with farm profile.
    :param species_df: DataFrame with tree species profile.
    :param cfg: Configuration dictionary.
    :param get_valid_tree_ids: Function to return a list of valid species per farm.
    :param params_index: Dictionary of parameters per species.
    :returns scores_df: scores for farm_id by species_id.
    :returns explanations: Dictionary of explanations for each farm_id -> list of
        species explanations
    """
    # Get dictionary of features from configuration dictionary
    features_cfg = cfg["features"]

    # Get column name for farm ids
    farm_id_col = cfg.get("ids", {}).get("farm", "farm_id")

    # Get column name for species ids
    species_id_col = cfg.get("ids", {}).get("species", "species_id")

    # Get column name for species name
    species_name_col = cfg.get("names", {}).get("species_name", "species_name")

    # Get column name for species common name
    species_cname_col = cfg.get("ids", {}).get(
        "species_common_name", "species_common_name"
    )

    # Create a dictionary for species data so we don't have to filter the dataframe every loop
    species_lookup = {row[species_id_col]: row for row in species_df.to_dict("records")}

    # Create a set of all the species ids in the species dataframe
    all_species_ids = set(species_lookup.keys())

    # Create a rules dictionary for optimisation
    # Structure: { species_id: [ (feature_key, rule_metadata, pre_calc_values), ... ] }
    optimized_rules = {}

    for sp_id, sp in species_lookup.items():
        rules_list = []

        for feat, meta in features_cfg.items():
            # Resolve overrides and defaults once
            params = get_feature_params(params_index, cfg, sp_id, feat)

            weight = params["weight"]
            score_method = params["score_method"]

            # Pack the specific data needed for scoring this feature
            rule_data = {
                "feat": feat,
                "weight": weight,
                "short_name": meta["short"],
                "type": meta["type"],
                "score_method": score_method,
            }

            if score_method == "num_range":
                min_v = sp.get(f"{feat}_min")
                max_v = sp.get(f"{feat}_max")
                rule_data["params_out"] = {"min": min_v, "max": max_v}
                rule_data["args"] = (min_v, max_v)

            elif score_method == "cat_exact":
                prefs = parse_prefs(sp.get(f"preferred_{feat}"))
                cat_cfg = meta.get("categorical", {}) or {}
                exact_score = float(cat_cfg.get("exact_match", 1.0))
                rule_data["preferred"] = prefs
                rule_data["args"] = (prefs, exact_score)

            rules_list.append(rule_data)

        optimized_rules[sp_id] = rules_list

    # Initialise results to an empty list
    results = []

    # Initialise explanation to an empty dictionary
    explanations = {}

    # Create a dictionary from dataframe
    farms_dicts = farms_df.to_dict("records")

    # Loop through all rows of the farms dataframe
    for farm in farms_dicts:
        # Get the farm id for the current farm
        farm_id = farm[farm_id_col]

        # Call the exclusion function to get the list of candidate tress for the current farm
        # return an empty list if the function returns None or is an empty list
        candidate_species_ids = get_valid_tree_ids(farm) or []

        # Create a list of id's that are in the valid_id list but not found in the species dataframe
        # This should always be empty
        unknown_ids = [id for id in candidate_species_ids if id not in all_species_ids]

        # Filter to only valid species for this farm
        valid_ids = [id for id in candidate_species_ids if id in all_species_ids]

        # Create an empty list that will hold the explanations for the current farm
        farm_explanations = []

        # Check if there are no candidate trees for this farm
        if not valid_ids:
            # Handle empty case
            if unknown_ids:
                explanations[farm_id] = [
                    {
                        "species_id": None,
                        "mcda_score": None,
                        "features": {},
                        "note": f"Exclusion function provided {len(unknown_ids)} unknown species_id(s): {unknown_ids[:5]}{'...' if len(unknown_ids) > 5 else ''}",
                    }
                ]
            else:
                explanations[farm_id] = []
            continue

        # Loop through each tree species in the filtered dataframe
        for species_id in valid_ids:
            # Get species dictionary
            sp = species_lookup[species_id]

            # Get the current species name
            species_name = sp.get(species_name_col)

            # Get the current species common name
            species_cname = sp.get(species_cname_col)

            # Create an empty dictionary to hold the scores from each feature
            feature_scores = {}

            # Create an empty dictionary to hold the explanations for each feature
            feature_explain = {}

            # Initialise the numerator score
            num_sum = 0.0

            # Initialise the denominator score
            denom = 0.0

            # Grab the pre-computer rules for this species
            rules = optimized_rules[species_id]

            # Iterate through the rules list
            for rule in rules:
                # Get feature name from rule
                feat = rule["feat"]

                # Get the farm's value for this feature
                farm_val = farm.get(feat)

                # Get scoring method for this feature
                score_method = rule["score_method"]

                # Get weight for this feature
                w = rule["weight"]

                # Numeric feature
                if rule["type"] == "numeric":
                    # Range scoring
                    if score_method == "num_range":
                        # Get minimum/maximum value for the feature
                        min_v, max_v = rule["args"]

                        # Score this feature
                        score = numerical_range_score(farm_val, min_v, max_v)

                        # Determine reason for score
                        if score == 1.0:
                            reason = "inside preferred range"

                        elif score == 0.0:
                            if farm_val < min_v:
                                reason = "below minimum"
                            else:
                                reason = "above maximum"
                        else:
                            reason = "missing data"

                    else:  # No valid scoring method selected
                        raise ValueError(
                            f"Unknown numeric scoring method '{score_method}' for '{feat}'"
                        )

                    # Store score for this feature
                    feature_scores[feat] = score

                    # Store explanation for this feature
                    feature_explain[feat] = {
                        "short_name": rule["short_name"],
                        "type": "numerical",
                        "farm_value": farm_val,
                        "score": score,
                        "reason": reason,
                        "params": rule["params_out"],
                    }

                # Categorical feature
                elif rule["type"] == "categorical":
                    # Check if the score method is for an exact categorical match
                    if score_method == "cat_exact":
                        # Get list of preferences and score for an exact match for this feature
                        prefs, exact_match_score = rule["args"]

                        # Call exact match scoring function
                        score = categorical_exact_score(
                            farm_val, prefs, exact_score=exact_score
                        )
                        if score is None:
                            reason = "missing or no preference"
                        elif score == exact_score:
                            reason = "exact match"
                        else:
                            reason = "no match"
                    else:  # No valid scoring method selected
                        raise ValueError(
                            f"Unknown categorical mode '{score_method}' for feature '{feat}'"
                        )

                    # Store score
                    feature_scores[feat] = score

                    # Store explanation
                    feature_explain[feat] = {
                        "short_name": rule["short_name"],
                        "type": "categorical",
                        "farm_value": farm_val,
                        "preferred": rule["preferred"],
                        "score": score,
                        "reason": reason,
                    }

                else:  # Feature type not numerical or categorical
                    raise ValueError(
                        f"Unknown feature type '{meta['type']}' for '{feat}'"
                    )

                # Accumulate scores for existing scores and weights
                if feature_scores[feat] is not None and w > 0:
                    num_sum += w * feature_scores[feat]
                    denom += w

            # End of feature loop
            if denom > 0:
                total_score = num_sum / denom
            else:
                total_score = 0.0

            # Append dictionary containing specie specific information
            farm_explanations.append(
                {
                    "species_id": species_id,
                    "species_name": species_name,
                    "species_common_name": species_cname,
                    "mcda_score": total_score,
                    "features": feature_explain,
                }
            )
            results.append((farm_id, species_id, total_score))

        # Attach unknown ID note if any
        if unknown_ids:
            farm_explanations.append(
                {
                    "species_id": None,
                    "mcda_score": None,
                    "features": {},
                    "note": f"Exclusion function provided {len(unknown_ids)} unknown species_id(s): {unknown_ids[:5]}{'...' if len(unknown_ids) > 5 else ''}",
                }
            )
        explanations[farm_id] = farm_explanations

    # For testing and debugging
    scores_df = pd.DataFrame(
        results, columns=[farm_id_col, species_id_col, "mcda_score"]
    )

    return scores_df, explanations


def mcda_scorer(farm_ids):
    """
    MCDA scorer:
      - non-vectorized,
      - ID-list pre-filtered exclusions,
      - per-species params

    Note this function will require updating when switching to a database.

    :param farm_ids: List of farm id's to score.
    :returns:
    """

    import timeit

    # Config variables - These could be arguments using an argparse
    # Path to farms Excel
    farms_path = "data/farms_cleaned.xlsx"

    # Path to species Excel
    species_path = "data/species.xlsx"

    # Path to species_params Excel
    species_params_path = "data/species_params.xlsx"

    # Path to YAML with defaults and feature meta
    config_path = "config/recommend.yaml"

    ## Load data
    # This will need to come from database in future

    # Load farm profile data from Excel file
    farms_df = pd.read_excel(farms_path)

    # Load species profile data from Excel file
    species_df = pd.read_excel(species_path)

    # Load species parameters
    species_params_df = pd.read_excel(species_params_path)

    # Configs
    cfg = load_yaml(config_path)

    # Build the species parameter dictionary
    params_dict = build_species_params_dict(species_params_df, cfg)

    #######################################
    ## Replace this with exclusion rules ##
    #######################################
    species_id_col = cfg.get("ids", {}).get("species", "species_id")
    all_ids = species_df[species_id_col].tolist()[::]

    def provider(farm_row):
        # Pass-through: all species IDs are valid (no upstream exclusion)
        return all_ids

    #######################################
    #######################################

    # Subset farms to only those requested
    farm_id_col = cfg.get("ids", {}).get("farm", "farm_id")
    farm_set = set(farm_ids)

    # Return the subset of the dataframe
    sub_farms_df = farms_df[farms_df[farm_id_col].isin(farm_set)]

    # Calculate start time
    start = timeit.default_timer()

    # Score
    scores_df, explanations = score_farms_species_by_id_list(
        sub_farms_df,
        species_df,
        cfg,
        get_valid_tree_ids=provider,
        params_index=params_dict,
    )

    # Calculate Stop time
    stop = timeit.default_timer()
    exec_time = stop - start

    print(f"Time taken: {exec_time}")

    return explanations
