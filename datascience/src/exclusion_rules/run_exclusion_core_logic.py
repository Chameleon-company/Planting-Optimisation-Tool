"""
Task 7 - Exclusion rules entrypoint for project integration (API-aligned: id).

Adapter accepts pandas objects (DataFrame / Series) and converts them into
records to run the config-driven core logic.

Updates included:
- Task 10: Config now may include "rules" and "annotation"
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd

from .exclusion_core_logic import run_exclusion_rules_records


DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parents[2] / "exclusion_rules" / "exclusion_config.json"
)


def load_exclusion_config(path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Load exclusion config from JSON.

    If missing, return safe defaults:
    - dependency disabled
    - other options use defaults inside core logic
    """
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH

    if not config_path.exists():
        return {"dependency": {"enabled": False}}

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_exclusion_rules(
    farm_data: Union[Dict[str, Any], pd.Series],
    species_df: pd.DataFrame,
    config: Optional[Dict[str, Any]] = None,
    dependencies_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Apply exclusion rules for ONE farm (API aligned: uses id).

    Returns
    -------
    {"candidate_ids": [...], "excluded_species": [...]}
    """
    farm_dict = (
        farm_data.to_dict() if isinstance(farm_data, pd.Series) else dict(farm_data)
    )
    cfg = config if config is not None else load_exclusion_config()

    species_rows = species_df.fillna(value=pd.NA).to_dict(orient="records")

    dep_rows = None
    if dependencies_df is not None:
        dep_rows = dependencies_df.fillna(value=pd.NA).to_dict(orient="records")

    return run_exclusion_rules_records(
        farm_data=farm_dict,
        species_rows=species_rows,
        config=cfg,
        dependencies_rows=dep_rows,
    )
