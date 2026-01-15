import pytest
from suitability_scoring.scoring.scoring import categorical_exact_score


@pytest.mark.parametrize(
    "value, preferred_list, expected",
    [
        # exact match
        ("clay", ["clay", "sand"], 1.0),
        (42, [1, 42, 100], 1.0),
        # non-match
        ("loam", ["clay", "sand"], 0.0),
        (3.14, [1.0, 2.0], 0.0),
        # case sensitivity: 'clay' != 'Clay'
        ("clay", ["Clay"], 0.0),
    ],
)
def test_matches_and_non_matches_default_score(value, preferred_list, expected):
    """
    Checks the categorical exact match function returns the expected value for matching
      and non-matching conditions.
    """
    assert categorical_exact_score(value, preferred_list) == pytest.approx(expected)


@pytest.mark.parametrize("missing", [None])
def test_missing_values_return_none(missing):
    """
    Checks missing values return None as a score. Tests for different types of missing.
    """
    assert categorical_exact_score(missing, ["clay", "loam"]) is None


def test_non_match_returns_zero():
    """
    Checks that a non-match returns a zero score
    """
    assert categorical_exact_score("clay", ["loam", "clay loam"]) == pytest.approx(0.0)


def test_preferred_list_with_duplicates_and_none():
    """
    Checks that the presence of None in preferred_list should not affect matching
    """
    assert categorical_exact_score("clay", ["clay", None, "clay"]) == pytest.approx(1.0)
    assert categorical_exact_score("loam", ["clay", None, "clay"]) == pytest.approx(0.0)


def test_type_strictness():
    """
    Checks type strictness is adhered asa non-match and returns a zero score.
    """
    # '1' (str) is not equal to 1 (int)
    assert categorical_exact_score("1", [1, 2]) == pytest.approx(0.0)
