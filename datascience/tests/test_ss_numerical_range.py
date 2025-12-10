import pytest
from suitability_scoring.scoring.scoring import numerical_range_score


def test_numerical_range_inclusive_bounds():
    """
    Testing when the value is between the min and max values.
    numerical_range_score(value, min, max)
    """
    assert numerical_range_score(10, 5, 10) == pytest.approx(1.0)
    assert numerical_range_score(5, 5, 10) == pytest.approx(1.0)
    assert numerical_range_score(7.5, 5, 10) == 1.0


def test_numerical_range_outside_lower_and_upper():
    """
    Testing when the value is below the min value or above the max value.
    numerical_range_score(value, min, max)
    """
    assert numerical_range_score(4.99, 5, 10) == pytest.approx(0.0)
    assert numerical_range_score(10.01, 5, 10) == pytest.approx(0.0)


def test_numerical_range_missing_returns_none():
    """
    Testing when either the value, the min or the max value are missing.
    numerical_range_score(value, min, max)
    """

    assert numerical_range_score(None, 5, 10) is None
    assert numerical_range_score(7.5, None, 10) is None
    assert numerical_range_score(7.5, 5, None) is None


def test_numerical_range_type_casting_float_int():
    """
    Testing type casting of a float to int or int to float.
    numerical_range_score(value, min, max)
    """
    assert numerical_range_score(9, 8.0, 10.0) == pytest.approx(1.0)
    assert numerical_range_score(11.0, 8, 10) == pytest.approx(0.0)
