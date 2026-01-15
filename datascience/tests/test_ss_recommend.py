import pytest
from suitability_scoring.recommend import (
    assign_dense_ranks,
    build_species_recommendations,
)


@pytest.fixture
def sample_species_list():
    """
    A list of species dictionaries with raw scores.
    """
    return [
        {
            "species_id": 101,
            "species_name": "Eucalyptus",
            "mcda_score": 0.8567,
            "features": {
                "rainfall": {"short_name": "rain", "reason": "Acceptable", "score": 1.0}
            },
        },
        {
            "species_id": 102,
            "species_name": "Acacia",
            "mcda_score": 0.8567,  # Tie with 101
            "features": {
                "soil_texture": {
                    "short_name": "soil",
                    "reason": "alright",
                    "score": 0.5,
                }
            },
        },
        {
            "species_id": 103,
            "species_name": "Banksia",
            "mcda_score": 0.400,  # Lower score
            "features": {},  # Empty features handling
        },
    ]


@pytest.fixture
def mock_scorer_output(sample_species_list):
    """
    Simulates the return value of mcda_scorer.
    """
    return sample_species_list, []


def test_assign_dense_ranks_basic():
    """
    Check standard dense ranking behaviour.
    """
    items = [{"score": 10}, {"score": 8}, {"score": 8}, {"score": 5}]
    ranks = assign_dense_ranks(items, score_key="score")
    assert ranks == [1, 2, 2, 3]


def test_assign_dense_ranks_empty():
    """
    Check empty list handling.
    """
    assert assign_dense_ranks([]) == []


def test_assign_dense_ranks_missing_key():
    """
    Check handling where score key is missing (defaults to 0).
    """
    items = [{"score": 10}, {}]  # Second item has no score -> 0
    ranks = assign_dense_ranks(items, score_key="score")
    assert ranks == [1, 2]


def test_build_species_recommendations_sorting_and_content(sample_species_list):
    """
    Check that recommendations are:
    - Sorted by score descending
    - Sorted by id ascending
    - Uses dense ranking
    - Formatted correctly (rounding, reason extraction)
    """
    recs = build_species_recommendations(sample_species_list)

    # Check sorting
    # Both have score 0.8567.
    # 101 comes before 102 numerically, so 101 should be first.
    assert recs[0]["species_id"] == 101
    assert recs[1]["species_id"] == 102
    assert recs[2]["species_id"] == 103

    # Check dense ranking
    assert recs[0]["rank_overall"] == 1
    assert recs[1]["rank_overall"] == 1  # Tie
    assert recs[2]["rank_overall"] == 2

    # Check formatting
    assert recs[0]["score_mcda"] == pytest.approx(0.857)  # Rounded to 3 decimal places
    assert recs[0]["key_reasons"] == ["rain:acceptable"]  # "short_name:reason.lower()"

    # Check Missing Features handling (Banksia)
    assert recs[2]["key_reasons"] == []
