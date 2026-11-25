import pandas as pd

from src.survivability.preprocessing import (
    calculate_environmental_features,
    calculate_tree_age,
    clean_environmental_data,
    clean_species_names,
    clean_tree_data,
    merge_farm_data,
    outside_range,
    prepare_model_input,
    preprocess_data,
    remove_invalid_records,
    select_model_features,
)


def test_calculate_tree_age():
    data = pd.DataFrame(
        {
            "scan_date": pd.to_datetime(["2026-11-15"]),
            "planted_year": [2024],
            "planted_month": [3],
        }
    )

    result = calculate_tree_age(data)

    assert result["age_months"].iloc[0] == 32


def test_outside_range():
    # Value within the optimal range
    assert outside_range(25, 20, 30) == 0

    # Value above the optimal range
    assert outside_range(35, 20, 30) == 5

    # Value below the optimal range
    assert outside_range(18, 20, 30) == 2


def test_calculate_environmental_features():
    df = pd.DataFrame({"correct_tree_species_name": ["Mango"], "rain_mean": [1500], "temp_mean": [35], "elev_mean": [100], "ph": [5.0]})

    optima_df = pd.DataFrame(
        {"species_name": ["Mango"], "rainfall_min": [1000], "rainfall_max": [2000], "temp_min": [20], "temp_max": [30], "alt_min": [200], "alt_max": [1000], "ph_min": [6.0], "ph_max": [7.0]}
    )

    result = calculate_environmental_features(df, optima_df)

    assert result["rain_outside_opt"].iloc[0] == 0
    assert result["temp_outside_opt"].iloc[0] == 5
    assert result["elev_outside_opt"].iloc[0] == 100
    assert result["ph_outside_opt"].iloc[0] == 1.0


def test_remove_invalid_records():
    df = pd.DataFrame({"trunk_circumference": [10, None, 20], "age_months": [12, 24, None]})

    result = remove_invalid_records(df)

    assert len(result) == 1
    assert result["trunk_circumference"].iloc[0] == 10
    assert result["age_months"].iloc[0] == 12


def test_preprocess_data():
    df = pd.DataFrame(
        {
            "correct_tree_species_name": ["Mango", "Mango"],
            "scan_date": ["2026-11-15", "2026-11-15"],
            "planted_year": [2024, 2024],
            "planted_month": [3, 3],
            "trunk_circumference": [20, None],
            "rain_mean": [1500, 1500],
            "temp_mean": [35, 35],
            "elev_mean": [100, 100],
            "ph": [5.0, 5.0],
        }
    )

    optima_df = pd.DataFrame(
        {"species_name": ["Mango"], "rainfall_min": [1000], "rainfall_max": [2000], "temp_min": [20], "temp_max": [30], "alt_min": [200], "alt_max": [1000], "ph_min": [6.0], "ph_max": [7.0]}
    )

    result = preprocess_data(df, optima_df)

    assert len(result) == 1
    assert result["age_months"].iloc[0] == 32
    assert result["rain_outside_opt"].iloc[0] == 0
    assert result["temp_outside_opt"].iloc[0] == 5
    assert result["elev_outside_opt"].iloc[0] == 100
    assert result["ph_outside_opt"].iloc[0] == 1.0


def test_select_model_features():
    df = pd.DataFrame(
        {
            "temp_mean": [25],
            "rain_mean": [1500],
            "elev_mean": [300],
            "slope_mean": [10],
            "ph": [6.5],
            "correct_tree_species_name": ["Mango"],
            "trunk_circumference": [20],
            "planted_month": [3],
            "age_months": [32],
            "rain_outside_opt": [0],
            "temp_outside_opt": [0],
            "elev_outside_opt": [0],
            "ph_outside_opt": [0],
            "survived": [1],
        }
    )

    result = select_model_features(df)

    assert result.shape == (1, 13)

    assert list(result.columns) == [
        "temp_mean",
        "rain_mean",
        "elev_mean",
        "slope_mean",
        "ph",
        "correct_tree_species_name",
        "trunk_circumference",
        "planted_month",
        "age_months",
        "rain_outside_opt",
        "temp_outside_opt",
        "elev_outside_opt",
        "ph_outside_opt",
    ]

    assert "survived" not in result.columns


def test_clean_tree_data():
    df = pd.DataFrame({"trunk_circumference": ["20", "invalid", "30", "40"], "planted_year": ["2024", "2023", None, "2024"], "planted_month": ["3", "5", "6", None]})

    result = clean_tree_data(df)

    assert len(result) == 1
    assert result["trunk_circumference"].iloc[0] == 20
    assert result["planted_year"].iloc[0] == 2024
    assert result["planted_month"].iloc[0] == 3


def test_clean_species_names():
    df = pd.DataFrame({"tree_species": ["eucalyptus", "ai-kamelii", "ai-bubur", "Ai- mahony"]})

    result = clean_species_names(df)

    assert result["correct_tree_species_name"].tolist() == ["Ai-bubur (mutin)", "Ai-kamelli", "Ai-bubur (mutin)", "Ai-mahony"]


def test_merge_farm_data():
    tree_df = pd.DataFrame({"farm_id": [1, 2], "tree_species": ["Mango", "Mahogany"]})

    farm_df = pd.DataFrame({"farm_id": [1, 2], "ph": [6.5, 7.0], "rainfall_mm": [1500, 2000], "temperature_celsius": [25, 30], "elevation_m": [300, 500], "slope": [10, 15]})

    result = merge_farm_data(tree_df, farm_df)

    assert len(result) == 2
    assert result["temp_mean"].tolist() == [25, 30]
    assert result["rain_mean"].tolist() == [1500, 2000]
    assert result["elev_mean"].tolist() == [300, 500]
    assert result["slope_mean"].tolist() == [10, 15]
    assert result["ph"].tolist() == [6.5, 7.0]
    assert "rainfall_mm" not in result.columns


def test_clean_environmental_data():
    df = pd.DataFrame({"temp_mean": [25, None, 30], "rain_mean": [1500, 2000, 1800], "elev_mean": [300, 500, 400], "slope_mean": [10, 15, 20], "ph": [6.5, 7.0, None]})

    result = clean_environmental_data(df)

    assert len(result) == 1
    assert result["temp_mean"].iloc[0] == 25
    assert result["ph"].iloc[0] == 6.5


def test_prepare_model_input():
    tree_df = pd.DataFrame(
        {
            "farm_id": [1, 2],
            "tree_species": ["Mango", "Mango"],
            "scan_date": ["2026-11-15", "2026-11-15"],
            "planted_year": ["2024", "2024"],
            "planted_month": ["3", "3"],
            "trunk_circumference": ["20", "invalid"],
        }
    )

    farm_df = pd.DataFrame({"farm_id": [1, 2], "ph": [5.0, 6.5], "rainfall_mm": [1500, 1800], "temperature_celsius": [35, 25], "elevation_m": [100, 300], "slope": [10, 15]})

    optima_df = pd.DataFrame(
        {"species_name": ["Mango"], "rainfall_min": [1000], "rainfall_max": [2000], "temp_min": [20], "temp_max": [30], "alt_min": [200], "alt_max": [1000], "ph_min": [6.0], "ph_max": [7.0]}
    )

    result = prepare_model_input(tree_df, farm_df, optima_df)

    assert result.shape == (1, 13)
    assert result["correct_tree_species_name"].iloc[0] == "Mango"
    assert result["trunk_circumference"].iloc[0] == 20
    assert result["age_months"].iloc[0] == 32
    assert result["rain_outside_opt"].iloc[0] == 0
    assert result["temp_outside_opt"].iloc[0] == 5
    assert result["elev_outside_opt"].iloc[0] == 100
    assert result["ph_outside_opt"].iloc[0] == 1.0
    assert result["slope_mean"].iloc[0] == 10


def test_clean_species_names_preserves_canonical_name():
    df = pd.DataFrame({"tree_species": ["Ai-bubur (mutin)", "Ai-bubur(mutin)"]})

    result = clean_species_names(df)

    assert result["correct_tree_species_name"].tolist() == ["Ai-bubur (mutin)", "Ai-bubur (mutin)"]
