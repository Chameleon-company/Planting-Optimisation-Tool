import pytest

from ahp.ahp_core import AhpCore


@pytest.fixture
def ahp():
    return AhpCore()


def test_perfect_consistency(ahp):
    """Test with a perfectly consistent matrix (Identity matrix)."""
    matrix = [[1, 1], [1, 1]]
    result = ahp.calculate_weights(matrix)

    assert result["consistency_ratio"] == 0.0
    assert result["is_consistent"] is True
    assert result["weights"] == [0.5, 0.5]


def test_tutorial_example(ahp):
    """
    Tests the specific Rainfall/Temperature/Soil texture example from the tutorial text.
    Matrix:
    [1,   1/3, 5]
    [3,   1,   7]
    [1/5, 1/7, 1]

    Expected Eigenvector (approx): [0.2790, 0.6491, 0.0719]
    Expected CR < 10%
    """
    matrix = [[1, 1 / 3, 5], [3, 1, 7], [1 / 5, 1 / 7, 1]]
    result = ahp.calculate_weights(matrix)

    weights = result["weights"]

    # Check weights match tutorial values (allowing small float error)
    assert 0.27 <= weights[0] <= 0.29  # Rainfall
    assert 0.64 <= weights[1] <= 0.66  # Temperature
    assert 0.06 <= weights[2] <= 0.08  # Soil Texture

    # Check consistency
    assert result["is_consistent"] is True
    assert result["consistency_ratio"] < 0.10


def test_inconsistent_matrix(ahp):
    """Test a logically impossible matrix (A > B, B > C, C > A)."""
    matrix = [[1, 5, 1 / 5], [1 / 5, 1, 5], [5, 1 / 5, 1]]
    result = ahp.calculate_weights(matrix)

    assert result["is_consistent"] is False
    assert result["consistency_ratio"] > 0.10
