def run_exclusion_rules(farm_data, species_data, config):
    """
    Dummy implementation of the exclusion rules module.

    This version does not apply any real exclusion logic.
    All species are treated as valid candidates.

    Parameters
    ----------
    farm_data : dict
        Farm-level information such as rainfall, temperature, soil and habitat flags.
        (Not used in the dummy version.)
    species_data : list of dict
        Species records. Each record is expected to contain a 'species_id' field.
    config : dict
        Rule thresholds and settings.
        (Not used in the dummy version.)

    Returns
    -------
    dict
        {
            "candidate_ids": [...],
            "excluded_species": []
        }
    """
    candidate_ids = []

    for record in species_data:
        # Backend uses "id" for species identifier
        if "id" in record:
            candidate_ids.append(record["id"])

    return {
        "candidate_ids": candidate_ids,
        "excluded_species": [],
    }
