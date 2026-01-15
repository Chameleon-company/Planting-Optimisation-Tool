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
    if (value is None) or (min_val is None) or (max_val is None):
        return None
    try:
        return 1.0 if float(min_val) <= float(value) <= float(max_val) else 0.0
    except (ValueError, TypeError):
        return None


def derive_trapezoid_from_minmax(min_v, max_v, delta_left, delta_right):
    """
    For species min/max, derive trapezoid params:
      a = min_v
      d = max_v
      b = min_v + delta_left   (shrink from min inward)
      c = max_v - delta_right  (shrink from max inward)

    If b > c after deltas, collapse plateau to midpoint to preserve a <= b <= c <= d.

    :param min_v: Minimum value
    :param max_v: Maximum value
    :param delta_left: Left shoulder width
    :param delta_right: Right shoulder width
    :returns: Float values for the trapezoid points.
    """
    if min_v is None or max_v is None:
        raise ValueError("min/max cannot be None.")
    min_v = float(min_v)
    max_v = float(max_v)

    if max_v < min_v:
        raise ValueError(f"max ({max_v}) < min ({min_v})")

    # Set the values of a and d
    a, d = min_v, max_v

    # Total width of trapezoid
    width = d - a

    b = a + delta_left
    c = d - delta_right

    # Ensure ordering a <= b <= c <= d
    if b > c:
        # Collapse plateau to midpoint to enforce point ordering
        mid = a + width / 2.0
        b = c = mid
    return a, b, c, d


def numerical_trapezoid_score(x, min_v, max_v, tol_left, tol_right):
    """
    Scoring for a trapezoid with shoulders [a,b], [c,d]; plateau [b,c],
    a=min, d=max, inner [b,c] from tolerances.
        b ------ c
       /          \
      /            \
     /              \
    a                d

    Function returns tuple containing the score, reason and trapezoid points. If any of x,
    min_v, max_v is missing a None score is returned. If x is within the trapezoid a score
    value in [0,1] is returned.
     
    Function assumes valid order a <= b <= c <= d.

    :param x:
    :param min_v:
    :param max_v:
    :param tol_left:
    :param tol_right:
    :returns: Tuple with score, reason and trapezoid points
    """
    if x is None:
        return None, "missing farm data", {}

    if min_v is None or max_v is None:
        return None, "missing species data", {}

    # Derive the trapezoid values
    a, b, c, d = derive_trapezoid_from_minmax(min_v, max_v, tol_left, tol_right)

    params_out = {"a": a, "b": b, "c": c, "d": d}

    # Below minimum
    if x < a:
        s = 0.0
        reason = "below minimum"

    elif a <= x < b:  # Left shoulder
        s = (x - a) / (b - a) if (b - a) > 0 else 0.0
        reason = f"within left shoulder [{a}, {b}]"

    elif b <= x <= c:  # Plateau
        s = 1.0
        reason = f"within plateau [{b}, {c}]"

    elif c < x <= d:  # Right shoulder
        s = (d - x) / (d - c) if (d - c) > 0 else 0.0
        reason = f"within right shoulder [{c}, {d}]"

    else:  # Above maximum x>d
        s = 0.0
        reason = "above maximum"

    return s, reason, params_out


def categorical_exact_score(value, preferred_list):
    """
    Function for scoring categorical values with an exact match.
    Returns exact_score if the value is in the preferred_list, else 0.0 and None for
    missing or no preferences.

    :param value: Farm's value of the feature.
    :param preferred_list: List of preferred values.
    :returns: Score value between 0 and 1 or None.
    """
    if value is None or not preferred_list:
        return None
    return 1.0 if (value in preferred_list) else 0.0


def categorical_compatibility_score(value, preferred_list, compat_dict):
    """
    Function for scoring categorical values using a compatibility matrix.
    Returns exact_score if the value is in the preferred_list, a value in [0,1]
    if the value matches another in the compatibility matrix else 0.0 and None for
    missing or no preferences.

    :param value: Farm's value of the feature.
    :param preferred_list: List of preferred values.
    :param compat_dict: Compatibility dictionary.
    :returns: Score value between 0 and 1 or None and the reason for the score.
    """
    if value is None:
        return None, "missing farm data"

    if not preferred_list:
        return None, "missing species data"

    # Compute per-preference scores and record match types
    pref_details = []

    for p in preferred_list:
        # Exact match if the preference equals value AND compatibility score available
        base = compat_dict.get(value, {}).get(p)

        if base is not None:
            score = float(base)

            if p == value:  # Exact match
                reason = "exact match"
            else:  # Compatibility match
                reason = f"closest compatibility match {p} at {score:.2f}"

            pref_details.append({"score": score, "reason": reason})
            continue
        else:
            pref_details.append({"score": 0.0, "reason": "no_match"})

    # Find the maximum score
    max_score = max(d["score"] for d in pref_details)

    # Collect all dicts that match that score
    if max_score > 0.0:
        top_reasons = [d["reason"] for d in pref_details if d["score"] == max_score]
    else:
        top_reasons = ["no_match"]

    # Join them into a single string separated by commas
    joined_reasons = ". ".join(top_reasons)

    return max_score, joined_reasons


def calculate_suitability(farm_data, species_list, optimised_rules, cfg):
    """
    This function performs a granular suitability assessment to score
    specific tree species against a single farm profile.

    Scoring Methodology
    Scoring is performed using a weighted arithmetic mean of individual feature scores.
    Feature behaviour is defined in `cfg['features']` and applied as follows:

    * Numerical features: Evaluated using one of two scoring methods
        * `num_range`: A score of 1.0 is awarded if the farm's value falls between the
          species' min/max requirements. Zero scores are assigned for values outside this
          range. None is assigned for missing data.

        * `trapezoid`: A score in [0, 1] is awarded if the farm's value falls within the
          trapezoid. Zero scores are assigned for values outside this
          range. None is assigned for missing data.

    * Categorical features: Evaluated using one of two scoring methods
        * `cat_exact`: Checks if the farm's attribute (e.g., soil texture) exists within
          the species' list of preferred types. A score of 1.0 is returned is an exact match
          is found and zero if no match is found.

        * `cat_compatibility`: Scores using a compatibility matrix. Returns 1.0 if an exact
          match is found, a value in [0,1] if the value matches another in the compatibility
          matrix else 0.0 and None for missing or no preferences.

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

                    # Get the output parameters
                    params_out = rule.get("params_out")

                    # Determine reason for score
                    if score == 1.0:
                        reason = "inside preferred range"
                    elif score == 0.0:
                        if farm_val < min_v:
                            reason = "below minimum"
                        else:
                            reason = "above maximum"
                    else:
                        if farm_val is None:
                            reason = "missing farm data"
                        elif (min_v is None) or (max_v is None):
                            reason = "missing species data"
                        else:
                            reason = "missing data"
                elif score_method == "trapezoid":
                    # Get minimum, maximum and tolerance values for the feature
                    min_v, max_v, left_tol, right_tol = rule["args"]

                    # Score the farm value
                    score, reason, params_out = numerical_trapezoid_score(
                        farm_val, min_v, max_v, left_tol, right_tol
                    )

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
                    "params": params_out,
                }

            # Categorical feature
            elif rule["type"] == "categorical":
                # Check if the score method is for an exact categorical match
                if score_method == "cat_exact":
                    # Get list of preferences for this feature
                    prefs = rule["args"]

                    # Call exact match scoring function
                    score = categorical_exact_score(farm_val, prefs)
                    if score is None:
                        reason = "missing or no preference"
                    elif score == 1.0:
                        reason = "exact match"
                    else:
                        reason = "no match"
                elif score_method == "cat_compatibility":
                    # Get list of preferences and compatibility dictionary
                    prefs, compat_dict = rule["args"]

                    # Score the farm value
                    score, reason = categorical_compatibility_score(
                        farm_val, prefs, compat_dict
                    )
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
