import pytest
from suitability_scoring.scoring.scoring import categorical_compatibility_score


@pytest.fixture
def basic_cfg():
    """
    Returns a minimal configuration dictionary.
    """
    return {
        "ids": {"farm": "farm_id", "species": "species_id"},
        "names": {"species_name": "scientific_name"},
        "features": {
            "soil_texture": {
                "type": "categorical",
                "short": "soil",
                "score_method": "cat_compatibility",
                "default_weight": 0.50,
                "compatibility_pairs": {
                    "sand": {"sand": 1.0, "loam": 0.4, "silt": 0.1, "clay": 0.0},
                    "loam": {"sand": 0.4, "loam": 1.0, "silt": 0.6, "clay": 0.3},
                    "silt": {"sand": 0.1, "loam": 0.6, "silt": 1.0, "clay": 0.3},
                    "clay": {"sand": 0.0, "loam": 0.3, "silt": 0.3, "clay": 1.0},
                },
            },
        },
    }


@pytest.mark.parametrize(
    "value, preferred_list, expected_score, expected_reason",
    [
        # exact match
        ("clay", ["clay", "sand"], 1.0, "exact match"),
        # compatibility match
        ("loam", ["clay", "sand"], 0.4, "closest compatibility match sand at 0.40"),
        # multiple compatibility matches
        (
            "clay",
            ["loam", "silt"],
            0.3,
            "closest compatibility match loam at 0.30. closest compatibility match silt at 0.30",
        ),
        # case sensitivity: 'clay' != 'Clay'
        ("clay", ["Clay"], 0.0, "no_match"),
    ],
)
def test_matches_and_non_matches_default_score(
    value, preferred_list, expected_score, expected_reason, basic_cfg
):
    """
    Checks the categorical compatibility scoring function returns the expected value for matching
      and non-matching conditions.
    """
    cat_cfg = basic_cfg["features"]["soil_texture"]["compatibility_pairs"]
    score, reason = categorical_compatibility_score(value, preferred_list, cat_cfg)

    assert score == pytest.approx(expected_score)
    assert reason == expected_reason


@pytest.mark.parametrize(
    "value, preferred_list, expected_score, expected_reason",
    [
        # No farm
        (None, ["clay", "sand"], None, "missing farm data"),
        # No species
        ("loam", [], None, "missing species data"),
    ],
)
def test_missing_values_return_none(
    value, preferred_list, expected_score, expected_reason, basic_cfg
):
    """
    Checks missing values return None as a score. Tests for different types of missing.
    """
    cat_cfg = basic_cfg["features"]["soil_texture"]["compatibility_pairs"]
    score, reason = categorical_compatibility_score(value, preferred_list, cat_cfg)

    assert score == pytest.approx(expected_score)
    assert reason == expected_reason
