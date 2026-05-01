"""
Global MCDA weight estimation from Farm-Species performance data

This module learns global environmental importance weights suitable
for MCDA by fitting pooled machine learning models and extracting
importance via information loss. It supports farm-level block bootstrap
confidence intervals for robust uncertainty estimation.

Intended use:
- Learn global criterion importance for MCDA
- Combine later with species-specific sensitivity modifiers (e.g. AHP)

"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import ElasticNetCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# === Configuration ====================================================================
SEED = 42
ENET_MAX_ITER = 10000
ENET_L1_RATIO = [0.1, 0.5, 0.9]
ENET_ALPHAS = np.logspace(-3, 1, 20)
CV = 5
RF_N_ESTIMATORS = 300
RF_MAX_DEPTH = None
RF_MIN_SAMPLES_LEAF = 20
RF_PERMUTATION_REPEATS = 10


@dataclass
class MCDAConfig:
    """Configuration for MCDA weight estimation."""

    target_col: str = "farm_mean_epi"
    farm_col: str = "farm_id"
    species_col: str = "species_id"
    env_cols: list = None
    random_state: int = SEED


# === Helper functions =================================================================
def ci_width(df):
    """Calculate the width of the 95% confidence interval for each variable."""
    return df.quantile(0.975) - df.quantile(0.025)


def mean_rank(df):
    """Calculate the mean rank of variables across bootstrap replicates."""
    return df.rank(axis=1, ascending=False).mean()


# === Preprocessing ====================================================================
def build_preprocessor(env_cols, species_col):
    """
    Environmental variables pass through unchanged (assumed scaled 0-1).
    Species is encoded only to absorb baseline shifts.

    Args:
    - env_cols: list of column names for environmental variables
    - species_col: column name for species identifier

    Returns:
    - ColumnTransformer that applies the specified transformations
    """
    return ColumnTransformer(
        transformers=[
            ("env", "passthrough", env_cols),
            ("species", OneHotEncoder(drop="first"), [species_col]),
        ]
    )


# === Elastic Net importance ===========================================================
def fit_elastic_net_weights(df, config: MCDAConfig):
    """
    Fit an Elastic Net model and extract normalised absolute coefficients as weights.

    Args:
    - df: DataFrame containing the data
    - config: MCDAConfig with column specifications and model parameters
    Returns:
    - Series of normalised weights for environmental variables
    """
    x = df[config.env_cols + [config.species_col]]
    y = df[config.target_col]

    preprocessor = build_preprocessor(config.env_cols, config.species_col)

    model = ElasticNetCV(
        l1_ratio=ENET_L1_RATIO,
        alphas=ENET_ALPHAS,
        cv=CV,
        max_iter=ENET_MAX_ITER,
        random_state=config.random_state,
    )

    pipeline = Pipeline(steps=[("preprocess", preprocessor), ("model", model)])

    pipeline.fit(x, y)

    coef = pipeline.named_steps["model"].coef_
    env_coef = np.abs(coef[: len(config.env_cols)])

    weights = env_coef / env_coef.sum()
    return pd.Series(weights, index=config.env_cols, name="elastic_net_weight")


# === Random Forest permutation importance =============================================
def fit_rf_weights(df, config: MCDAConfig):
    """
    Fit a Random Forest model and extract normalised permutation importance as weights.

    Args:
    - df: DataFrame containing the data
    - config: MCDAConfig with column specifications and model parameters
    Returns:
    - Series of normalised weights for environmental variables
    """
    x = df[config.env_cols + [config.species_col]]
    y = df[config.target_col]

    preprocessor = build_preprocessor(config.env_cols, config.species_col)

    model = RandomForestRegressor(
        n_estimators=RF_N_ESTIMATORS,
        max_depth=RF_MAX_DEPTH,
        min_samples_leaf=RF_MIN_SAMPLES_LEAF,
        random_state=config.random_state,
        n_jobs=-1,
    )

    pipeline = Pipeline(steps=[("preprocess", preprocessor), ("model", model)])

    pipeline.fit(x, y)

    perm = permutation_importance(
        pipeline,
        x,
        y,
        n_repeats=RF_PERMUTATION_REPEATS,
        scoring="neg_mean_absolute_error",
        random_state=config.random_state,
        n_jobs=-1,
    )

    env_importance = perm.importances_mean[: len(config.env_cols)]
    weights = env_importance / env_importance.sum()

    return pd.Series(weights, index=config.env_cols, name="rf_weight")


# === Combined weights =================================================================
def fit_combined_weights(df, config: MCDAConfig):
    """
    Average the weights from Elastic Net and Random Forest for a more robust estimate.

    Args:
    - df: DataFrame containing the data
    - config: MCDAConfig with column specifications and model parameters
    Returns:
    - Series of normalised combined weights for environmental variables
    """
    w_enet = fit_elastic_net_weights(df, config)
    w_rf = fit_rf_weights(df, config)

    combined = (w_enet + w_rf) / 2
    combined = combined / combined.sum()

    return combined.rename("combined_weight")


# === Bootstrap with early stopping ====================================================
def bootstrap_global_weights_early_stop(
    df,
    config,
    method="combined",
    min_boot=30,
    max_boot=150,
    check_every=10,
    eps_ci=0.02,
    eps_rank=0.1,
    patience=2,
):
    """
    Farm-level block bootstrap with early stopping
    for elastic net, random forest, or combined weights.
    """
    rng = np.random.default_rng(config.random_state)
    farms = df[config.farm_col].unique()

    weights = []
    stable_count = 0
    early_stop = False

    last_ci_width = None
    last_mean_rank = None

    for i in range(max_boot):
        sampled_farms = rng.choice(farms, size=len(farms), replace=True)
        boot_df = pd.concat(df[df[config.farm_col] == f] for f in sampled_farms).reset_index(drop=True)

        # === choose estimator ===
        if method == "elastic_net":
            w = fit_elastic_net_weights(boot_df, config)
        elif method == "rf":
            w = fit_rf_weights(boot_df, config)
        elif method == "combined":
            w = fit_combined_weights(boot_df, config)
        else:
            raise ValueError("method must be 'elastic_net', 'rf', or 'combined'")

        weights.append(w)

        # === early stopping logic ===
        if i + 1 < min_boot or (i + 1) % check_every != 0:
            continue

        w_df = pd.DataFrame(weights)

        curr_ci_width = ci_width(w_df)
        curr_mean_rank = mean_rank(w_df)

        if last_ci_width is not None:
            ci_change = (curr_ci_width - last_ci_width).abs().max()
            rank_change = (curr_mean_rank - last_mean_rank).abs().max()

            if ci_change < eps_ci and rank_change < eps_rank:
                stable_count += 1
            else:
                stable_count = 0

            if stable_count >= patience:
                print(f"Early stop at {i + 1} bootstraps (CI Δ={ci_change:.3f}, rank Δ={rank_change:.3f})")
                early_stop = True
                break

        last_ci_width = curr_ci_width
        last_mean_rank = curr_mean_rank

    return pd.DataFrame(weights), early_stop


# === Confidence interval summary ======================================================
def summarise_bootstrap_weights(boot_df, alpha=0.05):
    """
    Returns mean weight and percentile confidence intervals.

    Args:
    - boot_df: DataFrame of bootstrap weight estimates (one column per variable)
    - alpha: significance level for confidence intervals (default 0.05 for 95% CI)
    """
    lower = alpha / 2
    upper = 1 - alpha / 2

    summary = pd.DataFrame(
        {
            "mean_weight": boot_df.mean(),
            "ci_lower": boot_df.quantile(lower),
            "ci_upper": boot_df.quantile(upper),
        }
    )

    # Clip non-negative
    summary["ci_lower"] = summary["ci_lower"].clip(lower=0)
    summary["ci_upper"] = summary["ci_upper"].clip(lower=0)

    summary["ci_width"] = summary["ci_upper"] - summary["ci_lower"]
    summary["n_bootstraps"] = len(boot_df)

    return summary


# === Export to CSV for Planting Optimisation Tool =====================================
def export_global_weights_csv(
    summary_df,
    path,
    bootstraps,
    bootstrap_early_stopped,
    float_fmt="%.4f",
):
    """
    Export global weight summary to CSV with a META row for importing into the Planting Optimisation Tool.

    Args:
    - summary_df: output of summarise_bootstrap_weights()
                 index = feature names
    - path: output CSV path
    - bootstraps: number of bootstraps used
    - bootstrap_early_stopped: whether early stopping was triggered
    """
    # Ensure feature is a column
    df = summary_df.reset_index().rename(columns={"index": "feature"})

    # Only keep required columns
    df = df[["feature", "mean_weight", "ci_lower", "ci_upper"]]

    # Add empty META columns to feature rows
    df["bootstraps"] = np.nan
    df["bootstrap_early_stopped"] = np.nan

    # Build META row
    meta_row = pd.DataFrame(
        [
            {
                "feature": "__META__",
                "mean_weight": np.nan,
                "ci_lower": np.nan,
                "ci_upper": np.nan,
                "bootstraps": bootstraps,
                "bootstrap_early_stopped": str(bootstrap_early_stopped).lower(),
            }
        ]
    )

    # Concatenate META + data rows
    out_df = pd.concat([meta_row, df], ignore_index=True)

    # Write CSV
    out_df.to_csv(
        path,
        index=False,
        float_format=float_fmt,
        na_rep="",
    )


# === Execution ========================================================================
if __name__ == "__main__":
    # === Load data ===
    script_dir = Path(__file__).parent
    csv_path = script_dir / "epi_farm_species_scores_data.csv"
    df = pd.read_csv(csv_path)

    # === Config ===
    config = MCDAConfig(
        env_cols=[
            "rainfall_mm",
            "temperature_celsius",
            "elevation_m",
            "ph",
            "soil_texture",
        ],
    )

    # === Bootstrap weights with early stopping ===
    boot, boot_early_stop = bootstrap_global_weights_early_stop(
        df,
        config,
        method="combined",
    )

    # === Summarise bootstrap results ===
    summary = summarise_bootstrap_weights(boot)

    # Generate a safe, readable timestamp (e.g., "20260501_133217")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Inject it right before the extension
    path = script_dir / f"global_weights_{timestamp}.csv"

    # === export to CSV for Planting Optimisation Tool ===
    export_global_weights_csv(
        summary_df=summary,
        path=path,
        bootstraps=len(boot),
        bootstrap_early_stopped=boot_early_stop,
    )
