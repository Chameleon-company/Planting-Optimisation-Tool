import pandas as pd
import csv
from suitability_scoring.utils.config import load_yaml
from suitability_scoring.utils.params import build_species_params_dict

# Cache the data so we don't read CSV on every request
_DATA_CACHE = {}


def initialise_data():
    """
    Load all files once into memory.
    """
    if _DATA_CACHE:
        return

    # Path to YAML with defaults and feature meta
    config_path = "config/recommend.yaml"

    ## Load data
    # This will need to come from database in future

    # Load Config
    config = load_yaml(config_path)

    # Path to farms CSV
    farms_path = "data/farms_cleaned.csv"

    # Load farm profile data from CSV file
    farms_df = pd.read_csv(farms_path)

    # Path to species CSV
    species_path = "data/species.csv"

    # Load species profile data from CSV file
    species_df = pd.read_csv(species_path)

    # Path to species_params CSV
    species_params_path = "data/species_params.csv"

    # Load species parameters
    with open(species_params_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        species_params_rows = [row for row in reader]

    # Pre-process params
    params_dict = build_species_params_dict(species_params_rows, config)

    # Store in cache
    _DATA_CACHE["config"] = config
    _DATA_CACHE["farms_df"] = farms_df
    _DATA_CACHE["species_df"] = species_df
    _DATA_CACHE["params_dict"] = params_dict


def get_farms_by_ids(farm_id_list):
    """
    Simulates: SELECT * FROM farms WHERE farm_id IN (:farm_id_list)
    Returns a list of dictionaries.
    """
    # Initialise data by loading if not loaded
    initialise_data()

    df = _DATA_CACHE["farms_df"]
    cfg = _DATA_CACHE["config"]

    # Get the column name for farm_id from config
    farm_id_col = cfg.get("ids", {}).get("farm", "id")

    # Filter, matching any row where the ID is inside the provided list
    subset_df = df[df[farm_id_col].isin(farm_id_list)]

    # Return as list of dictionaries ensuring any NaN's are None
    farms_dicts = subset_df.where(pd.notnull(subset_df), None).to_dict(orient="records")

    return farms_dicts


def get_all_species():
    """
    Simulate: SELECT * FROM species
    """
    # Initialise data by loading if not loaded
    initialise_data()

    # Return as list of dictionaries ensuring any NaN's are None
    df = _DATA_CACHE["species_df"]
    species_dicts = df.where(pd.notnull(df), None).to_dict(orient="records")

    return species_dicts


def get_params_dict():
    """
    Retrieve the pre-built parameters index.
    """
    # Initialise data by loading if not loaded
    initialise_data()

    return _DATA_CACHE["params_dict"]


def get_config():
    """
    Retrieve global config.
    """
    # Initialise data by loading if not loaded
    initialise_data()

    return _DATA_CACHE["config"]
