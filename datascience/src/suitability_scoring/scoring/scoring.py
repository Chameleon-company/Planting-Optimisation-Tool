import pandas as pd
from suitability_scoring.utils.params import get_feature_params
from suitability_scoring.utils.config import load_yaml
from suitability_scoring.utils.params import build_species_params_dict


########################################################################################
# Helper functions
########################################################################################
def subset_species_by_ids(species_df, species_id_col, valid_ids):
    """
    Function to subset the species dataframe using a supplied id list.
    This is used to filter out the excluded tree species.

    :param species_df: DataFrame with tree species profile.
    :param species_id_col: Species id column name as a string.
    :param valid_ids: List of the compatible trees for the current farm.
    :returns: A dataframe containing only compatible trees.
    """
    # Check if the list of id's is empty
    if not valid_ids:
        # Return an empty dataframe
        return species_df.iloc[0:0]

    # List of id's is not empty so make a set to provided faster membership checks and
    # remove any duplicate id's automatically.
    valid_set = set(valid_ids)

    # Return the subset of the dataframe
    return species_df[species_df[species_id_col].isin(valid_set)]


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

    # Initialise results to an empty list
    results = []

    # Initialise explanation to an empty dictionary
    explanations = {}

    # Create a set of all the species ids in the species dataframe
    all_species_ids = set(species_df[species_id_col].tolist())

    # Loop through all rows of the farms dataframe
    for _, farm in farms_df.iterrows():
        # Get the farm id for the current farm
        farm_id = farm[farm_id_col]

        # Call the exclusion function to get the list of compatible tress for the current farm
        # return an empty list if the function returns None or is an empty list
        compatible_species = get_valid_tree_ids(farm)
        if compatible_species:
            valid_ids = compatible_species
        else:
            valid_ids = []

        # Create a dataframe by filtering out the excluded species
        sub_df = subset_species_by_ids(species_df, species_id_col, valid_ids)

        # Create a list of id's that are in the valid_id list but not found in the species dataframe
        # This should always be empty
        unknown_ids = [id for id in valid_ids if id not in all_species_ids]

        # Create an empty list that will hold the explanations for the current farm
        farm_explanations = []

        # Check if the filtered dataframe is empty. i.e. no compatible trees for this farm
        if sub_df.empty:
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
            continue

        # Loop through each tree species in the filtered dataframe
        for _, sp in sub_df.iterrows():
            # Get the current species id
            species_id = sp[species_id_col]

            # Get the current species name
            species_name = sp[species_name_col]

            # Get the current species common name
            species_cname = sp[species_cname_col]

            # Create an empty dictionary to hold the scores from each feature
            feature_scores = {}

            # Create an empty dictionary to hold the explanations for each feature
            feature_explain = {}

            # Initialise the numerator score
            num_sum = 0.0

            # Initialise the denominator score
            denom = 0.0

            # Loop through each feature defined in the configuration file
            for feat, meta in features_cfg.items():
                # Combine species specific params with YAML defaults
                params = get_feature_params(params_index, cfg, species_id, feat)

                # Get scoring method for this feature
                score_method = params["score_method"]

                # Get weight for this feature
                w = params["weight"]

                # Numeric feature
                if meta["type"] == "numeric":
                    # Get minimum value for the feature
                    min_v = sp.get(f"{feat}_min")

                    # Get maximum value for the feature
                    max_v = sp.get(f"{feat}_max")

                    # Get the farm's value for this feature
                    x = farm.get(feat)

                    # Range scoring
                    if score_method == "num_range":
                        # Score this feature
                        score = numerical_range_score(x, min_v, max_v)

                        # Determine reason for score
                        if score == 1.0:
                            reason = "inside preferred range"

                        elif score == 0.0:
                            if x < min_v:
                                reason = "below minimum"
                            else:
                                reason = "above maximum"
                        else:
                            reason = "missing data"

                        # Store the parameters used for the scoring
                        params_out = {"min": min_v, "max": max_v}

                    else:  # No valid scoring method selected
                        raise ValueError(
                            f"Unknown numeric scoring method '{score_method}' for '{feat}'"
                        )

                    # Store score for this feature
                    feature_scores[feat] = score

                    # Store explanation for this feature
                    feature_explain[feat] = {
                        "short_name": meta["short"],
                        "type": "numerical",
                        "farm_value": x,
                        "score": score,
                        "reason": reason,
                        "params": params_out,
                    }

                # Categorical feature
                elif meta["type"] == "categorical":
                    # Get categorical dictionary
                    cat_cfg = meta.get("categorical", {}) or {}

                    # Get farm value for this feature
                    val = farm.get(feat)

                    # Get list of preferences for this feature
                    prefs = parse_prefs(sp.get(f"preferred_{feat}"))

                    # Check if the score method is for an exact categorical match
                    if score_method == "cat_exact":
                        # Get the score for an exact match
                        exact_score = float(cat_cfg.get("exact_match", 1.0))

                        # Call exact match scoring function
                        score = categorical_exact_score(
                            val, prefs, exact_score=exact_score
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
                        "short_name": meta["short"],
                        "type": "categorical",
                        "farm_value": val,
                        "preferred": prefs,
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
    all_ids = species_df[species_id_col].tolist()[:3]

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

    # Score
    scores_df, explanations = score_farms_species_by_id_list(
        sub_farms_df,
        species_df,
        cfg,
        get_valid_tree_ids=provider,
        params_index=params_dict,
    )

    return explanations
