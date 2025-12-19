import pandas as pd


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
    try:
        return 1.0 if float(min_val) <= float(value) <= float(max_val) else 0.0
    except (ValueError, TypeError):
        return None


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


def calculate_suitability(farm_data, species_list, optimised_rules, cfg):
    """
    This function performs a granular suitability assessment to score
    specific tree species against a single farm profile.

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

    :param farms_data: Dictionary containing the farm's features (farm profile).
    :param species_list: List of dictionaries (species profile), each representing a valid
      candidate species.
    :param optimised_rules: Dictionary of scoring rules for each species.
    :param cfg: Configuration dictionary containing feature metadata.
    :returns explanations: List of result dictionaries with scores and detailed explanations.
    """

    # Get column names from config with defaults
    species_id_col = cfg.get("ids", {}).get("species", "id")
    species_name_col = cfg.get("names", {}).get("species_name", "name")
    species_cname_col = cfg.get("ids", {}).get("species_common_name", "common_name")

    # Initialise results to an empty list
    results = []

    # Initialise and empty list to hold scores for testing and debugging
    scores = []

    # Loop through each tree species in the filtered dataframe
    for sp in species_list:
        # Get species dictionary
        species_id = sp.get(species_id_col)

        # Get the current species name
        species_name = sp.get(species_name_col)

        # Get the current species common name
        species_cname = sp.get(species_cname_col)

        # Grab the pre-computer rules for this species
        rules = optimised_rules[species_id]

        # Create an empty dictionary to hold the scores from each feature
        feature_scores = {}

        # Create an empty dictionary to hold the explanations for each feature
        feature_explain = {}

        # Initialise the numerator score
        num_sum = 0.0

        # Initialise the denominator score
        denom = 0.0

        # Iterate through the rules list
        for rule in rules:
            # Get feature name from rule
            feat = rule["feat"]

            # Get the farm's value for this feature
            farm_val = farm_data.get(feat)

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
                        if pd.isna(farm_val):
                            reason = "missing farm data"
                        elif pd.isna(min_v) or pd.isna(max_v):
                            reason = "missing species data"
                        else:
                            reason = "missing data"

                else:  # No valid scoring method selected
                    raise ValueError(
                        f"Unknown numeric scoring method '{score_method}' for '{feat}'"
                    )

                # Store explanation for this feature
                feature_explain[feat] = {
                    "short_name": rule["short_name"],
                    "type": "numerical",
                    "farm_value": farm_val,
                    "score": score,
                    "reason": reason,
                    "params": rule.get("params_out"),
                }

            # Categorical feature
            elif rule["type"] == "categorical":
                # Check if the score method is for an exact categorical match
                if score_method == "cat_exact":
                    # Get list of preferences and score for an exact match for this feature
                    prefs, exact_match_score = rule["args"]

                    # Call exact match scoring function
                    score = categorical_exact_score(
                        farm_val, prefs, exact_score=exact_match_score
                    )
                    if score is None:
                        reason = "missing or no preference"
                    elif score == exact_match_score:
                        reason = "exact match"
                    else:
                        reason = "no match"
                else:  # No valid scoring method selected
                    raise ValueError(
                        f"Unknown categorical mode '{score_method}' for feature '{feat}'"
                    )

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
                raise ValueError(f"Unknown feature type '{rule['type']}' for '{feat}'")

            # Store score
            feature_scores[feat] = score

            # Accumulate scores for existing scores and weights
            if score is not None and w > 0:
                num_sum += w * feature_scores[feat]
                denom += w

        # End of feature loop
        if denom > 0:
            total_score = num_sum / denom
        else:
            total_score = 0.0

        # Append dictionary containing specie specific information
        results.append(
            {
                "species_id": species_id,
                "species_name": species_name,
                "species_common_name": species_cname,
                "mcda_score": total_score,
                "features": feature_explain,
            }
        )

        scores.append((species_id, total_score))

    return results, scores
