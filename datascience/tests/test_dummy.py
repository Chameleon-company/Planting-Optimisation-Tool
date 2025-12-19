import os
import sys

from exclusion_rules.dummy_run import run_exclusion_rules

# Add datascience/src to Python path so we can import exclusion_rules
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC_DIR)


def test_dummy_exclusion_rules_returns_all_candidates():
    farm_data = {"rainfall": 1200, "temperature": 24, "soil_type": "Loam"}

    species_data = [
        {"species_id": 1, "species_name": "Acacia"},
        {"species_id": 2, "species_name": "Eucalyptus"},
        {"species_id": 3, "species_name": "Ficus"},
    ]

    config = {}

    result = run_exclusion_rules(farm_data, species_data, config)

    assert "candidate_ids" in result
    assert "excluded_species" in result

    assert result["candidate_ids"] == [1, 2, 3]
    assert result["excluded_species"] == []
