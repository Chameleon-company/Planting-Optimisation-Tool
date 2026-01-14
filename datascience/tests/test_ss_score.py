import pytest
from suitability_scoring.scoring.scoring import calculate_suitability
from suitability_scoring.utils.params import build_rules_dict


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
                "default_weight": 0.50,
            },
        },
    }


@pytest.fixture
def second_cfg():
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


@pytest.fixture
def farms():
    """
    Returns a list with two farms.
    """
    return [
        {"farm_id": 101, "ph": 6.5, "soil_texture": "clay"},
        {"farm_id": 102, "ph": 4.0, "soil_texture": "sand"},
    ]


@pytest.fixture
def species():
    """
    Returns a list with species profiles.
    """
    return [
        {
            "species_id": 1,
            "scientific_name": "Tree A",
            "species_common_name": "Common A",
            "ph_min": 6.0,
            "ph_max": 7.0,
            "soil_textures": "clay",
        },
        {
            "species_id": 2,
            "scientific_name": "Tree B",
            "species_common_name": "Common B",
            "ph_min": 4.5,
            "ph_max": 5.0,
            "soil_textures": "sand",
        },
    ]


@pytest.fixture
def params_index():
    """
    Returns default params index.
    """
    return {}  # relying on get_feature_params defaults


def test_scoring_exact_match(farms, species, basic_cfg, params_index):
    """
    Checks if Farm 101 gets a 1.0 score for Species 1.
    """

    rules = build_rules_dict(species, params_index, basic_cfg)

    explanations, scores = calculate_suitability(farms[0], species, rules, basic_cfg)

    # Filter for Farm 101 and Species A
    result = scores[0]

    # Expect 1.0 because 6.5 is between 6.0-7.0 AND clay == clay
    assert result[1] == pytest.approx(1.0)


def test_scoring_exact_match2(farms, species, second_cfg, params_index):
    """
    Checks if Farm 101 gets a 1.0 score for Species 1.
    """

    rules = build_rules_dict(species, params_index, second_cfg)

    explanations, scores = calculate_suitability(farms[0], species, rules, second_cfg)

    # Filter for Farm 101 and Species A
    result = scores[0]

    # Expect 1.0 because 6.5 is between 6.0-7.0 AND clay == clay
    assert result[1] == pytest.approx(1.0)


def test_scoring_mismatch(farms, species, basic_cfg, params_index):
    """
    Checks if Farm 101 gets a 0.0 score for Species 2.
    (Species 2 needs acidic sand, Farm 101 is neutral clay)
    """

    rules = build_rules_dict(species, params_index, basic_cfg)

    _, scores = calculate_suitability(farms[0], species, rules, basic_cfg)

    result = scores[1]

    # Expect 0.0 because ph is out of range AND soil_texture mismatch
    assert result[1] == pytest.approx(0.0)

    explanations, scores = calculate_suitability(farms[1], species, rules, basic_cfg)

    # Second species should report below minimum for the ph score
    assert explanations[1]["features"]["ph"]["reason"] == "below minimum"


def test_missing_numeric_data(basic_cfg, params_index):
    """
    Checks handling of missing numeric data in both the species and the farm.
    """
    farms = [
        {"farm_id": 101, "ph": 6.5, "soil_texture": "clay"},
        {"farm_id": 102, "ph": None, "soil_texture": "sand"},
    ]

    # Create a species row with missing data
    species = [
        {
            "species_id": 1,
            "scientific_name": "Tree A",
            "species_common_name": "Common A",
            "ph_min": None,
            "ph_max": 7.0,
            "soil_textures": "clay",
        },
        {
            "species_id": 2,
            "scientific_name": "Tree A",
            "species_common_name": "Common A",
            "ph_min": 6.0,
            "ph_max": None,
            "soil_textures": "clay",
        },
    ]

    rules = build_rules_dict(species, params_index, basic_cfg)

    explanations, scores = calculate_suitability(farms[0], species, rules, basic_cfg)

    # First species should report missing data for the ph score
    assert explanations[0]["features"]["ph"]["reason"] == "missing species data"

    # Second species should report missing data for the ph score
    assert explanations[1]["features"]["ph"]["reason"] == "missing species data"

    explanations, scores = calculate_suitability(farms[1], species, rules, basic_cfg)

    # Second farm should report missing data for the ph score
    assert explanations[0]["features"]["ph"]["reason"] == "missing farm data"


def test_incorrect_type_numeric_data(basic_cfg, params_index):
    """
    Checks handling of wrong type for numeric data in both the species and the farm.
    """
    farms = [
        {"farm_id": 101, "ph": "6.5", "soil_texture": "clay"},
    ]

    # Create a species row with missing data
    species = [
        {
            "species_id": 1,
            "scientific_name": "Tree A",
            "species_common_name": "Common A",
            "ph_min": "s",
            "ph_max": 7.0,
            "soil_textures": "clay",
        }
    ]

    rules = build_rules_dict(species, params_index, basic_cfg)

    explanations, scores = calculate_suitability(farms[0], species, rules, basic_cfg)

    # First species should report missing data for the ph score
    assert explanations[0]["features"]["ph"]["reason"] == "missing data"


def test_missing_categorical(basic_cfg, params_index):
    """
    Checks handling missing categorical data either from the species of the farm.
    """
    farms = [
        {"farm_id": 101, "ph": 6.5, "soil_texture": None},
        {"farm_id": 102, "ph": 4.0, "soil_texture": "sand"},
    ]

    # Create a species row with missing data
    species = [
        {
            "species_id": 1,
            "scientific_name": "Tree A",
            "species_common_name": "Common A",
            "ph_min": 6.0,
            "ph_max": 7.0,
            "soil_textures": "clay",
        },
        {
            "species_id": 2,
            "scientific_name": "Tree B",
            "species_common_name": "Common B",
            "ph_min": 4.0,
            "ph_max": 5.0,
            "soil_textures": None,
        },
    ]

    rules = build_rules_dict(species, params_index, basic_cfg)

    explanations, scores = calculate_suitability(farms[0], species, rules, basic_cfg)

    # First species should report missing or no preference for the soil_texture score
    assert (
        explanations[0]["features"]["soil_texture"]["reason"]
        == "missing or no preference"
    )

    # Second species should report missing or no preference for the soil_texture score
    assert (
        explanations[1]["features"]["soil_texture"]["reason"]
        == "missing or no preference"
    )


def test_zero_denominator(basic_cfg, params_index):
    """
    Checks handling each feature retuning a None score, therefore giving a denominator of 0.
    """
    farms = [{"farm_id": 102, "ph": None, "soil_texture": None}]

    # Create a species row with missing data
    species = [
        {
            "species_id": 1,
            "scientific_name": "Tree A",
            "species_common_name": "Common A",
            "ph_min": None,
            "ph_max": 7.0,
            "soil_textures": "clay",
        }
    ]

    rules = build_rules_dict(species, params_index, basic_cfg)

    explanations, scores = calculate_suitability(farms[0], species, rules, basic_cfg)

    result = scores[0]

    # Expect 0.0 because all features return a None score
    assert result[1] == pytest.approx(0.0)


def test_unknown_numeric_scorer(farms, species, params_index):
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

    rules = build_rules_dict(species, params_index, cfg)

    with pytest.raises(
        ValueError, match="Unknown numeric scoring method 'magic' for 'ph'"
    ):
        scores, explanations = calculate_suitability(farms[0], species, rules, cfg)


def test_unknown_categorical_scorer(farms, species, params_index):
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

    rules = build_rules_dict(species, params_index, cfg)

    with pytest.raises(
        ValueError, match="Unknown categorical mode 'magic' for feature 'soil_texture'"
    ):
        scores, explanations = calculate_suitability(farms[0], species, rules, cfg)


def test_unknown_feature_type(farms, species, params_index):
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

    rules = build_rules_dict(species, params_index, cfg)

    with pytest.raises(ValueError, match="Unknown feature type 'number' for 'ph'"):
        scores, explanations = calculate_suitability(farms[0], species, rules, cfg)


def test_numerical_trapezoid(params_index):
    """
    Checks scoring for a single numeric feature using trapezoid.
    """
    cfg = {
        "ids": {"farm": "farm_id", "species": "species_id"},
        "names": {"species_name": "scientific_name"},
        "features": {
            "rainfall_mm": {
                "type": "numeric",
                "short": "rainfall",
                "score_method": "trapezoid",
                "tolerance": {"left": 250, "right": 500},
                "default_weight": 0.50,
            },
        },
    }

    farms = [
        {"farm_id": 101, "rainfall_mm": 1000, "soil_texture": "clay"},
    ]

    # Create a species row
    species = [
        {
            "species_id": 1,
            "scientific_name": "Tree A",
            "species_common_name": "Common A",
            "rainfall_mm_min": 500,
            "rainfall_mm_max": 2000,
            "soil_textures": "clay",
        }
    ]

    rules = build_rules_dict(species, params_index, cfg)

    explanations, scores = calculate_suitability(farms[0], species, rules, cfg)

    # First species should report missing data for the ph score
    assert (
        explanations[0]["features"]["rainfall_mm"]["reason"]
        == "within plateau [750.0, 1500.0]"
    )
    # Expect 1.0 because rainfall is within plateau  AND clay == clay
    assert scores[0][1] == pytest.approx(1.0)


def test_categorical_compatibility(params_index):
    """
    Checks scoring for a single categorical feature using cat_compatibility.
    """
    cfg = {
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

    farms = [
        {"farm_id": 101, "soil_texture": "clay"},
    ]

    # Create a species row with missing data
    species = [
        {
            "species_id": 1,
            "scientific_name": "Tree A",
            "species_common_name": "Common A",
            "soil_textures": ["loam", "silt"],
        }
    ]

    rules = build_rules_dict(species, params_index, cfg)

    explanations, scores = calculate_suitability(farms[0], species, rules, cfg)

    # First species should report missing data for the ph score
    assert (
        explanations[0]["features"]["soil_texture"]["reason"]
        == "closest compatibility match loam at 0.30. closest compatibility match silt at 0.30"
    )
    # Expect 0.3 because  clay:loam == 0.3
    assert scores[0][1] == pytest.approx(0.3)
