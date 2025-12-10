import pytest
import yaml
from suitability_scoring.utils.config import load_yaml


def test_load_yaml_valid_file(tmp_path):
    """
    Test that a valid YAML file is loaded correctly.
    Uses the pytest tmp_path fixture
    """
    # Create a dummy YAML file in the temporary directory
    config_file = tmp_path / "test_config.yaml"

    data = {
        "features": {
            "rainfall_mm": {
                "type": "numeric",
                "short": "rainfall",
                "score_method": "num_range",
                "default_weight": 0.20,
            }
        }
    }

    # Write data to the file
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f)

    # Call the function
    result = load_yaml(str(config_file))

    # 3. Assertions
    assert result == data
    assert result["features"]["rainfall_mm"]["type"] == "numeric"
    assert result["features"]["rainfall_mm"]["default_weight"] == pytest.approx(0.2)


def test_load_yaml_file_not_found():
    """
    Test that FileNotFoundError is raised for non-existent files.
    """
    with pytest.raises(FileNotFoundError):
        load_yaml("path/to/non_existent_file.yaml")


def test_load_yaml_invalid_syntax(tmp_path):
    """
    Test that YAMLError is raised when the file contains bad syntax.
    """
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text("key: [unclosed_list", encoding="utf-8")

    with pytest.raises(yaml.YAMLError):
        load_yaml(str(bad_file))
