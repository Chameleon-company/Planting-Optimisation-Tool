import yaml


def load_yaml(path: str):
    """
    Load YAML configuration file and return as dictionary

    :param path: Path to file as a string
    :returns: Dictionary of configuration parameters
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
