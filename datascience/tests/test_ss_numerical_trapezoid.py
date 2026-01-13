import re
import pytest
from suitability_scoring.scoring.scoring import (
    derive_trapezoid_from_minmax,
    numerical_trapezoid_score,
)


def test_derive_trapezoid_from_minmax():
    """
    Test calculation of trapezoid points for valid inputs
    """
    a, b, c, d = derive_trapezoid_from_minmax(10.0, 20.0, 2, 4)
    assert (a, b, c, d) == (10.0, 12.0, 16.0, 20.0)


def test_derive_trapezoid_from_minmax_max_none():
    """
    Test calculation of trapezoid points for max = None
    """
    with pytest.raises(ValueError, match="min/max cannot be None."):
        derive_trapezoid_from_minmax(10.0, None, 2, 4)


def test_derive_trapezoid_from_minmax_max_lt_min():
    """
    Test calculation of trapezoid points for max < min
    """
    msg = "max (10.0) < min (20.0)"
    with pytest.raises(ValueError, match=re.escape(msg)):
        derive_trapezoid_from_minmax(20.0, 10.0, 2, 4)


def test_derive_trapezoid_from_minmax_high_tol():
    """
    Test calculation of trapezoid points for tolerance > width
    """

    a, b, c, d = derive_trapezoid_from_minmax(10.0, 20.0, 15, 4)
    assert (a, b, c, d) == (10.0, 15.0, 15.0, 20.0)


def test_trapezoid_score_farm_missing():
    """
    Test trapezoid scoring for missing farm data
    """
    s, r, o = numerical_trapezoid_score(None, 10, 20, 2, 4)
    assert s is None
    assert r == "missing farm data"


def test_trapezoid_score_species_missing():
    """
    Test trapezoid scoring for missing species data
    """
    s, r, o = numerical_trapezoid_score(15, None, 20, 2, 4)
    assert s is None
    assert r == "missing species data"


def test_trapezoid_score_low_farm():
    """
    Test trapezoid scoring for low farm value
    """
    s, r, o = numerical_trapezoid_score(8, 10, 20, 2, 4)
    assert s == pytest.approx(0.0)
    assert r == "below minimum"


def test_trapezoid_score_high_farm():
    """
    Test trapezoid scoring for high farm value
    """
    s, r, o = numerical_trapezoid_score(22, 10, 20, 2, 4)
    assert s == pytest.approx(0.0)
    assert r == "above maximum"


def test_trapezoid_score_shoulders():
    """
    Test trapezoid scoring in shoulder regions
    """
    # min = a = 18, max = d = 24 -> width = 6
    # left_tol = 0.6 -> b = 18+0.6 = 18.6
    # right_tol = 3 -> c = 24-3 = 21.0
    a, b, c, d = derive_trapezoid_from_minmax(18.0, 24.0, 0.6, 3)
    assert a == pytest.approx(18.0)
    assert b == pytest.approx(18.6)
    assert c == pytest.approx(21.0)
    assert d == pytest.approx(24.0)

    # Shoulders midpoint ~ 0.5
    s, r, o = numerical_trapezoid_score((a + b) / 2, a, d, 0.6, 3)
    assert s == pytest.approx(0.5)
    assert r == "within left shoulder [18.0, 18.6]"

    s, r, o = numerical_trapezoid_score((c + d) / 2, a, d, 0.6, 3)
    assert s == pytest.approx(0.5)
    assert r == "within right shoulder [21.0, 24.0]"

    # Shoulder endpoints = 0.0
    s, r, o = numerical_trapezoid_score(a, a, d, 0.6, 3)
    assert s == pytest.approx(0.0)
    assert r == "within left shoulder [18.0, 18.6]"

    s, r, o = numerical_trapezoid_score(d, a, d, 0.6, 3)
    assert s == pytest.approx(0.0)
    assert r == "within right shoulder [21.0, 24.0]"


def test_trapezoid_score_plateau():
    """
    Test trapezoid scoring in shoulder regions
    """
    # min = a = 18, max = d = 24 -> width = 6
    # left_tol = 0.6 -> b = 18+0.6 = 18.6
    # right_tol = 3 -> c = 24-3 = 21.0
    a, b, c, d = derive_trapezoid_from_minmax(18.0, 24.0, 0.6, 3)
    assert a == pytest.approx(18.0)
    assert b == pytest.approx(18.6)
    assert c == pytest.approx(21.0)
    assert d == pytest.approx(24.0)

    # Plateau midpoint = 1.0
    s, r, o = numerical_trapezoid_score((b + c) / 2, a, d, 0.6, 3)
    assert s == pytest.approx(1.0)
    assert r == "within plateau [18.6, 21.0]"

    # Plateau endpoints = 1.0
    s, r, o = numerical_trapezoid_score(b, a, d, 0.6, 3)
    assert s == pytest.approx(1.0)
    assert r == "within plateau [18.6, 21.0]"

    s, r, o = numerical_trapezoid_score(c, a, d, 0.6, 3)
    assert s == pytest.approx(1.0)
    assert r == "within plateau [18.6, 21.0]"


def test_trapezoid_score_zero_shoulder():
    """
    Test trapezoid scoring when should regions are zero
    """
    # min = a = 18, max = d = 24 -> width = 6
    # left_tol = 0.0 -> b = 18.0
    # right_tol = 0.0 -> c = 24.0
    a, b, c, d = derive_trapezoid_from_minmax(18.0, 24.0, 0.0, 0.0)
    assert a == pytest.approx(18.0)
    assert b == pytest.approx(18.0)
    assert c == pytest.approx(24.0)
    assert d == pytest.approx(24.0)

    # Shoulder endpoints = 1.0
    s, r, o = numerical_trapezoid_score(b, a, d, 0.0, 0.0)
    assert s == pytest.approx(1.0)
    assert r == "within plateau [18.0, 24.0]"

    s, r, o = numerical_trapezoid_score(c, a, d, 0.0, 0.0)
    assert s == pytest.approx(1.0)
    assert r == "within plateau [18.0, 24.0]"
