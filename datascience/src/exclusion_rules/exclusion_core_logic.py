from typing import Any, Dict, List, Optional


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


def _check_biological_dependencies(candidate_ids: list[int], dep_lookup: dict[int, list[int]]):
    """
    Iteratively removes species whose required biological partners
    (e.g., host plants) are no longer in the candidate list.

    1. Iterative Reduction (while True):
     Dependencies can be "chained" (e.g., Species A depends on Species B, and Species B
     depends on Species C). If Species C is excluded by a physical rule (like soil pH),
     Species B must be removed. Once Species B is removed, the next pass of the loop will
     identify that Species A must also be removed. The loop continues until no more species
     are disqualified.

    2. The "OR" Logic (any(...)):
     The logic is designed to be supportive rather than overly aggressive. If a species like
     Sandalwood can use either Acacia or Casuarina as a host, it will remain a candidate as
     long as at least one of those species is still on the list.

    3. Post-Physical Check:
     This function runs after all physical exclusion rules and ecological filters have finished.
     This ensures that "Partners" are only counted if they actually survive the farm's environmental
     conditions.

    4. Stable State:
     The loop only breaks when it reaches a "Stable State"—meaning every remaining species either has
     no dependencies or has at least one viable partner remaining in the set.

    5. Fail-Safe:
     If a species has no dependencies defined in the species_dependencies table, it is ignored by this
     function and passes through to the next stage.
    """
    # Convert to a set for lookups during the loop
    current_candidates = set(candidate_ids)

    while True:
        to_remove = set()

        for sid in current_candidates:
            # Check if the species has any mandatory dependencies
            if sid in dep_lookup:
                partners = dep_lookup[sid]

                # If NONE of the required partners are still candidates,
                # this species cannot survive and must be removed
                if not any(pid in current_candidates for pid in partners):
                    to_remove.add(sid)

        # If no species were disqualified in this pass, the list is stable
        if not to_remove:
            break

        # Remove identified species and run the loop again to check for
        # cascading effects (e.g., if A needs B, and B was just removed)
        current_candidates -= to_remove

    # Identify which species were lost specifically in this step
    dep_excluded_ids = set(candidate_ids) - current_candidates
    dep_excluded_results = [{"id": eid, "reasons": ["excluded: no suitable host/partner plant available"]} for eid in dep_excluded_ids]

    return list(current_candidates), dep_excluded_results


def run_exclusion_rules(
    farm_data: Any,
    all_species: List[Any],
    rules_lookup: Dict[int, List[Any]],
    dep_lookup: Dict[int, List[int]],
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

                # Compare farm value to species threshold using rule's operator
                if _compare(farm_val, _get_val(rule, "operator"), _get_val(rule, "value")) is False:
                    reasons.append(f"excluded: {_get_val(rule, 'reason')}, farm value = {str(farm_val).strip().lower()}")

        ################################################################################
        # STORY 34: Ecological matching would go here (not implemented in this PR)
        # Something like this
        # func_reasons = _check_ecological_functions(sp, farm_data)
        # reasons.extend(func_reasons)
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

    # Biological Dependencies (Host Plants)
    # Runs last because it requires a finalised list of viable host candidates.
    final_candidates, dep_excluded = _check_biological_dependencies(candidates, dep_lookup)

    # Merge dependency failures into the final excluded list
    excluded.extend(dep_excluded)

    return {
        "candidate_ids": final_candidates,
        "excluded_species": excluded,
    }


def _get_val(obj, key, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)
