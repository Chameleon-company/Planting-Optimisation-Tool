import pytest
import pandas as pd
import numpy as np

from suitability_scoring.utils.params import (
    build_species_params_dict,
    get_feature_params,
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
                "default_weight": 0.50,
            },
            "soil_texture": {
                "type": "categorical",
                "short": "soil",
                "score_method": "cat_exact",
                "categorical": {"exact_match": 1.0},
                "default_weight": 0.50,
            },
        },
    }


@pytest.fixture
def species_params_df():
    """
    Returns a DataFrame with species parameters.
    """
    return pd.DataFrame(
        [
            {
                "species_id": 1,
                "feature": "ph",
                "score_method": "num_range",
                "weight": 0.3,
            },
            {
                "species_id": 1,
                "feature": "soil_texture",
                "score_method": "cat_exact",
                "weight": 0.7,
            },
            {
                "species_id": 2,
                "feature": "ph",
                "score_method": "num_range",
                "weight": 0.0,
            },
            {
                "species_id": 2,
                "feature": "soil_texture",
                "score_method": None,
                "weight": 0.8,
            },
            {
                "species_id": 3,
                "feature": "ph",
                "score_method": "num_range",
                "weight": 0.0,
            },
            {
                "species_id": 3,
                "feature": "soil_texture",
                "score_method": np.nan,
                "weight": np.nan,
            },
        ]
    )


def test_build_params_structure(species_params_df, basic_cfg):
    """
    Check that the dataFrame is correctly converted to a nested dictionary.
    """
    # Call function
    result = build_species_params_dict(species_params_df, basic_cfg)

    # Check if keys exist
    assert 1 in result
    assert "ph" in result[1]
    assert "soil_texture" in result[1]

    # Check values
    assert result[1]["ph"]["score_method"] == "num_range"
    assert result[1]["ph"]["weight"] == pytest.approx(0.3)
    assert result[1]["soil_texture"]["score_method"] == "cat_exact"
    assert result[1]["soil_texture"]["weight"] == pytest.approx(0.7)


def test_build_params_custom_id_column(basic_cfg):
    """
    Check that the function respects a custom ID column name defined in config.
    """
    # Modify config to look for 'species_key' instead of 'species_id'
    basic_cfg["ids"]["species"] = "species_key"

    # Create DF with that specific column
    df = pd.DataFrame(
        [
            {
                "species_key": 2,
                "feature": "rainfall",
                "score_method": "num_range",
                "weight": 0.3,
            }
        ]
    )

    result = build_species_params_dict(df, basic_cfg)

    assert 2 in result
    assert result[2]["rainfall"]["weight"] == pytest.approx(0.3)


def test_build_params_handles_missing_values(basic_cfg):
    """
    Check the function handles NaN or None values in the dataFrame.
    """
    df = pd.DataFrame(
        [{"species_id": 999, "feature": "ph", "score_method": None, "weight": np.nan}]
    )

    result = build_species_params_dict(df, basic_cfg)

    # Check that the keys exist, even if values are empty.
    assert "ph" in result[999]

    # Check for NaN
    assert np.isnan(result[999]["ph"]["weight"])


def test_get_params_full_override(species_params_df, basic_cfg):
    """
    Species exists in params_dict and has all values set.
    Expectation: Return the values from params_dict, ignore config defaults.
    """
    params_dict = build_species_params_dict(species_params_df, basic_cfg)

    result = get_feature_params(params_dict, basic_cfg, species_id=1, feature="ph")

    # Species 1 has a ph weight 0.3 (config default is 0.5)
    assert result["weight"] == pytest.approx(0.3)

    # Species 1 has a score_method of 'num_range' (config default is 'magic')
    assert result["score_method"] == "num_range"


def test_get_params_defaults_only(species_params_df, basic_cfg):
    """
    Species ID (999) is NOT in the params_dict.
    Expectation: Return purely the defaults from config.
    """
    params_dict = build_species_params_dict(species_params_df, basic_cfg)

    result = get_feature_params(params_dict, basic_cfg, species_id=999, feature="ph")

    # Should fall back to config values
    assert result["weight"] == pytest.approx(0.5)
    assert result["score_method"] == "magic"


def test_get_params_partial_fallback(species_params_df, basic_cfg):
    """
    Species exists, has a custom weight, but NO score_method.
    Expectation: Return custom weight, but default score_method.
    """
    params_dict = build_species_params_dict(species_params_df, basic_cfg)

    # Species 2 has a soil_texture weight 0.8, method is None
    result = get_feature_params(
        params_dict, basic_cfg, species_id=2, feature="soil_texture"
    )

    assert result["weight"] == pytest.approx(0.8)  # Specific
    assert result["score_method"] == "cat_exact"  # Default (fallback)

    # Species 3 has a soil_texture weight np.nan, method is np.nan
    result = get_feature_params(
        params_dict, basic_cfg, species_id=3, feature="soil_texture"
    )

    assert result["weight"] == pytest.approx(0.5)  # Default (fallback)
    assert result["score_method"] == "cat_exact"  # Default (fallback)


def test_get_params_zero_weight_edge_case(species_params_df, basic_cfg):
    """
    Feature has a weight explicitly set to 0.0.
    Expectation: Logic should treat 0.0 as a valid number, not as 'None'.
    It should NOT fall back to the default weight.
    """
    params_dict = build_species_params_dict(species_params_df, basic_cfg)

    result = get_feature_params(params_dict, basic_cfg, species_id=2, feature="ph")

    # Species 2 has a 'ph' weight 0.0. Default for 'ph' is 0.5.
    assert result["weight"] == pytest.approx(0.0)
    assert result["weight"] != pytest.approx(0.5)
