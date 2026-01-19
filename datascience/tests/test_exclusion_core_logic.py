import pandas as pd

from exclusion_rules.run_exclusion_core_logic import run_exclusion_rules


def test_task7_filters_species_by_rainfall_id_schema():
    farm = {
        "id": 1,
        "rainfall_mm": 500,
        "temperature_celsius": 20,
        "elevation_m": 100,
        "ph": 6.5,
        "soil_texture": "loam",
    }

    species_df = pd.DataFrame(
        [
            {
                "id": 1,
                "species_name": "Acacia",
                "species_common_name": "Acacia",
                "rainfall_mm_min": 400,
                "rainfall_mm_max": 900,
                "temperature_celsius_min": 10,
                "temperature_celsius_max": 30,
                "elevation_m_min": 0,
                "elevation_m_max": 500,
                "ph_min": 5.5,
                "ph_max": 7.5,
                "preferred_soil_texture": "loam, clay",
                "costal": 0,
                "riparian": 0,
            },
            {
                "id": 2,
                "species_name": "Eucalyptus",
                "species_common_name": "Eucalyptus",
                "rainfall_mm_min": 800,
                "rainfall_mm_max": 1200,
                "temperature_celsius_min": 10,
                "temperature_celsius_max": 30,
                "elevation_m_min": 0,
                "elevation_m_max": 500,
                "ph_min": 5.5,
                "ph_max": 7.5,
                "preferred_soil_texture": "loam",
                "costal": 0,
                "riparian": 0,
            },
        ]
    )

    # Task 9: dependency disabled by default
    config = {
        "dependency": {"enabled": False},
        # Task 8: annotation config (keep values off for stable output)
        "annotation": {"include_values": False},
    }

    out = run_exclusion_rules(farm, species_df, config=config, dependencies_df=None)

    assert 1 in out["candidate_ids"]
    assert 2 not in out["candidate_ids"]

    excluded_ids = {e["id"] for e in out["excluded_species"]}
    assert 2 in excluded_ids

    # -----------------------
    # Task 8: reasons exist
    # -----------------------
    excluded_item = next(e for e in out["excluded_species"] if e["id"] == 2)
    assert "reasons" in excluded_item
    assert any(
        "excluded: rainfall below minimum" in r for r in excluded_item["reasons"]
    )


def test_task10_allows_dynamic_rule_with_direct_columns_no_code_change():
    """
    Task 10:
    Add a new operator-based rule via config, using direct column names:
      - farm_col: "temperature_celsius"
      - species_col: "temp_threshold"
    No code change required to support temp_threshold.
    """
    farm = {
        "id": 1,
        "rainfall_mm": 500,
        "temperature_celsius": 20,
        "elevation_m": 100,
        "ph": 6.5,
        "soil_texture": "loam",
    }

    # Add a custom species column "temp_threshold"
    species_df = pd.DataFrame(
        [
            {
                "id": 10,
                "species_name": "S1",
                "species_common_name": "S1",
                "temp_threshold": 15,
            },
            {
                "id": 11,
                "species_name": "S2",
                "species_common_name": "S2",
                "temp_threshold": 25,
            },
        ]
    )

    config = {
        "dependency": {"enabled": False},
        "annotation": {"include_values": True},  # Task 8 + Task 10 together
        "rules": [
            {
                "id": "temp_gt_threshold",
                "farm_col": "temperature_celsius",
                "species_col": "temp_threshold",
                "op": ">",
                "reason": "excluded: temperature not above threshold",
            }
        ],
    }

    out = run_exclusion_rules(farm, species_df, config=config, dependencies_df=None)

    # farm temp = 20 => passes S1 (15), fails S2 (25)
    assert 10 in out["candidate_ids"]
    assert 11 not in out["candidate_ids"]

    excluded_item = next(e for e in out["excluded_species"] if e["id"] == 11)
    assert any(
        "excluded: temperature not above threshold" in r
        for r in excluded_item["reasons"]
    )
    # include_values=True should add context
    assert any("farm=20" in r for r in excluded_item["reasons"])

    # -------------------------


# Task 12 - Unit Tests
# -------------------------


def test_task12_missing_species_value_skips_rule_no_exclusion():
    """
    Task 12:
    Missing species value should skip the rule and not exclude.
    """
    farm = {
        "id": 1,
        "rainfall_mm": 500,
        "temperature_celsius": 20,
        "elevation_m": 100,
        "ph": 6.5,
        "soil_texture": "loam",
    }

    # rainfall_mm_min missing => rain_min rule is skipped
    species_df = pd.DataFrame(
        [
            {
                "id": 1,
                "species_name": "S1",
                "species_common_name": "S1",
                "rainfall_mm_min": None,
                "rainfall_mm_max": 900,
                "preferred_soil_texture": "loam",
            }
        ]
    )

    config = {"dependency": {"enabled": False}, "annotation": {"include_values": False}}

    out = run_exclusion_rules(farm, species_df, config=config, dependencies_df=None)

    assert 1 in out["candidate_ids"]
    assert out["excluded_species"] == []


def test_task12_missing_farm_value_skips_rule_no_exclusion():
    """
    Task 12:
    Missing farm value should skip the rule and not exclude.
    """
    farm = {
        "id": 1,
        "rainfall_mm": None,
        "temperature_celsius": 20,
        "elevation_m": 100,
        "ph": 6.5,
        "soil_texture": "loam",
    }

    species_df = pd.DataFrame(
        [
            {
                "id": 1,
                "species_name": "S1",
                "species_common_name": "S1",
                "rainfall_mm_min": 400,
                "rainfall_mm_max": 900,
                "preferred_soil_texture": "loam",
            }
        ]
    )

    config = {"dependency": {"enabled": False}, "annotation": {"include_values": False}}

    out = run_exclusion_rules(farm, species_df, config=config, dependencies_df=None)

    assert 1 in out["candidate_ids"]
    assert out["excluded_species"] == []


def test_task12_in_set_operator_parses_multiple_separators():
    """
    Task 12:
    preferred_soil_texture parsing should accept ';' '/' etc.
    """
    farm = {
        "id": 1,
        "rainfall_mm": 500,
        "temperature_celsius": 20,
        "elevation_m": 100,
        "ph": 6.5,
        "soil_texture": "loam",
    }

    species_df = pd.DataFrame(
        [
            {
                "id": 1,
                "species_name": "S1",
                "species_common_name": "S1",
                "preferred_soil_texture": "clay; loam / sand",
            }
        ]
    )

    # Only keep soil rule to make test focused
    config = {
        "dependency": {"enabled": False},
        "annotation": {"include_values": False},
        "rules": [
            {
                "id": "soil_only",
                "farm_col": "soil_texture",
                "species_col": "preferred_soil_texture",
                "op": "in_set",
                "reason": "excluded: soil texture not supported",
            }
        ],
    }

    out = run_exclusion_rules(farm, species_df, config=config, dependencies_df=None)

    assert 1 in out["candidate_ids"]
    assert out["excluded_species"] == []


def test_task12_requires_true_rule_skips_when_flag_missing():
    """
    Task 12:
    If farm coastal flag missing, requires_true rule should be skipped (no exclusion).
    """
    farm = {
        "id": 1,
        "rainfall_mm": 500,
        "temperature_celsius": 20,
        "elevation_m": 100,
        "ph": 6.5,
        "soil_texture": "loam",
        # coastal flag missing on purpose
    }

    species_df = pd.DataFrame(
        [
            {"id": 1, "species_name": "S1", "species_common_name": "S1", "costal": 0},
        ]
    )

    config = {
        "dependency": {"enabled": False},
        "annotation": {"include_values": False},
        "rules": [
            {
                "id": "coastal_rule",
                "farm_col": "costal",
                "species_col": "costal",
                "op": "requires_true",
                "reason": "excluded: not suitable for coastal habitat",
            }
        ],
    }

    out = run_exclusion_rules(farm, species_df, config=config, dependencies_df=None)

    assert 1 in out["candidate_ids"]
    assert out["excluded_species"] == []
