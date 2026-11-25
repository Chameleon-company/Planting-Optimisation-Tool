import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

FEATURES = [
    "temp_mean",
    "rain_mean",
    "elev_mean",
    "slope_mean",
    "ph",
    "correct_tree_species_name",
    "trunk_circumference",
    "planted_month",
    "age_months",
    "rain_outside_opt",
    "temp_outside_opt",
    "elev_outside_opt",
    "ph_outside_opt",
]

SPECIES_ALIASES = {
    "eucalyptus": "Ai-bubur (mutin)",
    "ai-kamelii": "Ai-kamelli",
    "ai-bubur": "Ai-bubur (mutin)",
    "ai-bubur(mutin)": "Ai-bubur (mutin)",
}

def calculate_tree_age(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate tree age in months from planting and scan dates."""

    result = df.copy()

    result["scan_date"] = pd.to_datetime(result["scan_date"])

    result["age_months"] = (
        (result["scan_date"].dt.year - result["planted_year"]) * 12
        + (result["scan_date"].dt.month - result["planted_month"])
    ).clip(lower=0)

    return result

def outside_range(value, lower, upper):
    """Calculate distance outside an optimal range."""
    return np.maximum(0, lower - value) + np.maximum(0, value - upper)

def calculate_environmental_features(
    df: pd.DataFrame, optima_df: pd.DataFrame
) -> pd.DataFrame:
    """Calculate environmental distances from species' optimal ranges."""

    result = df.copy()

    # Merge species optimal growing conditions
    opt = optima_df.rename(
        columns={"species_name": "correct_tree_species_name"}
    )

    result = result.merge(
        opt, on="correct_tree_species_name", how="left"
    )

    # Calculate environmental distances
    result["rain_outside_opt"] = outside_range(
        result["rain_mean"],
        result["rainfall_min"],
        result["rainfall_max"]
    )

    result["temp_outside_opt"] = outside_range(
        result["temp_mean"],
        result["temp_min"],
        result["temp_max"]
    )

    result["elev_outside_opt"] = outside_range(
        result["elev_mean"],
        result["alt_min"],
        result["alt_max"]
    )

    result["ph_outside_opt"] = outside_range(
        result["ph"],
        result["ph_min"],
        result["ph_max"]
    )

    # Fill missing optimal distances with zero
    opt_dist_cols = [
        "rain_outside_opt",
        "temp_outside_opt",
        "elev_outside_opt",
        "ph_outside_opt"
    ]

    result[opt_dist_cols] = result[opt_dist_cols].fillna(0)

    # Remove raw optimal range columns
    result = result.drop(
        columns=[
            "rainfall_min", "rainfall_max",
            "temp_min", "temp_max",
            "alt_min", "alt_max",
            "ph_min", "ph_max"
        ],
        errors="ignore"
    )

    return result

def remove_invalid_records(df: pd.DataFrame) -> pd.DataFrame:
    """Remove records with missing trunk circumference or tree age."""

    result = df.dropna(
        subset=["trunk_circumference", "age_months"]
    ).reset_index(drop=True)

    return result

def clean_tree_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean numerical tree data required by the survivability model."""

    result = df.copy()

    # Convert trunk circumference to numeric
    result["trunk_circumference"] = pd.to_numeric(
        result["trunk_circumference"], errors="coerce"
    )

    # Convert planting information to numeric
    for column in ["planted_year", "planted_month"]:
        result[column] = pd.to_numeric(
            result[column], errors="coerce"
        )

    # Remove records with missing required values
    result = result.dropna(
        subset=[
            "trunk_circumference",
            "planted_year",
            "planted_month"
        ]
    )

    # Convert planting information to integers
    result["planted_year"] = result["planted_year"].astype(int)
    result["planted_month"] = result["planted_month"].astype(int)

    return result

def clean_species_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise tree species names using known aliases."""

    result = df.copy()

    # Clean species names
    species = result["tree_species"].str.strip()
    species = species.str.replace(" ", "")
    species = species.str.replace("- ", "-")
    species = species.str.replace(" -", "-")
    species = species.str.capitalize()

    species = species.fillna("").astype(str).str.strip()

    # Correct known species aliases
    species_norm = species.str.lower()

    for alias, canonical_name in SPECIES_ALIASES.items():
        species = species.mask(
            species_norm.eq(alias), canonical_name
        )

    result["tree_species"] = species

    # Create the species feature required by the model
    result["correct_tree_species_name"] = (
        species.str.strip().str.lower().str.capitalize()
    )

    return result

def merge_farm_data(
    tree_df: pd.DataFrame, farm_df: pd.DataFrame
) -> pd.DataFrame:
    """Merge tree records with farm environmental data."""

    result = tree_df.merge(
        farm_df[
            [
                "farm_id",
                "ph",
                "rainfall_mm",
                "temperature_celsius",
                "elevation_m",
                "slope"
            ]
        ],
        on="farm_id",
        how="left"
    )

    result = result.rename(
        columns={
            "temperature_celsius": "temp_mean",
            "rainfall_mm": "rain_mean",
            "elevation_m": "elev_mean",
            "slope": "slope_mean"
        }
    )

    return result

def clean_environmental_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove records with missing environmental values."""

    env_features = [
        "temp_mean",
        "rain_mean",
        "elev_mean",
        "slope_mean",
        "ph"
    ]

    result = df.dropna(
        subset=env_features
    ).reset_index(drop=True)

    return result

def preprocess_data(
    df: pd.DataFrame, optima_df: pd.DataFrame
) -> pd.DataFrame:
    """Run the survivability feature preprocessing pipeline."""

    result = calculate_tree_age(df)

    result = calculate_environmental_features(result, optima_df)

    result = remove_invalid_records(result)

    return result

def prepare_model_input(
    tree_df: pd.DataFrame,
    farm_df: pd.DataFrame,
    optima_df: pd.DataFrame
) -> pd.DataFrame:
    """Prepare tree and farm data for survivability prediction."""

    # Clean tree data
    result = clean_tree_data(tree_df)

    # Standardise species names
    result = clean_species_names(result)

    # Merge tree and farm environmental data
    result = merge_farm_data(result, farm_df)

    # Remove missing environmental values
    result = clean_environmental_data(result)

    # Perform feature engineering
    result = preprocess_data(result, optima_df)

    # Select the 13 required model features
    result = select_model_features(result)

    return result

def select_model_features(df: pd.DataFrame) -> pd.DataFrame:
    """Select the 13 features required for model training and prediction."""

    result = df[FEATURES].copy()

    return result

def make_preprocessor() -> ColumnTransformer:
    """Create the preprocessing transformer for the survivability model."""

    return ColumnTransformer(
        transformers=[
            (
                "species",
                OneHotEncoder(handle_unknown="ignore"),
                ["correct_tree_species_name"],
            ),
            (
                "numeric",
                "passthrough",
                [
                    "temp_mean",
                    "rain_mean",
                    "elev_mean",
                    "slope_mean",
                    "ph",
                    "trunk_circumference",
                    "planted_month",
                    "age_months",
                    "rain_outside_opt",
                    "temp_outside_opt",
                    "elev_outside_opt",
                    "ph_outside_opt",
                ],
            ),
        ]
    )