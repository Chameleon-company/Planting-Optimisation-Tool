"""
Species suitability and recommendations package.

This package provides a small, focused toolkit for computing species-farm
suitability scores and turning them into ranked recommendations. It centers on
a transparent multi-criteria decision analysis (MCDA) workflow that supports
both numerical and categorical features, offers per-feature explanations, and
keeps internal helpers encapsulated behind a clean public API.


-------------------------------------------------------------------------------
Public API
-------------------------------------------------------------------------------
- calculate_suitability(
    farm_data: dict,
    species_list: list[dict],
    optimised_rules: dict,
    cfg: dict
  ) -> tuple[list[dict], list[tuple[int | str, float]]]
    Compute suitability for a single farm profile against multiple species
    using a weighted arithmetic mean of feature scores.

    Supported scoring modes:
      • Numerical
          - "num_range": 1.0 if farm_value ∈ [min, max]; 0.0 if out of range;
            None if missing farm or species data.
          - "trapezoid": returns a score in [0.0, 1.0] if inside the trapezoid
            (min/max with left/right tolerances); 0.0 if outside; None if missing.
      • Categorical
          - "cat_exact": 1.0 for exact membership match in preferences;
            0.0 for no match; None if missing/no preference.
          - "cat_compatibility": 1.0 for exact match; value in [0,1] for
            compatible alternatives; 0.0 for incompatible; None if missing.

    Returns:
      1) results: list[dict] — each item contains:
           {
             "species_id", "species_name", "species_common_name",
             "mcda_score": float,
             "features": {
               feat_key: {
                 "short_name": str,
                 "type": "numerical" | "categorical",
                 "farm_value": Any,
                 "score": float | None,
                 "reason": str,
                 # optional transparency fields, e.g. "params" or "preferred"
               }, ...
             }
           }
      2) scores: list[tuple[species_id, score]] — convenient (id, score) pairs.

- build_species_recommendations(species_list: list[dict]) -> list[dict]
    Rank species (descending) by "mcda_score" with dense tie-breaking.
    Produces dictionaries containing:
      "species_id", "species_name", "species_common_name",
      "score_mcda" (rounded), "rank_overall", and "key_reasons"
      (compact textual reasons derived from per-feature explanations).

- build_species_params_dict(
    species_params_rows: list[dict],
    config: dict
  ) -> dict[int | str, dict[str, dict[str, float | str | None]]]
    Build an index of species parameters for lookup:
      params[species_id][feature] = {
        "score_method": str | None,
        "weight": float | None,
        "trap_left_tol": float | None,
        "trap_right_tol": float | None,
      }
    Values are coerced using internal converters (e.g., to_*_or_none) for robust parsing.

- build_rules_dict(
    species_list: list[dict],
    params: dict,
    cfg: dict
  ) -> dict[int | str, list[dict]]
    Construct per-species, per-feature scoring rules by combining species
    attributes with configuration defaults/overrides. Each rule includes:
      {
        "feat", "weight", "short_name", "type", "score_method",
        "args": (...)  # method-specific:
                       #   num_range        -> (min, max)
                       #   trapezoid        -> (min, max, left_tol, right_tol)
                       #   cat_exact        -> prefs
                       #   cat_compatibility-> (prefs, compatibility_pairs)
        # Optional transparency fields:
        #   "params_out": {"min": ..., "max": ...} for num_range
        #   "preferred": [...] for categorical modes
      }

- load_yaml(path: str) -> dict
    Load a YAML file from `path` (UTF‑8) using `yaml.safe_load` and return a
    Python dictionary.


-------------------------------------------------------------------------------
Data & configuration expectations
-------------------------------------------------------------------------------
- cfg["ids"] / cfg["names"]: dict
    Mapping for canonical column/field names (e.g., species IDs and names).
- cfg["features"]: dict[str, dict]
    Feature metadata. Each feature should specify:
      - "type": "numeric" | "categorical"
      - "short": short display name
      - (optional) "compatibility_pairs": dict for categorical compatibility
- species_list: list[dict]
    Each species row provides raw attributes used by rule construction, e.g.:
      - For numeric features: "<feat>_min", "<feat>_max"
      - For categorical features: "<feat>s" (plural) with preference strings
- species_params_rows: list[dict]
    Per (species, feature) overrides such as score_method, weight, trapezoid tolerances.

-------------------------------------------------------------------------------
Quick start
-------------------------------------------------------------------------------
>>> # Load configuration and data
>>> from yourlib import (
...     load_yaml,
...     build_species_params_dict,
...     build_rules_dict,
...     calculate_suitability,
...     build_species_recommendations,
... )
>>>
>>> # Load configuration file
>>> cfg = load_yaml("config.yaml")
>>>
>>> # Build parameters index and scoring rules
>>> params = build_species_params_dict(species_params_rows, cfg)
>>> rules = build_rules_dict(species_list, params, cfg)
>>>
>>> # Score all species for the farm and get explanations
>>> # farm single farm profile dict
>>> results, scores = calculate_suitability(farm, species_list, rules, cfg)
>>>
>>> # Produce ranked recommendations
>>> recs = build_species_recommendations(results)
>>> recs[:3]
[{'species_id': 101, 'species_name': 'X', 'species_common_name': 'Y',
  'score_mcda': 0.842, 'rank_overall': 1,
  'key_reasons': ['Soil:exact match', 'Rainfall:inside preferred range', ...]},
 ...]


-------------------------------------------------------------------------------
Stability & versioning
-------------------------------------------------------------------------------
- Only the items re-exported from this package and listed in `__all__`
  are considered part of the public, supported API.
- Internal helpers (e.g., numerical_range_score, numerical_trapezoid_score,
  categorical_exact_score, categorical_compatibility_score, get_feature_params,
  parse_prefs, assign_dense_ranks) are implementation details and may change
  without notice.
"""

from .scoring import calculate_suitability
from .utils import build_species_params_dict, build_rules_dict, load_yaml
from .recommend import build_species_recommendations

__all__ = [
    "calculate_suitability",
    "build_species_params_dict",
    "build_rules_dict",
    "build_species_recommendations",
    "load_yaml",
]
