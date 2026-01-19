import pytest
from datetime import datetime, timezone
from app.orchestrators import (
    get_recommendations_service,
    get_batch_recommendations_service,
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


def test_get_recommendations_service_timestamp(mocker, sample_species_list):
    """
    Check that timestamp is generated correctly using a mock.
    """
    # Define the fixed time
    fixed_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # Patch the datetime class in 'app.orchestrators'
    # Create a mock object that behaves like the datetime class
    mock_dt = mocker.patch("app.orchestrators.datetime")
    mock_dt.now.return_value = fixed_time

    # Run the function
    result = get_recommendations_service(1)

    # Assert
    assert result["timestamp_utc"] == "2025-01-01T12:00:00Z"


def test_get_recommendations_service(mocker, mock_scorer_output):
    """
    Check that the single farm payload builder calls the scorer correctly.
    """

    # Patch the scorer function
    mocker.patch(
        "app.orchestrators.calculate_suitability",
        return_value=mock_scorer_output,
    )

    # Run the function
    result = get_recommendations_service(1)

    # Check the result for the farm
    assert result["farm_id"] == 1
    assert len(result["recommendations"]) == 3


def test_get_batch_recommendations_service(mocker, mock_scorer_output):
    """
    Check that multiple farms are processed in one scorer batch.
    """

    # Patch
    mocker.patch(
        "app.orchestrators.calculate_suitability",
        return_value=mock_scorer_output,
    )

    # Run
    farm_ids = [1, 2]
    results = get_batch_recommendations_service(farm_ids)

    # Check the results are a list
    assert isinstance(results, list)

    # Check there 2 results
    assert len(results) == 2

    # Check first farm
    assert results[0]["farm_id"] == 1
    assert len(results[0]["recommendations"]) == 3

    # Check second farm
    assert results[1]["farm_id"] == 2
    assert len(results[1]["recommendations"]) == 3
