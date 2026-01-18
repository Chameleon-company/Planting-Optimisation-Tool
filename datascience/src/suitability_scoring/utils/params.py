def to_float_or_none(value):
    """
    Convert value to float or None. Handles exception if the value cannot be converted
    to a Float.

    :param value: Value to be converted to a Float.
    """
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def to_string_or_none(value):
    """
    Convert value to string or None. Raises and exception if the value cannot be
    converted to a String.

    :param value: Value to be converted to a String.
    """
    if value is None or str(value).strip() == "":
        return None
    else:
        return str(value)


def build_species_params_dict(species_params_rows, config):
    """
    This function builds an dictionary of species parameters for lookup
      params_dict[species_id][feature] = {
        'score_method': str|None,
        'weight': float|None,
        'trap_left_tol':float|None,
        'trap_right_tol':float|None,
      }
    from a list of row dictionaries.

    Each row is for a species x feature.

    :param species_rows: List of dictionaries.
    :param config: Configuration dictionary
    :returns index: Nested dictionary with the species parameters.
    """
    # Create an empty dictionary
    params_dict = {}

    # Column name for species id
    species_id_col = "species_id"

    # For each row in the species_params dataframe
    for row in species_params_rows:
        # Get the species_id for this row
        species_id = (
            int(row[species_id_col]) if row[species_id_col] is not None else "unknown"
        )

        # Get the feature name for this row
        feat = row["feature"]

        # Look up the species_id in the dictionary:
        #   if it exists, return the existing value for over-writing
        #   if it doesn't exist, create an empty dictionary
        # Set the feat key for the dictionary to a new dictionary
        # contains keys score_method and weight.
        # use .get to return None if the values for score_method or weight are missing.
        params_dict.setdefault(species_id, {})[feat] = {
            "score_method": to_string_or_none(row.get("score_method")),
            "weight": to_float_or_none(row.get("weight")),
            "trap_left_tol": to_float_or_none(row.get("trap_left_tol")),
            "trap_right_tol": to_float_or_none(row.get("trap_right_tol")),
        }
    return params_dict


def get_feature_params(params_dict, config, species_id, feature):
    """
    Merge species-specific parameters with YAML defaults for one (species, feature).

    :param params_dict: Nested dictionary with the species parameters.
    :param config: Configuration dictionary.
    :param species_id: The id of the species.
    :param feature: The feature name as a string.
    :returns: Dictionary containing score_method, weight and trapezoid tolerances.
    """
    # Dictionary for the specified feature
    meta = config["features"][feature]

    # Get the default score_method for this feature
    default_scm = meta.get("score_method")

    # Get the default weight if specified or return zero
    default_weight = float(meta.get("default_weight", 0.0))

    # Get trapezoid tolerance dict if specified or return empty dict
    meta_tolerance = meta.get("tolerance", {})

    # Get the default trapezoid left tolerance if specified or return zero
    default_trap_left_tol = float(meta_tolerance.get("left", 0.0))

    # Get the default trapezoid right tolerance if specified or return zero
    default_trap_right_tol = float(meta_tolerance.get("right", 0.0))

    # Species override from params_dict (read from species_params.csv) (may be empty)
    # Get the species-level parameters
    species_params = params_dict.get(species_id, {})

    # Get the feature-level parameters
    sp_feature_params = species_params.get(feature, {})

    # Score method
    score_method = sp_feature_params.get("score_method")
    if score_method is None:
        score_method = default_scm

    # Weight
    weight = sp_feature_params.get("weight")
    if weight is None:
        weight = default_weight
    else:
        weight = float(weight)

    # Trapezoid tolerances
    trap_left_tol = sp_feature_params.get("trap_left_tol")
    if trap_left_tol is None:
        trap_left_tol = default_trap_left_tol
    else:
        trap_left_tol = float(trap_left_tol)

    trap_right_tol = sp_feature_params.get("trap_right_tol")
    if trap_right_tol is None:
        trap_right_tol = default_trap_right_tol
    else:
        trap_right_tol = float(trap_right_tol)

    return {
        "score_method": score_method,
        "weight": weight,
        "trap_left_tol": trap_left_tol,
        "trap_right_tol": trap_right_tol,
    }


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


def build_rules_dict(species_list, params, cfg):
    """
    Builds a dictionary of rules for each species/feature combination

    :param species_list: List of species dictionaries
    :param params: Nested dictionary with the species parameters.
    :param cfg: Configuration dictionary
    :returns: Dictionary of rules
    """
    # Fetch column name for species id
    species_id_col = cfg.get("ids", {}).get("species", "id")

    # Fetch feature dictionary
    features_cfg = cfg["features"]

    # Create a rules dictionary for optimisation
    # Structure: { species_id: [ (feature_key, rule_metadata, pre_calc_values), ... ] }
    rules = {}

    for sp in species_list:
        sp_id = sp.get(species_id_col)
        rules_list = []

        for feat, meta in features_cfg.items():
            # Resolve overrides and defaults once
            combined_params = get_feature_params(params, cfg, sp_id, feat)

            weight = combined_params["weight"]
            score_method = combined_params["score_method"]

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

            elif score_method == "trapezoid":
                min_v = sp.get(f"{feat}_min")
                max_v = sp.get(f"{feat}_max")
                left_tol = combined_params["trap_left_tol"]
                right_tol = combined_params["trap_right_tol"]
                rule_data["args"] = (min_v, max_v, left_tol, right_tol)

            elif score_method == "cat_exact":
                # Note: In the database the column name is feature+'s'
                prefs = parse_prefs(sp.get(f"{feat}s"))
                cat_cfg = meta.get("categorical", {}) or {}
                rule_data["preferred"] = prefs
                rule_data["args"] = prefs

            elif score_method == "cat_compatibility":
                prefs = parse_prefs(sp.get(f"{feat}s"))
                rule_data["preferred"] = prefs
                cat_cfg = meta.get("compatibility_pairs", {}) or {}
                rule_data["args"] = (prefs, cat_cfg)

            rules_list.append(rule_data)

        rules[sp_id] = rules_list
    return rules
