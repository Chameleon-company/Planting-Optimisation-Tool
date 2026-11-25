from unittest.mock import Mock

import pandas as pd
import pytest

from src.survivability.prediction import generate_warnings, predict_survival, prepare_prediction_input


@pytest.fixture
def optima_df():
    return pd.DataFrame(
        {"species_name": ["Mango"], "rainfall_min": [1000], "rainfall_max": [2000], "temp_min": [20], "temp_max": [30], "alt_min": [100], "alt_max": [500], "ph_min": [5.5], "ph_max": [7.5]}
    )


def test_generate_warnings_optimal(optima_df):
    result = generate_warnings("Mango", 25, 1500, 300, 10, 6.5, optima_df, 0, 30)

    assert result == []


def test_generate_warnings_outside_range(optima_df):
    result = generate_warnings("Mango", 35, 2500, 600, 40, 8.0, optima_df, 0, 30)

    assert len(result) == 5


def test_generate_warnings_unknown_species(optima_df):
    result = generate_warnings("Unknown", 25, 1500, 300, 10, 6.5, optima_df, 0, 30)

    assert result == ["Species not found in optimal range table"]


def test_prepare_prediction_input(optima_df):
    result = prepare_prediction_input("Mango", 35, 2500, 600, 10, 8.0, 15, 3, 24, optima_df)

    assert result.shape == (1, 13)

    assert result["correct_tree_species_name"].iloc[0] == "Mango"
    assert result["age_months"].iloc[0] == 24
    assert result["trunk_circumference"].iloc[0] == 15

    assert result["rain_outside_opt"].iloc[0] == 500
    assert result["temp_outside_opt"].iloc[0] == 5
    assert result["elev_outside_opt"].iloc[0] == 100
    assert result["ph_outside_opt"].iloc[0] == 0.5


def test_prepare_prediction_input_unknown_species(optima_df):
    result = prepare_prediction_input("Unknown", 25, 1500, 300, 10, 6.5, 15, 3, 24, optima_df)

    assert result.shape == (1, 13)

    assert result["rain_outside_opt"].iloc[0] == 0
    assert result["temp_outside_opt"].iloc[0] == 0
    assert result["elev_outside_opt"].iloc[0] == 0
    assert result["ph_outside_opt"].iloc[0] == 0


def test_predict_survival_survived(optima_df):
    pipeline = Mock()
    pipeline.predict_proba.return_value = [[0.15, 0.85]]

    result = predict_survival("Mango", 25, 1500, 300, 10, 6.5, 15, 3, 24, optima_df, pipeline, 0.3, 0, 30)

    assert result["survival_probability"] == pytest.approx(85.0)
    assert result["prediction"] == "Survived"
    assert result["warnings"] == []

    pipeline.predict_proba.assert_called_once()


def test_predict_survival_died(optima_df):
    pipeline = Mock()
    pipeline.predict_proba.return_value = [[0.6, 0.4]]

    result = predict_survival("Mango", 35, 1500, 300, 10, 6.5, 15, 3, 24, optima_df, pipeline, 0.3, 0, 30)

    assert result["survival_probability"] == pytest.approx(40.0)
    assert result["prediction"] == "Died"
    assert len(result["warnings"]) == 1


def test_predict_survival_threshold_boundary(optima_df):
    pipeline = Mock()
    pipeline.predict_proba.return_value = [[0.3, 0.7]]

    result = predict_survival("Mango", 25, 1500, 300, 10, 6.5, 15, 3, 24, optima_df, pipeline, 0.3, 0, 30)

    assert result["prediction"] == "Died"
