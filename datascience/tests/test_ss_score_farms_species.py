import pytest
import pandas as pd
from suitability_scoring.scoring.scoring import score_farms_species_by_id_list


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
                "score_method": "num_range",
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
def farms_df():
    """
    Returns a DataFrame with two farms.
    """
    return pd.DataFrame(
        [
            {"farm_id": 101, "ph": 6.5, "soil_texture": "clay"},
            {"farm_id": 102, "ph": 4.0, "soil_texture": "sand"},
        ]
    )


@pytest.fixture
def species_df():
    """
    Returns a DataFrame with species profiles.
    """
    return pd.DataFrame(
        [
            {
                "species_id": 1,
                "scientific_name": "Tree A",
                "species_common_name": "Common A",
                "ph_min": 6.0,
                "ph_max": 7.0,
                "preferred_soil_texture": "clay",
            },
            {
                "species_id": 2,
                "scientific_name": "Tree B",
                "species_common_name": "Common B",
                "ph_min": 4.0,
                "ph_max": 5.0,
                "preferred_soil_texture": "sand",
            },
        ]
    )


@pytest.fixture
def params_index():
    """
    Returns default params index.
    """
    return {}  # relying on get_feature_params defaults


def test_scoring_exact_match(farms_df, species_df, basic_cfg, params_index):
    """
    Checks if Farm 101 gets a 1.0 score for Species 1.
    """

    # Define a valid set filter
    def get_valid_tree_ids(farm_row):
        return [1, 2]

    scores, explanations = score_farms_species_by_id_list(
        farms_df, species_df, basic_cfg, get_valid_tree_ids, params_index
    )

    # Filter for Farm 101 and Species A
    result = scores[(scores["farm_id"] == 101) & (scores["species_id"] == 1)]

    assert not result.empty, "Farm 101 / Species 1 row is missing."

    # Expect 1.0 because 6.5 is between 6.0-7.0 AND clay == clay
    assert result.iloc[0]["mcda_score"] == pytest.approx(1.0)


def test_scoring_mismatch(farms_df, species_df, basic_cfg, params_index):
    """
    Checks if Farm 101 gets a 0.0 score for Species 2.
    (Species 2 needs acidic sand, Farm 101 is neutral clay)
    """

    def get_valid_tree_ids(farm_row):
        return [1, 2]

    scores, _ = score_farms_species_by_id_list(
        farms_df, species_df, basic_cfg, get_valid_tree_ids, params_index
    )

    result = scores[(scores["farm_id"] == 101) & (scores["species_id"] == 2)]

    # Expect 0.0 because ph is out of range AND soil_texture mismatch
    assert result.iloc[0]["mcda_score"] == pytest.approx(0.0)


def test_missing_numeric_data(basic_cfg, params_index):
    """
    Checks handling of missing numeric data in both the species and the farm.
    """
    farms_df = pd.DataFrame(
        [
            {"farm_id": 101, "ph": 6.5, "soil_texture": "clay"},
            {"farm_id": 102, "ph": None, "soil_texture": "sand"},
        ]
    )

    # Create a species row with missing data
    species_df = pd.DataFrame(
        [
            {
                "species_id": 1,
                "scientific_name": "Tree A",
                "species_common_name": "Common A",
                "ph_min": None,
                "ph_max": 7.0,
                "preferred_soil_texture": "clay",
            },
            {
                "species_id": 2,
                "scientific_name": "Tree A",
                "species_common_name": "Common A",
                "ph_min": 6.0,
                "ph_max": None,
                "preferred_soil_texture": "clay",
            },
        ]
    )

    def get_valid_tree_ids(farm_row):
        return [1, 2]

    scores, explanations = score_farms_species_by_id_list(
        farms_df, species_df, basic_cfg, get_valid_tree_ids, params_index
    )

    # First species should report missing data for the ph score
    assert explanations[101][0]["features"]["ph"]["reason"] == "missing data"

    # Second species should report missing data for the ph score
    assert explanations[101][1]["features"]["ph"]["reason"] == "missing data"

    # Second farm should report missing data for the ph score
    assert explanations[102][0]["features"]["ph"]["reason"] == "missing data"


def test_missing_categorical(basic_cfg, params_index):
    """
    Checks handling missing categorical data either from the species of the farm.
    """
    farms_df = pd.DataFrame(
        [
            {"farm_id": 101, "ph": 6.5, "soil_texture": None},
            {"farm_id": 102, "ph": 4.0, "soil_texture": "sand"},
        ]
    )

    # Create a species row with missing data
    species_df = pd.DataFrame(
        [
            {
                "species_id": 1,
                "scientific_name": "Tree A",
                "species_common_name": "Common A",
                "ph_min": 6.0,
                "ph_max": 7.0,
                "preferred_soil_texture": "clay",
            },
            {
                "species_id": 2,
                "scientific_name": "Tree B",
                "species_common_name": "Common B",
                "ph_min": 4.0,
                "ph_max": 5.0,
                "preferred_soil_texture": None,
            },
        ]
    )

    def get_valid_tree_ids(farm_row):
        return [1, 2]

    scores, explanations = score_farms_species_by_id_list(
        farms_df, species_df, basic_cfg, get_valid_tree_ids, params_index
    )

    # First species should report missing or no preference for the soil_texture score
    assert (
        explanations[101][0]["features"]["soil_texture"]["reason"]
        == "missing or no preference"
    )

    # Second species should report missing data for the ph score
    assert (
        explanations[102][1]["features"]["soil_texture"]["reason"]
        == "missing or no preference"
    )


def test_zero_denominator(basic_cfg, params_index):
    """
    Checks handling each feature retuning a None score, therefore giving a denominator of 0.
    """
    farms_df = pd.DataFrame([{"farm_id": 102, "ph": None, "soil_texture": None}])

    # Create a species row with missing data
    species_df = pd.DataFrame(
        [
            {
                "species_id": 1,
                "scientific_name": "Tree A",
                "species_common_name": "Common A",
                "ph_min": None,
                "ph_max": 7.0,
                "preferred_soil_texture": "clay",
            }
        ]
    )

    def get_valid_tree_ids(farm_row):
        return [1]

    scores, explanations = score_farms_species_by_id_list(
        farms_df, species_df, basic_cfg, get_valid_tree_ids, params_index
    )

    result = scores[(scores["farm_id"] == 102) & (scores["species_id"] == 1)]

    # Expect 0.0 because all features return a None score
    assert result.iloc[0]["mcda_score"] == pytest.approx(0.0)


def test_unknown_ids_handling_empty_subset(
    farms_df, species_df, basic_cfg, params_index
):
    """
    Checks if the function handles IDs returned by 'get_valid_tree_ids'
    that do not exist in 'species_df'. This version only has unknown IDs so checks the
    handing of unknown IDs when the subset dataframe is empty.
    """
    # Only run this for the first farm
    single_farm = farms_df.head(1)

    def get_valid_tree_ids(farm_row):
        return [99]

    scores, explanations = score_farms_species_by_id_list(
        single_farm, species_df, basic_cfg, get_valid_tree_ids, params_index
    )

    # Scores should be empty (no valid species match found in dataframe)
    assert scores.empty

    # Explanations should contain a note about the missing ID
    farm_id = single_farm.iloc[0]["farm_id"]
    farm_exp = explanations[farm_id]

    # Check the list structure
    assert any(" unknown species_id(s)" in str(item) for item in farm_exp)


def test_unknown_ids_handling(farms_df, species_df, basic_cfg, params_index):
    """
    Checks if the function handles IDs returned by 'get_valid_tree_ids'
    that do not exist in 'species_df'.
    """
    # Only run this for the first farm
    single_farm = farms_df.head(1)

    def get_valid_tree_ids(farm_row):
        return [1, 99]

    scores, explanations = score_farms_species_by_id_list(
        single_farm, species_df, basic_cfg, get_valid_tree_ids, params_index
    )

    # Explanations should contain a note about the missing ID
    farm_id = single_farm.iloc[0]["farm_id"]
    farm_exp = explanations[farm_id]

    # Check the list structure
    assert any(" unknown species_id(s)" in str(item) for item in farm_exp)


def test_empty_ids(farms_df, species_df, basic_cfg, params_index):
    """
    Checks if the function handles no IDs returned by 'get_valid_tree_ids'.
    """
    # Only run this for the first farm
    single_farm = farms_df.head(1)

    def get_valid_tree_ids(farm_row):
        return None

    scores, explanations = score_farms_species_by_id_list(
        single_farm, species_df, basic_cfg, get_valid_tree_ids, params_index
    )

    # Scores should be empty (no valid species match found in dataframe)
    assert scores.empty
    assert explanations[101] == []


def test_unknown_numeric_scorer(farms_df, species_df, params_index):
    """
    Check the function raise a ValueError when an unknown numeric score is selected.
    """
    cfg = {
        "ids": {"farm": "farm_id", "species": "species_id"},
        "names": {"species_name": "scientific_name"},
        "features": {
            "ph": {
                "type": "numeric",
                "short": "ph",
                "score_method": "magic",
                "default_weight": 0.50,
            }
        },
    }

    def get_valid_tree_ids(farm_row):
        return [1]

    with pytest.raises(
        ValueError, match="Unknown numeric scoring method 'magic' for 'ph'"
    ):
        scores, explanations = score_farms_species_by_id_list(
            farms_df, species_df, cfg, get_valid_tree_ids, params_index
        )


def test_unknown_categorical_scorer(farms_df, species_df, params_index):
    """
    Checks the function raise a ValueError when an unknown categorical scorer is selected.
    """
    cfg = {
        "ids": {"farm": "farm_id", "species": "species_id"},
        "names": {"species_name": "scientific_name"},
        "features": {
            "soil_texture": {
                "type": "categorical",
                "short": "soil",
                "score_method": "magic",
                "categorical": {"exact_match": 1.0},
                "default_weight": 0.50,
            }
        },
    }

    def get_valid_tree_ids(farm_row):
        return [1]

    with pytest.raises(
        ValueError, match="Unknown categorical mode 'magic' for feature 'soil_texture'"
    ):
        scores, explanations = score_farms_species_by_id_list(
            farms_df, species_df, cfg, get_valid_tree_ids, params_index
        )


def test_unknown_feature_type(farms_df, species_df, params_index):
    """
    Checks the function raise a ValueError when an unknown feature type is specified.
    """
    cfg = {
        "ids": {"farm": "farm_id", "species": "species_id"},
        "names": {"species_name": "scientific_name"},
        "features": {
            "ph": {
                "type": "number",
                "short": "ph",
                "score_method": "num_range",
                "default_weight": 0.50,
            }
        },
    }

    def get_valid_tree_ids(farm_row):
        return [1]

    with pytest.raises(ValueError, match="Unknown feature type 'number' for 'ph'"):
        scores, explanations = score_farms_species_by_id_list(
            farms_df, species_df, cfg, get_valid_tree_ids, params_index
        )
