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
