# Task 11 - Scenario test cases for exclusion rules
# Covers:
# - dynamic operator rules via config["rules"]
# - no dependencies / single dependency / chain dependency / circular dependency
# - checks behaviour without changing core logic structure

import pandas as pd

from exclusion_rules.run_exclusion_core_logic import run_exclusion_rules


def _base_farm() -> dict:
    return {
        "id": 1,
        "rainfall_mm": 700,
        "temperature_celsius": 20,
        "elevation_m": 100,
        "ph": 6.5,
        "soil_texture": "loam",
    }


def _simple_species_df(rows: list[dict]) -> pd.DataFrame:
    """
    Helper: create a species DataFrame with only fields needed for the test.
    """
    return pd.DataFrame(rows)


def _dependency_df(rows: list[dict]) -> pd.DataFrame:
    """
    Helper: dependencies file sometimes has trailing spaces in headers.
    We intentionally use 'Good_tree_partners ' (with a trailing space)
    to match real-world messy data.
    """
    return pd.DataFrame(rows)


# ------------------------------------------------------------
# 1) Dynamic operator-based rule (example: temperature > 15)
# ------------------------------------------------------------
def test_task11_dynamic_operator_rule_temperature_gt_15():
    """
    Task 11:
    Add an operator-based rule dynamically (temperature > 15).
    This test assumes your core logic supports reading rules from config["rules"].

    Expected:
    - farm temperature = 20 passes
    - if we set threshold to 25, farm fails and species should be excluded
    """
    farm = _base_farm()

    # We create a "threshold" as a per-species column so the engine can compare
    # farm_val vs species_val without any hard-coded logic.
    species_df = _simple_species_df(
        [
            {
                "id": 101,
                "name": "S1",
                "common_name": "S1",
                "temp_threshold": 15,
            },
            {
                "id": 102,
                "name": "S2",
                "common_name": "S2",
                "temp_threshold": 25,
            },
        ]
    )

    config = {
        "dependency": {"enabled": False},
        # Task 11: dynamic rule
        "rules": [
            {
                "id": "temp_gt_threshold",
                # Use direct column names so you don't need to change mapping code
                "farm_col": "temperature_celsius",
                "species_col": "temp_threshold",
                "op": ">",
                "reason": "excluded: temperature not above threshold",
            }
        ],
    }

    out = run_exclusion_rules(farm, species_df, config=config, dependencies_df=None)

    assert 101 in out["candidate_ids"]
    assert 102 not in out["candidate_ids"]

    excluded_102 = next(e for e in out["excluded_species"] if e["id"] == 102)
    assert any(
        "excluded: temperature not above threshold" in r
        for r in excluded_102["reasons"]
    )


# ------------------------------------------------------------
# 2) Species with NO dependencies
# ------------------------------------------------------------
def test_species_with_no_dependencies_stays_candidate():
    farm = _base_farm()

    species_df = _simple_species_df(
        [
            {"id": 201, "name": "Acacia", "common_name": "Acacia"},
            {
                "id": 202,
                "name": "Eucalyptus",
                "common_name": "Eucalyptus",
            },
        ]
    )

    # dependency enabled, but dependency table is empty => no exclusions
    dep_df = _dependency_df([])

    config = {"dependency": {"enabled": True}, "rules": []}

    out = run_exclusion_rules(farm, species_df, config=config, dependencies_df=dep_df)

    assert set(out["candidate_ids"]) == {201, 202}
    assert out["excluded_species"] == []


# ------------------------------------------------------------
# 3) Single dependency (A requires B or C)
# ------------------------------------------------------------
def test_single_dependency_excludes_when_no_partner_present():
    farm = _base_farm()

    # Only "Santalum album" is present, but none of its required partners are present
    species_df = _simple_species_df(
        [
            {
                "id": 301,
                "name": "Santalum album",
                "common_name": "Sandalwood",
            },
        ]
    )

    dep_df = _dependency_df(
        [
            {
                "Focal_species": "Santalum album",
                # Trailing space in header name is intentional
                "Good_tree_partners ": "Acacia, Eucalyptus",
            }
        ]
    )

    config = {
        "dependency": {"enabled": True},
        "rules": [],  # ignore environmental rules for this test
    }

    out = run_exclusion_rules(farm, species_df, config=config, dependencies_df=dep_df)

    assert 301 not in out["candidate_ids"]
    excluded_301 = next(e for e in out["excluded_species"] if e["id"] == 301)
    assert any("excluded: no suitable host plant" in r for r in excluded_301["reasons"])


def test_single_dependency_passes_when_partner_present():
    farm = _base_farm()

    # Now include one valid partner (Acacia)
    species_df = _simple_species_df(
        [
            {
                "id": 401,
                "name": "Santalum album",
                "common_name": "Sandalwood",
            },
            {"id": 402, "name": "Acacia", "common_name": "Acacia"},
        ]
    )

    dep_df = _dependency_df(
        [
            {
                "Focal_species": "Santalum album",
                "Good_tree_partners ": "Acacia, Eucalyptus",
            }
        ]
    )

    config = {"dependency": {"enabled": True}, "rules": []}

    out = run_exclusion_rules(farm, species_df, config=config, dependencies_df=dep_df)

    assert 401 in out["candidate_ids"]
    assert 402 in out["candidate_ids"]
    assert out["excluded_species"] == []


# ------------------------------------------------------------
# 4) Chain dependency (A -> B, B -> C)
# ------------------------------------------------------------
def test_dependency_chain_excludes_upstream_when_chain_breaks():
    """
    Task 11:
    Chains of dependencies.
    We structure rows so that B->C is evaluated before A->B.
    That makes a single pass produce the expected chain effect:
      - C missing => B excluded
      - B excluded => A excluded
    """
    farm = _base_farm()

    species_df = _simple_species_df(
        [
            {"id": 501, "name": "A", "common_name": "A"},
            {"id": 502, "name": "B", "common_name": "B"},
            # C is missing on purpose
        ]
    )

    dep_df = _dependency_df(
        [
            {"Focal_species": "B", "Good_tree_partners ": "C"},
            {"Focal_species": "A", "Good_tree_partners ": "B"},
        ]
    )

    config = {"dependency": {"enabled": True}, "rules": []}

    out = run_exclusion_rules(farm, species_df, config=config, dependencies_df=dep_df)

    assert 501 not in out["candidate_ids"]
    assert 502 not in out["candidate_ids"]

    excluded_ids = {e["id"] for e in out["excluded_species"]}
    assert excluded_ids == {501, 502}


# ------------------------------------------------------------
# 5) Circular dependency (A -> B, B -> A)
# ------------------------------------------------------------
def test_circular_dependency_does_not_crash_and_is_stable():
    """
    Task 11:
    Edge case - circular dependency.
    A requires B, and B requires A.
    Current safe behaviour:
      - both remain candidates (because each has a partner present)
      - function should NOT crash or loop forever
    """
    farm = _base_farm()

    species_df = _simple_species_df(
        [
            {"id": 601, "name": "A", "common_name": "A"},
            {"id": 602, "name": "B", "common_name": "B"},
        ]
    )

    dep_df = _dependency_df(
        [
            {"Focal_species": "A", "Good_tree_partners ": "B"},
            {"Focal_species": "B", "Good_tree_partners ": "A"},
        ]
    )

    config = {"dependency": {"enabled": True}, "rules": []}

    out = run_exclusion_rules(farm, species_df, config=config, dependencies_df=dep_df)

    assert set(out["candidate_ids"]) == {601, 602}
    assert out["excluded_species"] == []
