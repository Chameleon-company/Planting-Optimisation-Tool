from typing import Any, Dict, List, Optional


def _compare(farm_val: Any, op: str, threshold_val: Any) -> Optional[bool]:
    """Compare a farm value against a threshold using the given operator.

    Args:
        farm_val: The value from farm data being evaluated.
        op: The comparison operator to apply.
        threshold_val: The threshold value from the rule.

    Returns:
        ``False`` when the farm value fails the exclusion check, ``True`` when
        it passes, or ``True`` when the comparison cannot be evaluated and the
        rule should not exclude the species.

    Raises:
        None: This function does not raise exceptions.
    """
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
    """Filter candidate species by recursively enforcing biological dependencies.

    The function removes species whose required partner species are no longer
    present in the candidate list. It continues iterating until the set reaches a
    stable state, so chained dependency failures are also removed.

    Args:
        candidate_ids: Species identifiers that have passed earlier exclusion checks.
        dep_lookup: Mapping of species identifiers to required partner species identifiers.

    Returns:
        A tuple containing the remaining candidate species identifiers and a list
        of dependency-based exclusion records.

    Raises:
        None: This function does not raise exceptions.
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


def _check_topographic_requirements(species: Any, farm: Any) -> list[str]:
    """
    Check species suitability against farm topographic requirements.

    Args:
        species: Species record evaluated for topographic compatibility.
        farm: Farm record containing topographic requirement flags.

    Returns:
        A list of exclusion reason messages. Empty when the species satisfies
        all topographic requirements.

    Raises:
        None: This function does not raise exceptions.
    """
    reasons = []

    # Mapping of farm 'demand' flags to species 'supply' flags
    checks = [
        ("riparian", "excluded: species is not suitable for riparian zones"),
        ("coastal", "excluded: species is not suitable for coastal zones"),
    ]

    for attr, msg in checks:
        # If the farm DEMANDS it (True), but the species lacks it (False/None)
        if _get_val(farm, attr) is True and not _get_val(species, attr):
            reasons.append(msg)

    return reasons


# Ecological function filtering
def _check_ecological_functions(species: Any, farm: Any) -> list[str]:
    reasons = []

    # Map of farm boolean → species attribute
    checks = [
        ("nitrogen_fixing", "excluded: species is not nitrogen fixing"),
        ("shade_tolerant", "excluded: species is not shade tolerant"),
        ("bank_stabilising", "excluded: species is not bank stabilising"),
    ]

    for attr, msg in checks:
        if _get_val(farm, attr) is True and not _get_val(species, attr, False):
            reasons.append(msg)

    return reasons


# Agroforestry type filtering
def _check_agroforestry_types(species: Any, farm: Any) -> list[str]:
    reasons = []

    farm_types_raw = _get_val(farm, "agroforestry_types", [])
    species_types_raw = _get_val(species, "agroforestry_types", [])

    # Normalize both to lowercase lists
    farm_types = [str(t).strip().lower() for t in farm_types_raw]
    species_types = [str(t).strip().lower() for t in species_types_raw]

    # If farm has no preference → allow
    if not farm_types:
        return reasons

    # Check intersection
    if not any(ft in species_types for ft in farm_types):
        reasons.append("excluded: not compatible with selected agroforestry types")

    return reasons


def run_exclusion_rules(
    farm_data: Any,
    all_species: List[Any],
    rules_lookup: Dict[int, List[Any]],
    dep_lookup: Dict[int, List[int]],
) -> Dict[str, Any]:
    """Apply all exclusion rules for a single farm.

    Args:
        farm_data: Farm-level data used to evaluate exclusion rules.
        all_species: All species records that should be evaluated.
        rules_lookup: Mapping of species identifiers to exclusion rules.
        dep_lookup: Mapping of species identifiers to biological dependencies.

    Returns:
        A dictionary containing the surviving candidate species identifiers and
        the full list of excluded species with reasons.

    Raises:
        None: This function does not raise exceptions.
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

        # Check topographic requirements
        topographic_reasons = _check_topographic_requirements(sp, farm_data)
        reasons.extend(topographic_reasons)

        # Ecological function filtering
        eco_reasons = _check_ecological_functions(sp, farm_data)
        reasons.extend(eco_reasons)

        # Agroforestry type filtering
        agro_reasons = _check_agroforestry_types(sp, farm_data)
        reasons.extend(agro_reasons)

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
    """Return a value from a mapping or object attribute lookup.

    Args:
        obj: A dictionary-like object or attribute-bearing object.
        key: The key or attribute name to retrieve.
        default: The value to return when the key or attribute is missing.

    Returns:
        The resolved value or ``default`` when the lookup fails.

    Raises:
        None: This function does not raise exceptions.
    """
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)
