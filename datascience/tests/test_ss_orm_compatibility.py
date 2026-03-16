import pytest

from suitability_scoring.scoring import calculate_suitability
from suitability_scoring.utils.accessors import get_val
from suitability_scoring.utils.params import build_rules_dict


# Mock ORM Class to simulate SQLAlchemy models
class MockORM:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@pytest.fixture
def base_config():
    """
    Provides the standard feature configuration.
    """
    return {
        "ids": {"species": "species_id"},
        "features": {
            "rainfall": {
                "short": "Rain",
                "type": "numeric",
                "score_method": "num_range",
                "default_weight": 0.50,
            }
        },
    }


@pytest.fixture
def sample_data():
    """
    Provides consistent sample species and farm data.
    """
    return {
        "species_id": 101,
        "species_name": "Eucalyptus globulus",
        "rainfall_min": 500,
        "rainfall_max": 1500,
        "farm_rainfall": 800,
    }


def test_get_val_logic(sample_data):
    """
    Verifies get_val handles both dict and objects identically.
    """
    as_dict = sample_data
    as_obj = MockORM(**sample_data)

    assert get_val(as_dict, "species_id") == 101
    assert get_val(as_obj, "species_id") == 101
    assert get_val(as_obj, "missing", "default") == "default"


def test_get_val_with_none():
    """
    Ensure utility handles None gracefully.
    """
    assert get_val(None, "any_key", default="fallback") == "fallback"


@pytest.mark.parametrize("farm_type", ["dict", "orm"])
@pytest.mark.parametrize("species_type", ["dict", "orm"])
def test_full_engine_agnosticism(farm_type, species_type, sample_data, base_config):
    """
    Verifies the engine produces identical results regardless of
    whether farm_data or species_list are dicts or ORM objects.
    """
    # Prepare Farm input
    farm_raw = {"rainfall": sample_data["farm_rainfall"]}
    farm_input = farm_raw if farm_type == "dict" else MockORM(**farm_raw)

    # Prepare Species input
    species_raw = {
        "species_id": sample_data["species_id"],
        "rainfall_min": sample_data["rainfall_min"],
        "rainfall_max": sample_data["rainfall_max"],
    }
    species_list_input = [species_raw if species_type == "dict" else MockORM(**species_raw)]

    # Build rules (this tests get_val inside params.py)
    rules = build_rules_dict(species_list_input, {}, base_config)

    # Run suitability (this tests get_val inside scoring.py)
    result_list, _ = calculate_suitability(
        farm_data=farm_input,
        species_list=species_list_input,
        optimised_rules=rules,
        cfg=base_config,
    )

    # Assertions
    result = result_list[0]
    assert result["species_id"] == 101
    assert result["mcda_score"] == 1.0  # 800 is within [500, 1500]
