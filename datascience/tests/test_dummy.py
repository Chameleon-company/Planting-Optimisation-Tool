import os
import sys

from exclusion_rules.dummy_run import run_exclusion_rules


# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)


def test_dummy_exclusion_rules_returns_all_candidates():
    # Farm uses "id" now (was farm_id)
    farm_data = {
        "id": 1,
        "rainfall": 1200,
        "temperature": 24,
        "soil_type": "Loam",
    }

    # Species uses "id" now (was species_id)
    species_data = [
        {"id": 1, "species_name": "Acacia"},
        {"id": 2, "species_name": "Eucalyptus"},
        {"id": 3, "species_name": "Ficus"},
    ]

    config = {}

    result = run_exclusion_rules(farm_data, species_data, config)

    assert "candidate_ids" in result
    assert "excluded_species" in result

    assert result["candidate_ids"] == [1, 2, 3]
    assert result["excluded_species"] == []
