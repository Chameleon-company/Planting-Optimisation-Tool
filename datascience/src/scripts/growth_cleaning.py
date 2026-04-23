import argparse
import re
import sys
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ReportLab Imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer

# ==== Cleaning Settings ===========================================================================
MAD_TO_SIGMA = 0.6745  # scales MAD to sigma-equivalent units for robust z-scores
ROBUST_Z_CUTOFF = 3.0  # absolute robust z-score above this is flagged as suspicious
EPSILON = 1e-9  # tiny stabilizer to avoid divide-by-zero in denominators
GAP_MIN = 0.5  # minimum age gap (years) to treat neighbouring scans as valid
GAP_MAX = 3.0  # maximum age gap (years) to treat neighbouring scans as valid
AGE_BIN_WIDTH_YEARS = 1.0  # width of age bins used for species x age outlier checks
MIN_PER_BIN = 20  # minimum observations per bin before applying outlier flags
ANNUAL_LOW = 0.9  # lower bound (years) for near-annual growth intervals
ANNUAL_HIGH = 1.1  # upper bound (years) for near-annual growth intervals
OVERSHOOT_FACTOR_LAST = 1.0  # multiplier for latest-point growth overshoot tolerance
OVERSHOOT_FACTOR_FIRST = 1.0  # multiplier for first-point growth overshoot tolerance
BASELINE_AT_PLANT_CM = 1.0  # assumed starting circumference at planting (cm)
OVERSHOOT_FACTOR_SINGLE = 1.0  # multiplier for single-scan allowed-circumference threshold

# ==== Plotting Settings ===========================================================================
MIN_PER_BIN = 50  # drop low-sample bins from the plot
SHOW_FLIERS = True  # boxplot outliers
SAVE_DPI = 150
VALUE_COL = "trunk_circumference_clean"
AGE_BIN_WIDTH_YEARS = 1


# ==== Cleaning Functions ==========================================================================
def safe_slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", str(s)).strip("_")[:100]


def validate_and_load(file_path):
    """
    Checks for required columns and loads data.

    Args:
        file_path (str): Path to the input CSV file.

    Returns:
        pd.DataFrame: Loaded and validated DataFrame.

    Raises:
        Exits with error message if validation fails.
    """
    required_columns = [
        "scan_date",
        "planted_year",
        "planted_month",
        "trunk_circumference",
        "tree_species",
        "tree_instance_id",
        "is_dead",
        "farm_id",
    ]

    try:
        # Check header first for speed
        df_header = pd.read_csv(file_path, nrows=0)
        missing = [col for col in required_columns if col not in df_header.columns]

        if missing:
            print(f"ERROR: Missing columns: {', '.join(missing)}")
            sys.exit(1)

        df = pd.read_csv(file_path)
        df["scan_date"] = pd.to_datetime(df["scan_date"])
        return df
    except Exception as e:
        print(f"ERROR: Could not read file: {e}")
        sys.exit(1)


def add_species_id_from_reference(trees_df, species_ref_path="../backend/src/scripts/data/species_20251222.csv"):
    """
    Add species_id to trees_df by matching tree_species against species_ref names.

    Notes:
    - Matching is done by normalising both the 'tree_species' values and the 'name'/'common_name' in the reference to lowercase alphanumeric strings.
    - If 'species_id' is not provided or not numeric in the reference, deterministic IDs will be assigned based on the order of appearance.
    - The function prints summary statistics about the matching process.

    Args:
        trees_df (pd.DataFrame): DataFrame containing tree measurements with a 'tree_species' column.
        species_ref_path (str): Path to the species reference CSV file, which should contain 'name', 'common_name', and optionally 'species_id' columns.

    Returns:
        pd.DataFrame: A copy of trees_df with an added 'species_id' column (Int64 dtype) where matches were found, and NaN where not.

    Raises:
        ValueError: If the species reference file is missing required columns.

    """
    species_ref = pd.read_csv(species_ref_path)

    # Ensure required name columns exist
    required_cols = ["name", "common_name"]
    missing_cols = [c for c in required_cols if c not in species_ref.columns]
    if missing_cols:
        raise ValueError(f"species_ref is missing required columns: {missing_cols}")

    # Standardise text columns for safer matching
    for col in ["name", "common_name"]:
        species_ref[col] = species_ref[col].fillna("").astype(str).str.strip()

    # Prefer species_id from species_ref if available, otherwise assign deterministic IDs
    if "species_id" in species_ref.columns and pd.to_numeric(species_ref["species_id"], errors="coerce").notna().any():
        species_ref["species_id"] = pd.to_numeric(species_ref["species_id"], errors="coerce")
    else:
        species_ref = species_ref.reset_index(drop=True).copy()
        species_ref["species_id"] = species_ref.index + 1

    def normalise_species_name(value):
        return "".join(ch for ch in str(value).lower() if ch.isalnum())

    # Build normalized name -> species_id map from scientific and common names
    species_name_to_id = {}
    for _, row in species_ref.iterrows():
        sid = row["species_id"]
        if pd.isna(sid):
            continue
        sid = int(sid)
        for raw_name in [row["name"], row["common_name"]]:
            norm = normalise_species_name(raw_name)
            if norm and norm not in species_name_to_id:
                species_name_to_id[norm] = sid

    trees_out = trees_df.copy()
    trees_out["species_id"] = trees_out["tree_species"].fillna("").astype(str).map(normalise_species_name).map(species_name_to_id).astype("Int64")

    print(f"Imported {len(species_ref):,} species rows from {species_ref_path}")
    print("Matched rows:", int(trees_out["species_id"].notna().sum()))
    print("Unmatched rows:", int(trees_out["species_id"].isna().sum()))

    return trees_out


def clean_data(df):
    """
    Returns the cleaned DF and a summary dict.

    Notes:
    - The cleaning process includes:
        1. Computing age at scan and filtering out invalid measurements.
        2. Interpolating suspect interior points based on valid neighbours.
        3. Flagging and dropping endpoint measurements with unrealistic growth rates.
        4. Applying a species-aware growth threshold to single-scan tree_instance_ids.
        5. Performing robust z-score outlier detection within species x age bins.
        6. Removing tree_instance_ids with only one scan after cleaning.

    - The function returns both the cleaned DataFrame and a dictionary of metrics summarizing the cleaning process, such as counts of flagged measurements and changes made.

    - The cleaned DataFrame includes a new column 'trunk_circumference_clean' with corrected values, and a 'correction_method' column indicating how each suspect measurement
      was handled ('drop', 'interp_neighbours', or 'as_is').

    - The function assumes that the input DataFrame has already been validated for required columns and that 'scan_date' is in datetime format.

    - The cleaning thresholds and parameters are defined as constants at the top of the script for easy adjustment.

    - After cleaning, the function also removes any tree_instance_id that has only one remaining scan, as these cannot be used for growth analysis.

    Args:
        df (pd.DataFrame): Raw input dataframe with required columns.

    Returns:
        dftc_clean (pd.DataFrame): Cleaned dataframe with suspect measurements removed and outliers flagged.
        metrics (dict): Dictionary of summary metrics about the cleaning process.

    Raises:
        ValueError: If required columns are missing or if no valid ages are found.
    """
    metrics = {}
    initial_count = len(df)
    metrics["total"] = f"Initial measurements: {initial_count}"

    # Make a copy of the cleaned dataframe
    dft = df.dropna(subset=["trunk_circumference"]).copy()

    # Compute age at scan (years, fractional)
    planted_month = dft["planted_month"].fillna(1).astype(int).clip(1, 12)
    dft["planted_date"] = pd.to_datetime(dict(year=dft["planted_year"], month=planted_month, day=15), errors="coerce")
    dft["age_years_at_scan"] = (dft["scan_date"] - dft["planted_date"]).dt.days / 365.25

    # Collapse near-duplicate scans within a short window
    dft["age_round"] = dft["age_years_at_scan"].round(2)  # ≈ 3.65 days
    dft = dft.sort_values(["tree_instance_id", "age_round", "scan_date"]).drop_duplicates(subset=["tree_instance_id", "age_round"], keep="last").drop(columns="age_round")

    # Sort by continuous age and build neighbours
    dftc = dft.sort_values(["tree_instance_id", "age_years_at_scan", "scan_date"]).copy()
    grp = dftc.groupby("tree_instance_id", sort=False, observed=True)

    dftc["prev_age"] = grp["age_years_at_scan"].shift(1)
    dftc["prev_circ"] = grp["trunk_circumference"].shift(1)
    dftc["next_age"] = grp["age_years_at_scan"].shift(-1)
    dftc["next_circ"] = grp["trunk_circumference"].shift(-1)

    dftc["gap_prev"] = dftc["age_years_at_scan"] - dftc["prev_age"]
    dftc["gap_next"] = dftc["next_age"] - dftc["age_years_at_scan"]

    # ==== Interpolation over continuous age ===========================================
    valid_neighbours = dftc["prev_circ"].notna() & dftc["next_circ"].notna() & dftc["gap_prev"].between(GAP_MIN, GAP_MAX) & dftc["gap_next"].between(GAP_MIN, GAP_MAX)

    # Linear interpolation weight by continuous ages
    den = dftc["next_age"] - dftc["prev_age"]
    w = (dftc["age_years_at_scan"] - dftc["prev_age"]) / den
    interp = dftc["prev_circ"] + w * (dftc["next_circ"] - dftc["prev_circ"])
    dftc["interp_from_neighbours"] = np.where(valid_neighbours & den.ne(0), interp, np.nan)

    # Residuals
    dftc["resid_vs_interp"] = dftc["trunk_circumference"] - dftc["interp_from_neighbours"]

    # Local growth rates per year; invalidate rates if gaps < 0.5 (6 months)
    with np.errstate(divide="ignore", invalid="ignore"):
        g_prev = (dftc["trunk_circumference"] - dftc["prev_circ"]) / dftc["gap_prev"]
        g_next = (dftc["next_circ"] - dftc["trunk_circumference"]) / dftc["gap_next"]

    dftc.loc[~dftc["gap_prev"].between(GAP_MIN, GAP_MAX), "prev_circ"] = dftc["prev_circ"]
    dftc.loc[~dftc["gap_next"].between(GAP_MIN, GAP_MAX), "next_circ"] = dftc["next_circ"]

    dftc["g_prev"] = g_prev.replace([np.inf, -np.inf], np.nan)
    dftc["g_next"] = g_next.replace([np.inf, -np.inf], np.nan)

    # Opposite-sign large jumps indicate a spike-revert
    opposite_large = dftc["g_prev"].notna() & dftc["g_next"].notna() & (np.sign(dftc["g_prev"]) != np.sign(dftc["g_next"]))

    # ==== Species-aware growth threshold (p95) ========================================
    pairs_all = dftc.loc[
        dftc["g_prev"].notna() & dftc["gap_prev"].between(GAP_MIN, GAP_MAX),
        ["tree_species", "g_prev", "gap_prev"],
    ].copy()

    pairs_annual = pairs_all.loc[
        pairs_all["gap_prev"].between(ANNUAL_LOW, ANNUAL_HIGH),
        ["tree_species", "g_prev"],
    ]
    have_annual = not pairs_annual.empty

    if have_annual:
        species_thr = pairs_annual.groupby("tree_species", observed=True)["g_prev"].quantile(0.95).rename("species_growth_p95")
    else:
        # Fall back to using all acceptable gaps (rates are already normalised per year)
        species_thr = pairs_all.groupby("tree_species", observed=True)["g_prev"].quantile(0.95).rename("species_growth_p95")

    dftc = dftc.merge(species_thr, on="tree_species", how="left")

    # Global fallback p95 if some species missing thresholds
    global_p95 = pairs_annual["g_prev"].quantile(0.95) if have_annual else pairs_all["g_prev"].quantile(0.95)
    dftc["species_growth_p95"] = dftc["species_growth_p95"].fillna(global_p95)

    # === Robust residual z-score within species ===================================================
    # Force alignment with dftc index (in case of any prior filtering or reordering)
    valid_neighbours = pd.Series(valid_neighbours, index=dftc.index, dtype=bool).fillna(False)

    # Build reference subset for robust residual stats
    resid_ref = dftc.loc[valid_neighbours, ["tree_species", "resid_vs_interp"]].dropna()

    resid_stats = resid_ref.groupby("tree_species", observed=True)["resid_vs_interp"].agg(med="median", mad=lambda s: np.median(np.abs(s - np.median(s)))).reset_index()
    resid_stats["mad"] = resid_stats["mad"].replace(0, np.nan)

    dftc = dftc.merge(resid_stats, on="tree_species", how="left")
    dftc["robust_z_resid"] = MAD_TO_SIGMA * (dftc["resid_vs_interp"] - dftc["med"]) / (dftc["mad"] + EPSILON)

    # === Endpoint rules (continuous ages) =========================================================
    # Latest observation per fob (max age) and earliest (min age)
    dftc["is_latest"] = dftc.groupby("tree_instance_id")["age_years_at_scan"].transform("max").eq(dftc["age_years_at_scan"])
    dftc["is_first"] = dftc.groupby("tree_instance_id")["age_years_at_scan"].transform("min").eq(dftc["age_years_at_scan"])

    # Growth from previous / to next; only consider reasonable gaps
    gap_ok_last = dftc["gap_prev"].between(GAP_MIN, GAP_MAX)
    gap_ok_first = dftc["gap_next"].between(GAP_MIN, GAP_MAX)

    dftc["growth_from_prev"] = (dftc["trunk_circumference"] - dftc["prev_circ"]) / dftc["gap_prev"]
    dftc.loc[(dftc["prev_circ"].isna()) | ~gap_ok_last, "growth_from_prev"] = np.nan

    dftc["growth_to_next"] = (dftc["next_circ"] - dftc["trunk_circumference"]) / dftc["gap_next"]
    dftc.loc[(dftc["next_circ"].isna()) | ~gap_ok_first, "growth_to_next"] = np.nan

    # Species-aware threshold: flag if the latest-year growth rate overshoots the high-end species growth
    endpoint_large_growth = dftc["is_latest"] & gap_ok_last & dftc["growth_from_prev"].notna() & (dftc["growth_from_prev"].abs() > OVERSHOOT_FACTOR_LAST * dftc["species_growth_p95"])

    # Extra endpoint check using an allowed delta over the actual gap
    dftc["allowed_delta_last"] = dftc["species_growth_p95"] * dftc["gap_prev"]
    endpoint_exceeds_cap = dftc["is_latest"] & dftc["prev_circ"].notna() & gap_ok_last & ((dftc["trunk_circumference"] - dftc["prev_circ"]).abs() > dftc["allowed_delta_last"])

    # Species-aware threshold: if first-year growth towards the next year is too extreme, flag
    first_endpoint_large_growth = dftc["is_first"] & gap_ok_first & dftc["growth_to_next"].notna() & (dftc["growth_to_next"].abs() > OVERSHOOT_FACTOR_FIRST * dftc["species_growth_p95"])

    # Cap check using allowed delta over the actual gap (towards next)
    dftc["allowed_delta_first"] = dftc["species_growth_p95"] * dftc["gap_next"]
    first_endpoint_exceeds_cap = dftc["is_first"] & dftc["next_circ"].notna() & gap_ok_first & ((dftc["next_circ"] - dftc["trunk_circumference"]).abs() > dftc["allowed_delta_first"])

    endpoint_suspect = endpoint_large_growth | endpoint_exceeds_cap
    first_endpoint_suspect = first_endpoint_large_growth | first_endpoint_exceeds_cap

    # ==== Single-scan tree_instance_ids: vs species p95 growth * age since planting ===
    # This checks tree_instance_ids that have exactly one row in dftc.
    # It computes age from planted_year/month to scan_date and flags if
    # circ > (species_growth_p95 * age_years).

    # Identify tree_instance_ids with exactly one scan
    scan_counts = dftc.groupby("tree_instance_id", observed=True)["tree_instance_id"].transform("size")
    single_mask = scan_counts.eq(1)
    singles = dftc.loc[single_mask].copy()

    # If nothing to process, initialize flag and skip
    if singles.empty:
        dftc["single_suspect_since_plant"] = False
    else:
        # Valid ages only (>= 0 and not NA)
        singles_valid = singles.loc[singles["age_years_at_scan"].notna() & (singles["age_years_at_scan"] >= 0)].copy()

        singles_valid["allowed_circ"] = BASELINE_AT_PLANT_CM + singles_valid["species_growth_p95"] * singles_valid["age_years_at_scan"]

        singles_valid["single_suspect_since_plant"] = singles_valid["trunk_circumference"] > (OVERSHOOT_FACTOR_SINGLE * singles_valid["allowed_circ"])

        # Write the flag back to dftc (others -> False)
        dftc["single_suspect_since_plant"] = False
        dftc.loc[singles_valid.index, "single_suspect_since_plant"] = singles_valid["single_suspect_since_plant"].astype(bool)

    # ==== Final flags and corrections =================================================
    # Conditions:
    #  - Have valid neighbours
    #  - Large deviation from interpolated expectation (robust z > ROBUST_Z_CUTOFF)
    #  - AND/OR spike-revert with both growth magnitudes unusually large for the species
    large_resid = valid_neighbours & (dftc["robust_z_resid"].abs() > ROBUST_Z_CUTOFF)

    large_spike_revert = valid_neighbours & opposite_large & (dftc["g_prev"].abs() > dftc["species_growth_p95"]) & (dftc["g_next"].abs() > dftc["species_growth_p95"])

    dftc["is_suspect_measure"] = large_resid | large_spike_revert | endpoint_suspect | first_endpoint_suspect | dftc["single_suspect_since_plant"]

    # Correction policy
    #  - Endpoints (latest/first) OR single-scan suspects -> mark as "drop". Leave numeric value unchanged.
    #  - Interior points:
    #       * If flagged and have a valid interp_from_neighbors -> replace value and mark "interp_neighbors".
    #       * Else -> "as_is".
    #  - Non-flagged rows -> "as_is".

    # Build endpoint/single mask
    endpoint_or_single = endpoint_suspect | first_endpoint_suspect
    if "single_suspect_since_plant" in dftc.columns:
        endpoint_or_single = endpoint_or_single | dftc["single_suspect_since_plant"]

    # Interior-suspect mask (exclude endpoint/single to avoid overlap)
    interior_flag = dftc["is_suspect_measure"] & ~endpoint_or_single

    # Start from original values
    dftc["trunk_circumference_clean"] = dftc["trunk_circumference"]

    # Initialise correction_method to blank, then fill cases
    dftc["correction_method"] = ""

    # Endpoints/single-scan suspects -> drop (highest precedence)
    dftc.loc[endpoint_or_single, "correction_method"] = "drop"

    # Interior — interpolate when possible
    interp_mask = interior_flag & dftc["interp_from_neighbours"].notna()
    dftc.loc[interp_mask, "trunk_circumference_clean"] = dftc.loc[interp_mask, "interp_from_neighbours"]
    dftc.loc[interp_mask, "correction_method"] = "interp_neighbours"

    # Interior — flagged but no interpolation available -> drop
    interior_as_is_mask = interior_flag & ~interp_mask
    dftc.loc[interior_as_is_mask, "correction_method"] = "drop"

    # Any rows not covered yet -> as_is
    dftc.loc[dftc["correction_method"].eq(""), "correction_method"] = "as_is"

    # Convenience boolean
    dftc["to_drop"] = dftc["correction_method"].eq("drop")

    # ==== Quick QA ====================================================================
    n_flagged = int(dftc["to_drop"].sum())
    n_rows = len(dftc)
    metrics["clo1"] = f"Flagged measurements to drop: {n_flagged} / {n_rows} ({n_flagged / n_rows:.2%})"

    rel_change = ((dftc["trunk_circumference_clean"] - dftc["trunk_circumference"]) / dftc["trunk_circumference"].replace(0, np.nan)).abs()
    metrics["clo2"] = f"Share of corrected points with >10% relative change: {(rel_change > 0.10).mean():.2%}"

    # ==== Remove cleaned circumference outliers per (species × age_bin) ===============

    # Drop previously marked suspect observations
    dftc = dftc.loc[~dftc["to_drop"]].copy()

    # Keep only rows with circumference and valid ages (should already be true)
    dftc = dftc.loc[dftc["trunk_circumference_clean"].notna() & dftc["age_years_at_scan"].notna() & (dftc["age_years_at_scan"] >= 1)].copy()

    # Fixed-width age bins anchored at 0 (age since planting).
    max_age = float(np.nanmax(dftc["age_years_at_scan"]))
    if not np.isfinite(max_age):
        raise ValueError("No valid ages found in dftc['age_years_at_scan'].")

    # Build bin indices directly
    dftc["age_bin_idx"] = np.floor(dftc["age_years_at_scan"] / AGE_BIN_WIDTH_YEARS).astype("Int64")
    dftc["age_bin_start"] = dftc["age_bin_idx"].astype(float) * AGE_BIN_WIDTH_YEARS
    dftc["age_bin_end"] = dftc["age_bin_start"] + AGE_BIN_WIDTH_YEARS
    dftc["age_bin_label"] = pd.IntervalIndex.from_arrays(left=dftc["age_bin_start"], right=dftc["age_bin_end"], closed="left").astype(str)  # e.g., "[2.0, 3.0)"

    # === Robust z-score on log-circumference per (species × age_bin) ==============================
    dftc["log_circ"] = np.log1p(dftc["trunk_circumference_clean"])

    grp = dftc.groupby(["tree_species", "age_bin_idx"], observed=True)

    # Per-bin statistics
    med = grp["log_circ"].transform("median")
    mad = grp["log_circ"].transform(lambda s: np.median(np.abs(s - np.median(s))))
    mad = mad.replace(0, np.nan)  # avoid division by zero (flat bins)

    # Count per bin (for MIN_PER_BIN guard)
    bin_n = grp["log_circ"].transform("size")

    # Robust z
    dftc["robust_z_species_age_bin"] = MAD_TO_SIGMA * (dftc["log_circ"] - med) / (mad + EPSILON)

    # Outlier flags
    enough_data = bin_n >= MIN_PER_BIN
    dftc["is_outlier_species_age_bin"] = enough_data & (dftc["robust_z_species_age_bin"].abs() > ROBUST_Z_CUTOFF)

    dftc["is_outlier_species_age_bin"] = dftc["is_outlier_species_age_bin"].fillna(False)

    # ==== Quick QA ====================================================================
    n_flagged = int(dftc["is_outlier_species_age_bin"].sum())
    n_rows = len(dftc)
    metrics["clo3"] = f"Flagged outlier measurements: {n_flagged} / {n_rows} ({n_flagged / n_rows:.2%})"

    dftc_clean = dftc.loc[~dftc["is_outlier_species_age_bin"]].copy()

    # Keep only rows where tree_instance_id occurs 2+ times
    mask = dftc_clean["tree_instance_id"].duplicated(keep=False)
    n_before_drop_single = len(dftc_clean)
    dftc_clean = dftc_clean[mask].copy()

    metrics["clo4"] = f"Number of single scan trees being dropped: {n_before_drop_single - len(dftc_clean)}"

    # Remove generated columns
    cols_to_drop = [
        "trunk_circumference",
        "prev_age",
        "prev_circ",
        "next_age",
        "next_circ",
        "gap_prev",
        "gap_next",
        "interp_from_neighbours",
        "resid_vs_interp",
        "g_prev",
        "g_next",
        "species_growth_p95",
        "med",
        "mad",
        "robust_z_resid",
        "is_latest",
        "is_first",
        "growth_from_prev",
        "growth_to_next",
        "allowed_delta_last",
        "allowed_delta_first",
        "single_suspect_since_plant",
        "correction_method",
        "robust_z_species_age_bin",
        "log_circ",
        "is_suspect_measure",
        "to_drop",
        "is_outlier_species_age_bin",
    ]
    dftc_clean.drop(columns=cols_to_drop, inplace=True, errors="ignore")
    dftc_clean = dftc_clean.reset_index(drop=True)

    metrics["retained"] = f"Final cleaned measurements: {len(dftc_clean)}"
    metrics["dropped"] = f"Total dropped measurements: {initial_count - len(dftc_clean)}"

    return dftc_clean, metrics


def calculate_lifetime_growth_rate(df_clean, min_span_years=0.5, max_growth_cm_yr=100.0, drop_negative=True):
    """
    Converts a cleaned longitudinal dataset into a single annualised
    growth rate per tree_instance_id, enforcing biological realism constraints.

    Args:
        df_clean (pd.DataFrame): The cleaned tree measurements dataset.
        min_span_years (float): Minimum elapsed time between first and last scan.
        max_growth_cm_yr (float): The absolute biological ceiling for cm grown per year.
        drop_negative (bool): If True, removes trees with a net negative growth rate.
    """
    # Ensure chronological order per tree to accurately grab first/last scans
    df_sorted = df_clean.sort_values(["tree_instance_id", "age_years_at_scan"])

    # Group by tree to extract the endpoints
    growth_df = (
        df_sorted.groupby("tree_instance_id", observed=True)
        .agg(
            farm_id=("farm_id", "first"),
            species_id=("species_id", "first"),
            tree_species=("tree_species", "first"),
            is_dead=("is_dead", "last"),
            first_age=("age_years_at_scan", "first"),
            last_age=("age_years_at_scan", "last"),
            first_circ=("trunk_circumference_clean", "first"),
            last_circ=("trunk_circumference_clean", "last"),
        )
        .reset_index()
    )

    # Calculate the elapsed time between first and last scan
    growth_df["age_span"] = growth_df["last_age"] - growth_df["first_age"]

    # Enforce minimum time span
    growth_df = growth_df[growth_df["age_span"] >= min_span_years].copy()

    # Calculate the annualised growth rate
    growth_df["net_growth_rate_cm_yr"] = (growth_df["last_circ"] - growth_df["first_circ"]) / growth_df["age_span"]

    # Clean up math artifacts
    growth_df["net_growth_rate_cm_yr"] = growth_df["net_growth_rate_cm_yr"].replace([np.inf, -np.inf], np.nan)
    growth_df = growth_df.dropna(subset=["net_growth_rate_cm_yr"])

    # Handle negative growth
    if drop_negative:
        # We assume net negative growth over a >6 month span is a hardware reset
        # or measurement failure that slipped through, rather than biological shrinkage.
        growth_df = growth_df[growth_df["net_growth_rate_cm_yr"] > 0.0]

    # Enforce biological ceiling
    # Drops extreme outliers resulting from misentered data (e.g., 10cm recorded as 100cm)
    growth_df = growth_df[growth_df["net_growth_rate_cm_yr"] <= max_growth_cm_yr]

    return growth_df.reset_index(drop=True)


# ==== Plotting Functions ==========================================================================
def plot_species_for_report(df_base, species_name):
    """
    Generates a boxplot of trunk circumference by age bin for a given species, and returns it as a ReportLab Image object.

    Args:
        df_base (pd.DataFrame): The cleaned DataFrame containing the data to plot.
        species_name (str): The name of the species to filter and plot.

    Returns:
        ReportLab Image object containing the boxplot, or None if there is insufficient data to plot.

    Raises:
        ValueError: If the required columns for plotting are missing from df_base.
    """
    # Filter data for this specific species
    # Ensure 'age_bin_idx' exists - if not, you may need to add your binning logic here
    df_sp = df_base.loc[(df_base["tree_species"] == species_name) & df_base[VALUE_COL].notna() & df_base["age_bin_idx"].notna()].copy()

    if df_sp.empty:
        return None

    # Filter bins with enough samples
    bin_counts = df_sp.groupby("age_bin_idx", observed=True)[VALUE_COL].size()
    valid_bins = bin_counts[bin_counts >= MIN_PER_BIN].index
    df_sp = df_sp[df_sp["age_bin_idx"].isin(valid_bins)].copy()

    if df_sp.empty:
        return None

    # Handle ordering and labels
    bin_order = df_sp.loc[:, ["age_bin_idx", "age_bin_start"]].drop_duplicates().sort_values("age_bin_start")["age_bin_idx"].tolist()

    tick_labels = df_sp.loc[:, ["age_bin_idx", "age_bin_label", "age_bin_start"]].drop_duplicates().set_index("age_bin_idx").loc[bin_order, "age_bin_label"].tolist()

    # Generate the Matplotlib Figure
    plt.figure(figsize=(12, 5))
    ax = sns.boxplot(
        data=df_sp,
        x="age_bin_idx",
        y=VALUE_COL,
        order=bin_order,
        showfliers=SHOW_FLIERS,
        color="#8fb4d9",
    )

    ax.set_xticks(range(len(tick_labels)))
    ax.set_xticklabels(tick_labels, rotation=45, ha="right")
    ax.set_xlabel(f"Age bin (width = {AGE_BIN_WIDTH_YEARS} years)")
    ax.set_ylabel("Trunk circumference (cm)")
    ax.set_title(f"{species_name}: Trunk circumference by age bin")
    plt.tight_layout()

    # Convert to ReportLab Image
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format="png", dpi=SAVE_DPI, bbox_inches="tight")
    plt.close()  # CRITICAL: Frees memory and stops the plot from showing in terminal
    img_buffer.seek(0)

    return Image(img_buffer, width=6 * inch, height=2.5 * inch)


def plot_growth_rate_distribution(df_growth_rates):
    """
    Generates a boxplot of the net annualised growth rates across all species.
    Returns a ReportLab Image object.

    Args:
        df_growth_rates (pd.DataFrame): DataFrame containing at least 'tree_species' and 'net_growth_rate_cm_yr' columns.

    Returns:
        ReportLab Image object containing the boxplot, or None if there is insufficient data to plot
    """
    # Filter out species with too few trees to make a meaningful boxplot
    species_counts = df_growth_rates["tree_species"].value_counts()
    valid_species = species_counts[species_counts >= 10].index
    df_plot = df_growth_rates[df_growth_rates["tree_species"].isin(valid_species)].copy()

    if df_plot.empty:
        print("[skip] Not enough data to plot growth rate distributions.")
        return None

    # Sort species by median growth rate for a cleaner visual
    order = df_plot.groupby("tree_species")["net_growth_rate_cm_yr"].median().sort_values(ascending=False).index

    plt.figure(figsize=(10, 6))

    # Create the boxplot
    ax = sns.boxplot(data=df_plot, x="net_growth_rate_cm_yr", y="tree_species", order=order, color="#8fb4d9", showfliers=SHOW_FLIERS)

    ax.set_xlabel("Net Annualised Growth Rate (cm/year)")
    ax.set_ylabel("Tree Species")
    ax.set_title("Distribution of Annualised Growth Rates by Species")
    plt.tight_layout()

    # Convert to ReportLab Image
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format="png", dpi=SAVE_DPI, bbox_inches="tight")
    plt.close()
    img_buffer.seek(0)

    return Image(img_buffer, width=6.5 * inch, height=4 * inch)


# ==== Output Functions ============================================================================
def save_cleaned_circumference_data(df, output_csv_path):
    """
    Removes generated/internal columns and saves the dataframe to a CSV.

    Args:
        df (pd.DataFrame): The cleaned DataFrame to save.
        output_csv_path (str): The file path for the output CSV.

    Raises:
        Exception: If there is an error during saving.
    """
    cols_to_drop = [
        "planted_month",
        "planted_year",
        "age_bin_idx",
        "age_bin_start",
        "age_bin_end",
        "age_bin_label",
        "farmer_card_id",
        "scan_date",
        "planted_date",
    ]

    # Create a copy to avoid SettingWithCopy warnings if df is a slice
    df_out = df.drop(columns=cols_to_drop, errors="ignore").copy()

    # Reorder result_df columns using exact column names only
    column_order = [
        "farm_id",
        "tree_instance_id",
        "species_id",
        "tree_species",
        "is_dead",
        "age_years_at_scan",
        "trunk_circumference_clean",
    ]

    remaining_cols = [c for c in df_out.columns if c not in column_order]
    df_out = df_out[column_order + remaining_cols]

    try:
        df_out.to_csv(output_csv_path, index=False)
        print(f"[saved] Cleaned data exported to: {output_csv_path}")
    except Exception as e:
        print(f"ERROR: Could not save CSV: {e}")


def save_cleaned_rate_data(df, output_csv_path):
    """
    Removes generated/internal columns and saves the dataframe to a CSV.

    Args:
        df (pd.DataFrame): The cleaned DataFrame to save.
        output_csv_path (str): The file path for the output CSV.

    Raises:
        Exception: If there is an error during saving.
    """
    cols_to_drop = [
        "is_dead",
        "last_age",
        "first_circ",
        "last_circ",
    ]

    # Create a copy to avoid SettingWithCopy warnings if df is a slice
    df_out = df.drop(columns=cols_to_drop, errors="ignore").copy()

    # Reorder result_df columns using exact column names only
    column_order = ["tree_instance_id", "farm_id", "species_id", "tree_species", "first_age", "age_span", "net_growth_rate_cm_yr"]

    remaining_cols = [c for c in df_out.columns if c not in column_order]
    df_out = df_out[column_order + remaining_cols]

    try:
        df_out.to_csv(output_csv_path, index=False)
        print(f"[saved] Cleaned data exported to: {output_csv_path}")
    except Exception as e:
        print(f"ERROR: Could not save CSV: {e}")


def generate_pdf(df, df_growth_rates, metrics, output_path, logo_path="../frontend/public/assets/images/logo2.png"):
    """
    Generates a PDF report with a summary of cleaning metrics and boxplots for each species.

    Args:
        df (pd.DataFrame): The cleaned DataFrame containing the data to plot.
        metrics (dict): A dictionary of summary metrics about the cleaning process to include in the report.
        output_path (str): The file path for the output PDF report.

    Raises:
        Exception: If there is an error during PDF generation.
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    def add_header_logo(canvas, doc):
        canvas.saveState()

        # Set desired dimensions
        logo_width = 1.25 * inch
        logo_height = 1.25 * inch

        # Position: Top Right
        # doc.pagesize[0] is width, [1] is height
        padding = 0.5 * inch
        x_pos = doc.pagesize[0] - logo_width - padding
        y_pos = doc.pagesize[1] - logo_height - padding

        try:
            # mask='auto' handles transparency in PNGs beautifully
            canvas.drawImage(
                logo_path,
                x_pos,
                y_pos,
                width=logo_width,
                height=logo_height,
                mask="auto",
                preserveAspectRatio=True,
            )
        except Exception as e:
            print(f"Could not load PNG logo: {e}")

        canvas.restoreState()

    # Title
    story.append(Paragraph("Growth Data Cleaning Report", styles["Title"]))

    # Processing description
    story.append(Paragraph("Data Processing Methodology", styles["Heading2"]))
    processing_text = (
        "This report summarises the results of a multi-stage cleaning pipeline designed to "
        "identify and correct anomalies in longitudinal tree growth data. The process includes "
        "local growth rate validation, robust z-score outlier detection within species-age cohorts, "
        "and linear interpolation for identified spike-revert anomalies."
    )
    story.append(Paragraph(processing_text, styles["Normal"]))

    # Summary section
    story.append(Paragraph("Processing Metrics", styles["Heading2"]))

    # Loop through all keys in the metrics dictionary
    # We use <br/> because ReportLab Paragraphs don't recognize \n
    summary_lines = []
    for key, value in metrics.items():
        summary_lines.append(f"{value}")

    # Join lines with HTML line breaks
    summary_text = "<br/>".join(summary_lines)

    # Add to the story
    story.append(Paragraph(summary_text, styles["Normal"]))

    # Output Table Description
    story.append(Paragraph("Cleaned Data Output", styles["Heading2"]))
    table_text = (
        "The resulting cleaned dataset provides a refined basis for growth modelling. Key outputs "
        "include <i>trunk_circumference_clean</i>, which represents the validated measurement, "
        "and <i>age_years_at_scan</i>, which normalises measurements to the time elapsed since planting and"
        "<i>net_growth_rate_cm_yr</i>, which represents the calculated annualised growth rate for a tree."
    )
    story.append(Paragraph(table_text, styles["Normal"]))

    # Figure interpretation
    story.append(Paragraph("Interpreting Species Figures", styles["Heading2"]))
    figure_text = (
        "The box plots on the following pages illustrate the distribution of trunk circumferences "
        "across different age bins (1-year intervals). The 'boxes' represent the interquartile range (IQR), "
        "the internal line represents the median, and the whiskers extend to 1.5x the IQR. "
        "Individual points (fliers) represent trees that are statistically significant but passed "
        "the cleaning thresholds."
    )
    story.append(Paragraph(figure_text, styles["Normal"]))

    story.append(PageBreak())
    # Species Loop
    species_list = df["tree_species"].dropna().unique().tolist()
    # Initialise a counter for successful plots
    plots_added = 0

    for spec in species_list:
        plot_img = plot_species_for_report(df, spec)

        if plot_img:
            story.append(Paragraph(f"Species: {spec}", styles["Heading3"]))
            story.append(plot_img)
            story.append(Spacer(1, 0.1 * inch))
            # Increment the counter
            plots_added += 1

            # If we just added the 3rd plot (or 6th, 9th, etc.), add a page break
            if plots_added % 3 == 0:
                story.append(PageBreak())
        else:
            print(f"[skip] {spec}: Insufficient data for plotting.")

    # Add to the story
    story.append(Paragraph("Overall Growth Rate Distributions", styles["Heading2"]))
    story.append(Paragraph("The chart below illustrates the annualised net growth rate (cm/year) calculated from the first and last valid scans of each tree, grouped by species.", styles["Normal"]))
    story.append(Spacer(1, 0.1 * inch))

    # Generate and append the new plot
    distribution_plot = plot_growth_rate_distribution(df_growth_rates)
    if distribution_plot:
        story.append(distribution_plot)

    story.append(PageBreak())

    doc.build(story, onFirstPage=add_header_logo)


# ==== CLI Entry Point =============================================================================
def main():
    parser = argparse.ArgumentParser(description="TreeO2 Growth Cleaning and Reporting Tool")
    # Input
    parser.add_argument("input", help="Path to input treeo2_cleaned.csv.gz")

    # Outputs
    parser.add_argument(
        "--report",
        "-r",
        default="docs/Growth_Cleaning_Report.pdf",
        help="Output PDF report path (default: Growth_Cleaning_Report.pdf)",
    )

    parser.add_argument(
        "--csv",
        "-c",
        default="notebooks/farm_species_age_circumference.csv",
        help="Output cleaned CSV path (default: farm_species_age_circumference.csv)",
    )

    args = parser.parse_args()

    print(f"Reading {args.input}...")
    trees = validate_and_load(args.input)

    print("Adding species IDs from reference")
    df = add_species_id_from_reference(trees, "../backend/src/scripts/data/species_20251222.csv")

    print("Cleaning data...")
    df_cleaned, metrics = clean_data(df)

    # Calculate the annualised growth rate for each tree
    print("Calculating annualised growth rates...")
    df_growth_rates = calculate_lifetime_growth_rate(df_cleaned)

    print(f"Generating PDF: {args.report}...")
    generate_pdf(df_cleaned, df_growth_rates, metrics, args.report)
    print("Success.")

    # Save the CSV (The requested save function)
    print(f"Saving cleaned circumference CSV: {args.csv}...")
    save_cleaned_circumference_data(df_cleaned, args.csv)

    print(f"Saving cleaned rates CSV: {args.csv}...")
    save_cleaned_rate_data(df_growth_rates, args.csv.replace(".csv", "_growth_rates.csv"))

    print("Process complete.")


if __name__ == "__main__":
    main()
