import pytest

from exclusion_rules.exclusion_core_logic import run_exclusion_rules_records


# Mock ORM-like object
class MockORM:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@pytest.mark.parametrize("farm_type", ["dict", "orm"])
@pytest.mark.parametrize("species_type", ["dict", "orm"])
def test_exclusion_agnosticism(farm_type, species_type):
    # Prepare farm input
    farm_dict = {
        "id": 1,
        "rainfall_mm": 500,
        "temperature_celsius": 20,
        "elevation_m": 100,
        "ph": 6.5,
        "soil_texture": "loam",
    }

    farm = farm_dict if farm_type == "dict" else MockORM(**farm_dict)

    # Prepare species input
    species_dict = {
        "id": 1,
        "name": "S1",
        "common_name": "S1",
        "rainfall_mm_min": 800,  # should be excluded
        "rainfall_mm_max": 1200,
        "temperature_celsius_min": 10,
        "temperature_celsius_max": 30,
        "elevation_m_min": 0,
        "elevation_m_max": 500,
        "ph_min": 5,
        "ph_max": 8,
        "soil_textures": ["loam"],
    }

    species = [species_dict if species_type == "dict" else MockORM(**species_dict)]

    result = run_exclusion_rules_records(farm, species)

    # Assertion: species should be excluded due to rainfall
    assert len(result["excluded_species"]) == 1
