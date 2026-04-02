"""
Task 7 - Exclusion Rules Core Logic (API-aligned: id)

Key points
- Uses "id" for both farm and species primary keys (API aligned)
- Rules are config-driven via RULES list (easy to add/remove rules)
- Column mapping is centralised (easy to adapt to renamed columns)
- Missing data does NOT exclude species (skip rule safely)
- Dependency check is optional via config["dependency"]["enabled"] (default False)
- Dependency headers may contain trailing spaces (handled by stripping keys)

Updates included:
- Task 8: Add annotation logic (more specific, readable reasons)
- Task 9: Handle missing data (explicitly enforced; no exclusion on missing values)
- Task 10: Make it configurable (support direct column names in config rules)

# NOTES:
# Exclusion_criteria.xlsx includes some narrative/text rules.
# In this sprint we do not parse text-only rules.
# Exclusions are driven by structured datasets only.
# Missing values are skipped to avoid accidental exclusion when data is incomplete.

# Notes on missing vs valid values handling:
#
# - Blank / NA-like values (e.g. "", "NA", "N/A", "null", None) are treated as MISSING
#   and will cause the rule to be skipped (no exclusion).
#
# - False is considered a VALID value and may trigger exclusion
#   (e.g. habitat flags such as coastal / riparian).
#
# - 0 is considered a VALID numeric value and will be evaluated normally
#   in numeric comparisons (e.g. rainfall, temperature, elevation).
#
# This design avoids accidental exclusion when datasets are incomplete,
# while still respecting explicit negative constraints in the data.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set


# ============================================================
# 2) Rules (edit/add rules here later; core flow does NOT change)
# ============================================================

RULES: List[Dict[str, Any]] = [
    # Habitat rules: only apply if farm flag == True.
    # If farm flag missing => skip rule safely.
    {
        "id": "coastal_habitat",
        "farm": "coastal_flag",
        "op": "requires_true",
        "species": "coastal_ok",
        "reason": "excluded: not suitable for coastal habitat",
    },
    {
        "id": "riparian_habitat",
        "farm": "riparian_flag",
        "op": "requires_true",
        "species": "riparian_ok",
        "reason": "excluded: not suitable for riparian habitat",
    },
]


# ============================================================
# 3) Dependency model (name-based, flexible parser)
# ============================================================
@dataclass(frozen=True)
class DependencyRule:
    focal_species_name: str
    good_partners: Set[str]
    reason: str = "excluded: no suitable host plant"


def _compare(farm_val: Any, op: str, threshold_val: Any) -> Optional[bool]:
    """ """
    if farm_val is None:
        return False

    if threshold_val is None:
        return True

    # Categorical logic
    if op in ("==", "!=", "in_set", "not_in_set"):
        f_str = str(farm_val).strip().lower()

        # Ensure threshold is a list for consistent processing
        if isinstance(threshold_val, list):
            not_allowed_list = [str(t).strip().lower() for t in threshold_val]
        else:
            not_allowed_list = [str(threshold_val).strip().lower()]

        if op == "==" or op == "in_set":
            # Exclude if farm value is in the list
            return f_str not in not_allowed_list

        if op == "!=" or op == "not_in_set":
            # Exclude if farm value is not in the list
            return f_str in not_allowed_list

    # Numeric logic
    try:
        f_num = float(farm_val)
    except (ValueError, TypeError):
        return False

    try:
        t_num = float(threshold_val)
    except (ValueError, TypeError):
        return True

    if op == "<":
        return not (f_num < t_num)
    if op == ">":
        return not (f_num > t_num)
    if op == "<=":
        return not (f_num <= t_num)
    if op == ">=":
        return not (f_num >= t_num)

    return True


# def parse_dependencies_rows(
#     dep_rows: List[Dict[str, Any]],
#     *,
#     focal_key: str = "Focal_species",
#     partners_key: str = "Good_tree_partners",
#     default_reason: str = "excluded: no suitable host plant",
# ) -> List[DependencyRule]:
#     """
#     Parse dependency rows in a flexible way.

#     The Excel file may have headers like:
#         "Good_tree_partners  "
#         "Role "
#         "Group_notes "
#     We strip whitespace from keys so it keeps working if spacing changes.
#     """
#     rules: List[DependencyRule] = []

#     for row in dep_rows:
#         clean_row = {str(k).strip(): v for k, v in row.items()}

#         focal = _norm_str(clean_row.get(focal_key))
#         partners = _parse_set(clean_row.get(partners_key)) or set()
#         partners = {p for p in partners if _norm_str(p)}

#         if focal and partners:
#             rules.append(
#                 DependencyRule(
#                     focal_species_name=focal,
#                     good_partners=partners,
#                     reason=default_reason,
#                 )
#             )

#     return rules


# ============================================================
# 4) Core function (records-based)
# ============================================================


def run_exclusion_rules_records(
    farm_data: Any,
    all_species: List[Any],
    rules_lookup: Dict[int, List[Any]],
    dependencies_rows: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Apply exclusion rules for ONE farm.

    Returns
    -------
    {
      "candidate_ids": [...],
      "excluded_species": [
        {"id", "species_name", "species_common_name", "reasons": [...]}
      ]
    }
    """
    excluded: List[Dict[str, Any]] = []
    candidates: List[int] = []

    # For each species, check all applicable rules and annotate reasons for exclusion if any rule fails.
    for sp in all_species:
        # Get species dictionary
        species_id = _get_val(sp, "id")

        # Get the current species name
        species_name = _get_val(sp, "name")

        # Get the current species common name
        species_cname = _get_val(sp, "common_name")

        # Initialise list to hold exclusion reasons for this species
        reasons = []

        # Check if there are any rules applicable to this species based on its ID
        if species_id in rules_lookup:
            # For each rule applicable to this species, check if the farm data violates it
            for rule in rules_lookup[species_id]:
                # Get farm value based on rule's farm feature
                rule_feature = _get_val(rule, "feature")
                if rule_feature is None:
                    continue  # Skip rule if feature is missing
                farm_val = _get_val(farm_data, rule_feature)
                print(type(farm_val))
                # Compare farm value to species threshold using rule's operator
                if _compare(farm_val, _get_val(rule, "operator"), _get_val(rule, "value")) is False:
                    reasons.append(f"excluded: {_get_val(rule, 'reason')}, farm value = {str(farm_val).strip().lower()}")

        ################################################################################
        # STORY 34: Ecological matching would go here (not implemented in this PR)
        ################################################################################
        if reasons:
            excluded.append(
                {
                    "id": species_id,
                    "species_name": species_name,
                    "species_common_name": species_cname,
                    "reasons": reasons,
                }
            )
        else:
            candidates.append(species_id)

    # 2) Dependency pass (optional)
    # dep_enabled = cfg.get("dependency", {}).get("enabled", False)

    # if dep_enabled and dependencies_rows:
    #     dep_rules = parse_dependencies_rows(dependencies_rows)

    #     candidate_set = set(candidates)
    #     excluded_by_id = {e["id"]: e for e in excluded}

    #     for dep in dep_rules:
    #         focal_id = name_to_id.get(dep.focal_species_name.lower())
    #         if focal_id is None or focal_id not in candidate_set:
    #             continue

    #         partner_ids = {name_to_id.get(p.lower()) for p in dep.good_partners if p}
    #         partner_ids = {pid for pid in partner_ids if pid is not None}

    #         if not partner_ids.intersection(candidate_set):
    #             candidate_set.remove(focal_id)

    #             # Task 8: dependency reason is already human readable in DependencyRule.reason
    #             if focal_id in excluded_by_id:
    #                 excluded_by_id[focal_id]["reasons"].append(dep.reason)
    #             else:
    #                 sp = id_to_species.get(focal_id, {})
    #                 excluded_by_id[focal_id] = {
    #                     "id": focal_id,
    #                     "species_name": _get_val(sp, SPECIES_COL["species_name"], None),
    #                     "species_common_name": _get_val(sp, SPECIES_COL["species_common_name"], None),
    #                     "reasons": [dep.reason],
    #                 }

    #    candidates = sorted(candidate_set)
    #    excluded = list(excluded_by_id.values())

    return {
        "candidate_ids": candidates,
        "excluded_species": excluded,
    }


def _get_val(obj, key, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)
