import pandas as pd


def build_species_params_dict(species_params_df, config):
    """
    This function builds an dictionary of species parameters for lookup
      params_dict[species_id][feature] = {
        'score_method': str|None,
        'weight': float|None
      }
    from the species_params dataframe to prevent the scoring from searching through the dataframe.

    The species_parameters dataframe is in long form were each row is for a species x feature.
    This choice was made for the future move to a database.

    :param species_params_df: DataFrame with the per species parameters.
    :param config: Configuration dictionary
    :returns index: Nested dictionary with the species parameters.
    """
    # Create an empty dictionary
    params_dict = {}

    # Get column name for species id
    species_id_col = config.get("ids", {}).get("species", "species_id")

    # For each row in the species_params dataframe
    for _, row in species_params_df.iterrows():
        # Get the species_id for this row
        species_id = row[species_id_col]

        # Get the feature name for this row
        feat = row["feature"]

        # Look up the species_id in the dictionary:
        #   if it exists, return the existing value for over-writing
        #   if it doesn't exist, create an empty dictionary
        # Set the feat key for the dictionary to a new dictionary
        # contains keys score_method and weight.
        # use .get to return None if the values for score_method or weight are missing.
        params_dict.setdefault(species_id, {})[feat] = {
            "score_method": row.get("score_method"),
            "weight": row.get("weight"),
        }
    return params_dict


def get_feature_params(params_dict, config, species_id, feature):
    """
    Merge species-specific parameters with YAML defaults for one (species, feature).

    :param params_dict: Nested dictionary with the species parameters.
    :param config: Configuration dictionary.
    :param species_id: The id of the species.
    :param feature: The feature name as a string.
    :returns: Dictionary containing score_method and weight.
    """
    # Dictionary for the specified feature
    meta = config["features"][feature]

    # Get the default score_method for this feature
    default_scm = meta.get("score_method")

    # Get the default weight if specified or return zero
    default_weight = float(meta.get("default_weight", 0.0))

    # Species override from params_dict (read from species_params.xlsx) (may be empty)
    # Get the species-level parameters
    species_params = params_dict.get(species_id, {})

    # Get the feature-level parameters
    sp_feature_params = species_params.get(feature, {})

    # Score method
    score_method = sp_feature_params.get("score_method")
    if score_method is None or pd.isna(score_method):
        score_method = default_scm

    # Weight
    weight = sp_feature_params.get("weight")
    if weight is None or pd.isna(weight):
        weight = default_weight
    else:
        weight = float(weight)

    return {"score_method": score_method, "weight": weight}
