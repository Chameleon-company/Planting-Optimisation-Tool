import pytest

from suitability_scoring.utils.params import (
    build_rules_dict,
    build_species_params_dict,
    get_feature_params,
    parse_prefs,
)


@pytest.fixture
def basic_cfg():
    """
    Returns a minimal configuration dictionary.
    """
    return {
        "ids": {"farm": "farm_id", "species": "species_id"},
        "names": {"species_name": "scientific_name"},
        "features": {
            "ph": {
                "type": "numeric",
                "short": "ph",
                "score_method": "magic",
                "tolerance": {"left": 0.25, "right": 0.6},
                "default_weight": 0.50,
            },
            "soil_texture": {
                "type": "categorical",
                "short": "soil",
                "score_method": "cat_exact",
                "default_weight": 0.50,
            },
        },
    }


@pytest.fixture
def species_params_rows():
    """
    Returns a list of dictionaries with species parameters.
    """
    return [
        {
            "species_id": 1,
            "feature": "ph",
            "score_method": "num_range",
            "weight": 0.3,
            "trap_left_tol": 0,
            "trap_right_tol": 0.5,
        },
        {
            "species_id": 1,
            "feature": "soil_texture",
            "score_method": "cat_exact",
            "weight": 0.7,
            "trap_left_tol": None,
            "trap_right_tol": None,
        },
        {
            "species_id": 2,
            "feature": "ph",
            "score_method": "num_range",
            "weight": 0.0,
            "trap_left_tol": None,
            "trap_right_tol": 0.5,
        },
        {
            "species_id": 2,
            "feature": "soil_texture",
            "score_method": None,
            "weight": 0.8,
            "trap_left_tol": None,
            "trap_right_tol": None,
        },
        {
            "species_id": 3,
            "feature": "ph",
            "score_method": "num_range",
            "weight": 0.0,
            "trap_left_tol": None,
            "trap_right_tol": None,
        },
        {
            "species_id": 3,
            "feature": "soil_texture",
            "score_method": "",
            "weight": "",
            "trap_left_tol": "",
            "trap_right_tol": "",
        },
    ]


@pytest.fixture
def simple_species_list():
    return [
        {
            "species_id": 1,
            "ph_min": 5.5,
            "ph_max": 7.0,
            "soil_textures": "loam",
        }
    ]


def test_build_params_structure(species_params_rows, basic_cfg):
    """
    Check that the dataFrame is correctly converted to a nested dictionary.
    """
    # Call function
    result = build_species_params_dict(species_params_rows, basic_cfg)

    # Check if keys exist
    assert 1 in result
    assert "ph" in result[1]
    assert "soil_texture" in result[1]

    # Check values
    assert result[1]["ph"]["score_method"] == "num_range"
    assert result[1]["ph"]["weight"] == pytest.approx(0.3)
    assert result[1]["ph"]["trap_left_tol"] == pytest.approx(0.0)
    assert result[1]["ph"]["trap_right_tol"] == pytest.approx(0.5)
    assert result[1]["soil_texture"]["score_method"] == "cat_exact"
    assert result[1]["soil_texture"]["weight"] == pytest.approx(0.7)


def test_build_params_handles_exceptions(basic_cfg):
    """
    Check the function handles exceptions.
    """
    rows = [{"species_id": 999, "feature": "ph", "score_method": 1, "weight": "large"}]

    result = build_species_params_dict(rows, basic_cfg)

    # Check that the keys exist, even if values are empty.
    assert "ph" in result[999]

    # Check for None
    assert result[999]["ph"]["weight"] is None


def test_build_params_handles_missing_values(basic_cfg):
    """
    Check the function handles None values in the data.
    """
    rows = [{"species_id": 999, "feature": "ph", "score_method": None, "weight": None}]

    result = build_species_params_dict(rows, basic_cfg)

    # Check that the keys exist, even if values are empty.
    assert "ph" in result[999]

    # Check for None
    assert result[999]["ph"]["weight"] is None


def test_get_params_full_override(species_params_rows, basic_cfg):
    """
    Species exists in params_dict and has all values set.
    Expectation: Return the values from params_dict, ignore config defaults.
    """
    params_dict = build_species_params_dict(species_params_rows, basic_cfg)

    result = get_feature_params(params_dict, basic_cfg, species_id=1, feature="ph")

    # Species 1 has a ph weight 0.3 (config default is 0.5)
    assert result["weight"] == pytest.approx(0.3)

    # Species 1 has a score_method of 'num_range' (config default is 'magic')
    assert result["score_method"] == "num_range"

    # Species 1 has a ph trap_left_tol 0.0 (config default is 0.25)
    assert result["trap_left_tol"] == pytest.approx(0.0)

    # Species 1 has a ph trap_right_tol 0.5 (config default is 0.6)
    assert result["trap_right_tol"] == pytest.approx(0.5)


def test_get_params_defaults_only(species_params_rows, basic_cfg):
    """
    Species ID (999) is NOT in the params_dict.
    Expectation: Return purely the defaults from config.
    """
    params_dict = build_species_params_dict(species_params_rows, basic_cfg)

    result = get_feature_params(params_dict, basic_cfg, species_id=999, feature="ph")

    # Should fall back to config values
    assert result["weight"] == pytest.approx(0.5)
    assert result["score_method"] == "magic"
    assert result["trap_left_tol"] == pytest.approx(0.25)
    assert result["trap_right_tol"] == pytest.approx(0.6)


def test_get_params_partial_fallback(species_params_rows, basic_cfg):
    """
    Species exists, has a custom weight, but NO score_method.
    Expectation: Return custom weight, but default score_method.
    """
    params_dict = build_species_params_dict(species_params_rows, basic_cfg)

    # Species 2 has a soil_texture weight 0.8, method is None
    result = get_feature_params(params_dict, basic_cfg, species_id=2, feature="soil_texture")

    assert result["weight"] == pytest.approx(0.8)  # Specific
    assert result["score_method"] == "cat_exact"  # Default (fallback)

    # Species 3 has a soil_texture weight np.nan, method is np.nan
    result = get_feature_params(params_dict, basic_cfg, species_id=3, feature="soil_texture")

    assert result["weight"] == pytest.approx(0.5)  # Default (fallback)
    assert result["score_method"] == "cat_exact"  # Default (fallback)

    # Species 2 has a ph trap_right_tol 0.5, trap_left_tol is None
    result = get_feature_params(params_dict, basic_cfg, species_id=2, feature="ph")
    assert result["trap_right_tol"] == pytest.approx(0.5)  # Specific
    assert result["trap_left_tol"] == pytest.approx(0.25)  # Default (fallback)


def test_get_params_zero_weight_edge_case(species_params_rows, basic_cfg):
    """
    Feature has a weight explicitly set to 0.0.
    Expectation: Logic should treat 0.0 as a valid number, not as 'None'.
    It should NOT fall back to the default weight.
    """
    params_dict = build_species_params_dict(species_params_rows, basic_cfg)

    result = get_feature_params(params_dict, basic_cfg, species_id=2, feature="ph")

    # Species 2 has a 'ph' weight 0.0. Default for 'ph' is 0.5.
    assert result["weight"] == pytest.approx(0.0)
    assert result["weight"] != pytest.approx(0.5)


def test_parse_prefs_none_returns_empty_list():
    """
    Checks a None preference returns and empty list.
    """
    assert parse_prefs(None) == []


def test_parse_prefs_list_passthrough():
    """
    Checks a list of preferences is passed through.
    """
    src = ["loam", "sandy loam"]
    out = parse_prefs(src)
    assert out is src  # function returns the same list object
    assert out == ["loam", "sandy loam"]


def test_parse_prefs_simple_string_split_and_strip():
    """
    Checks a single string is split into a list correctly.
    """
    assert parse_prefs("loam, sandy loam,clay") == ["loam", "sandy loam", "clay"]
    assert parse_prefs("  loam ,  sandy loam , clay  ") == [
        "loam",
        "sandy loam",
        "clay",
    ]


def test_parse_prefs_empty_string_results_in_single_empty_item():
    """
    Checks and empty string is returned as single empty item.
    """
    assert parse_prefs("") == [""]


def test_parse_prefs_trailing_comma_preserves_empty_item():
    """
    Checks trailing commas returns and empty item.
    """
    assert parse_prefs("clay,") == ["clay", ""]


def test_parse_prefs_only_spaces_become_empty_item_after_strip():
    """
    Checks only spaces become and empty item.
    """
    assert parse_prefs("   ") == [""]


def test_parse_prefs_non_string_non_list_non_none_returns_none():
    """
    Checks numbers are returned as None.
    """
    assert parse_prefs(123) is None
    assert parse_prefs(3.14) is None


def test_build_rules_no_global_weights(
    simple_species_list,
    species_params_rows,
    basic_cfg,
):
    """
    Check that the rules are built correctly when no global weights are provided.
     - Species 1 has a ph weight 0.3 and soil_texture weight 0.7.
     - After normalisation, the weights should be unchanged.
     - The score methods should be as per the params_dict.
     - The tolerances should be as per the params_dict.
     - The feature names should be as per the config 'short' names.
     - The species name should be as per the config 'species_name' field.
     - The species_id should be included in the output for reference.
     - The rules list should contain one rule for each feature of the species.
     - The overall structure of the output should match the expected format.
     - No global weights are applied, so the weights should reflect only the species-specific values.
     - The sum of the weights for all features of the species should equal 1.0 after normalisation.
     - The function should handle missing values in the params_dict gracefully, using defaults where necessary.
    """
    params_dict = build_species_params_dict(species_params_rows, basic_cfg)

    rules = build_rules_dict(
        simple_species_list,
        params_dict,
        basic_cfg,
        global_weights=None,
    )

    rules_list = rules[1]

    weights = {r["feat"]: r["weight"] for r in rules_list}

    # Original species weights: ph=0.3, soil=0.7
    # After normalisation, they should be unchanged
    assert weights["ph"] == pytest.approx(0.3)
    assert weights["soil_texture"] == pytest.approx(0.7)
    assert sum(weights.values()) == pytest.approx(1.0)


def test_build_rules_with_complete_global_weights(
    simple_species_list,
    species_params_rows,
    basic_cfg,
):
    """
    Check that the rules are built correctly when complete global weights are provided.
     - Species 1 has a ph weight 0.3 and soil_texture weight 0.7.
     - Global weights are provided for both features.
     - The final weights should be the product of the species-specific and global weights.
    """
    params_dict = build_species_params_dict(species_params_rows, basic_cfg)

    global_weights = {
        "ph": 0.2,
        "soil_texture": 0.8,
    }

    rules = build_rules_dict(
        simple_species_list,
        params_dict,
        basic_cfg,
        global_weights=global_weights,
    )

    rules_list = rules[1]
    weights = {r["feat"]: r["weight"] for r in rules_list}

    # Raw (before normalisation):
    # ph:   0.3 × 0.2 = 0.06
    # soil: 0.7 × 0.8 = 0.56
    total = 0.06 + 0.56

    assert weights["ph"] == pytest.approx(0.06 / total)
    assert weights["soil_texture"] == pytest.approx(0.56 / total)
    assert sum(weights.values()) == pytest.approx(1.0)


def test_build_rules_incomplete_global_weights_fallbacks_to_uniform(
    simple_species_list,
    species_params_rows,
    basic_cfg,
):
    """Check that the rules are built correctly when incomplete global weights are provided.
    - Species 1 has a ph weight 0.3 and soil_texture weight 0.7.
    - Global weight is provided for 'ph' but missing for 'soil_texture'.
    - The function should treat the missing global weight as 1.0 (no adjustment) for 'soil_texture'.
    - The final weights should be calculated using a value of 1.0 for all features.
    - The sum of the final weights should equal 1.0 after normalisation.
    """
    params_dict = build_species_params_dict(species_params_rows, basic_cfg)

    # Missing soil_texture → incomplete
    global_weights = {
        "ph": 0.2,
    }

    rules = build_rules_dict(
        simple_species_list,
        params_dict,
        basic_cfg,
        global_weights=global_weights,
    )

    rules_list = rules[1]
    weights = {r["feat"]: r["weight"] for r in rules_list}

    # Should behave like "no global weights"
    assert weights["ph"] == pytest.approx(0.3)
    assert weights["soil_texture"] == pytest.approx(0.7)
    assert sum(weights.values()) == pytest.approx(1.0)


def test_build_rules_zero_species_weight_preserved(
    simple_species_list,
    species_params_rows,
    basic_cfg,
):
    """
    Check that a species weight of zero is preserved even when global weights are applied.
    - Species 2 has a ph weight of 0.0 in the params_dict.
    - Global weights are provided for both features.
    - The final weight for 'ph' should remain 0.0, demonstrating that the function correctly treats zero as a valid weight and does not override it with global weights or defaults.
    - The final weight for 'soil_texture' should be calculated using the global weight and the species-specific weight from the params_dict.
    - The sum of the final weights should equal 1.0 after normalisation, with 'ph' contributing 0.0 and 'soil_texture' contributing the remainder.
    """
    params_dict = build_species_params_dict(species_params_rows, basic_cfg)

    # Species 2 has ph weight = 0.0
    species_list = [{"species_id": 2, "ph_min": 5.0, "ph_max": 8.0, "soil_textures": "loam"}]

    global_weights = {
        "ph": 0.5,
        "soil_texture": 0.5,
    }

    rules = build_rules_dict(
        species_list,
        params_dict,
        basic_cfg,
        global_weights=global_weights,
    )

    rules_list = rules[2]
    weights = {r["feat"]: r["weight"] for r in rules_list}

    # ph should remain zero
    assert weights["ph"] == pytest.approx(0.0)
    assert weights["soil_texture"] == pytest.approx(1.0)
