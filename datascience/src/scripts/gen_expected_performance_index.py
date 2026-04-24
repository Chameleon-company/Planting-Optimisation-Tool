import argparse
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pygam import GammaGAM, s
from reportlab.lib import colors

# ReportLab Imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ==== Plotting Settings ===========================================================================
SAVE_DPI = 150


# ==== GAM Functions ===============================================================================
def fit_species_gams(age, rate, n_splines=10):
    """
    Fits a GammaGAM.

    Args:
        age (np.array): Age data for the species.
        rate (np.array): Growth rate data for the species.
        n_splines (int): Number of splines to use in the GAM.

    Returns:
        name (str): Name of the model type.
        model (GammaGAM): The fitted GAM model.
        stats (dict): A dictionary of model statistics (AIC, deviance, edof).
    """
    x = age.reshape(-1, 1)
    gam = GammaGAM(s(0, n_splines=n_splines))
    model = gam.gridsearch(x, rate, progress=False)
    stats = getattr(model, "statistics_", {})
    return "Gamma", model, stats


def gam_predict(model, age_grid):
    """
    Predicts values and confidence intervals.

    Args:
        model (GammaGAM): The fitted GAM model.
        age_grid (np.array): A grid of age values to predict on.

    Returns:
        yhat (np.array): Predicted growth rate values.
        lo (np.array or None): Lower bounds of confidence intervals, or None if not available.
        hi (np.array or None): Upper bounds of confidence intervals, or None if not available
    """
    xg = age_grid.reshape(-1, 1)
    yhat = model.predict(xg)
    lo, hi = None, None
    try:
        lo, hi = model.confidence_intervals(xg, width=0.95).T
    except Exception:
        pass
    return yhat, lo, hi


# ==== Output Functions ============================================================================
def plot_growth_for_report(sp, grp, age_grid, yhat_grid, lo, hi):
    """
    Generates the GAM plot and returns it as an in-memory BytesIO buffer.

    Args:
        sp (str): Species name for the plot title.
        grp (pd.DataFrame): The data group for the species.
        age_grid (np.array): The age values used for predictions.
        yhat_grid (np.array): The predicted growth rate values.
        lo (np.array or None): Lower bounds of confidence intervals.
        hi (np.array or None): Upper bounds of confidence intervals.

    Returns:
        BytesIO: An in-memory buffer containing the plot image.
    """
    fig, ax = plt.subplots(figsize=(12, 5), dpi=120)
    ax.scatter(grp["mid_age"], grp["rate"], s=10, alpha=0.3, color="#5a5a5a", label="Observed")
    ax.plot(age_grid, yhat_grid, color="#2a9d8f", lw=2, label="GAM Fit")

    if lo is not None and hi is not None:
        ax.fill_between(age_grid, lo, hi, color="#2a9d8f", alpha=0.15, linewidth=0)

    ax.set_xlabel("Biological Age (Mid-point of growth window)")
    ax.set_ylabel("Annualised Growth Rate (cm/yr)")
    ax.legend(frameon=False)

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=SAVE_DPI, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    return Image(buf, width=6 * inch, height=2.5 * inch)


def plot_epi_for_report(sp, grp):
    """
    Generates the EPI histogram and returns it as an in-memory BytesIO buffer.

    Args:
        sp (str): Species name for the plot title.
        grp (pd.DataFrame): The data group for the species.

    Returns:
        BytesIO: An in-memory buffer containing the plot image.
    """
    fig, ax = plt.subplots(figsize=(12, 5), dpi=120)

    d = grp["epi"].dropna()
    if d.empty:
        return

    ax.hist(d, bins=10, edgecolor="black")
    ax.set_title(f"Histogram of {'Expected Performance Index'} — {sp}")
    ax.set_xlabel("Expected Performance Index")
    ax.set_ylabel("Frequency")

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=SAVE_DPI, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    return Image(buf, width=6 * inch, height=2.5 * inch)


def plot_farm_performance_violin(farm_targets):
    """
    Generates a violin plot of farm performance by species
    and returns it as an in-memory ReportLab Image.

    Args:
        farm_targets (pd.DataFrame): The aggregated dataset containing 'farm_mean_epi' and 'species'.

    Returns:
        reportlab.platypus.Image: A flowable image ready to be appended to a Story.
    """
    # Set up the figure (Slightly taller than the histogram to fit multiple species)
    fig, ax = plt.subplots(figsize=(6.5, 3.5), dpi=120)

    # Prevent errors on empty data
    if farm_targets.empty:
        plt.close(fig)
        return None

    # Draw the violin plot onto our specific axes (ax)
    sns.violinplot(data=farm_targets, x="farm_mean_epi", y="species", orient="h", hue="species_id", legend=False, palette="crest", inner="quartile", linewidth=1, cut=0, ax=ax)

    # Add the baseline reference
    ax.axvline(x=1.0, color="#e76f51", linestyle="--", linewidth=1.5, label="Baseline (EPI=1.0)")

    # Clean labels and styling to match the histogram
    ax.set_title("Distribution of Farm Performance by Species ID", fontsize=11, pad=10)
    ax.set_xlabel("Farm Mean EPI (Actual / Expected Growth)", fontsize=9)
    ax.set_ylabel("")
    ax.legend(frameon=False, fontsize=8)

    # Clean up the layout
    plt.tight_layout()

    # Save to the in-memory buffer
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    return Image(buf, width=6.5 * inch, height=3.5 * inch)


def generate_pdf_report(df, summary_df, preds_df, epi_df, farm_targets, output_path, logo_path="../frontend/public/assets/images/logo2.png"):
    """
    Builds the ReportLab PDF.

    Args:
        df (pd.DataFrame): The full dataset for all species.
        summary_df (pd.DataFrame): Summary statistics for each species.
        preds_df (pd.DataFrame): Predicted values for each species.
        epi_df (pd.DataFrame): Expected Performance Index values for each species.
        farm_targets (pd.DataFrame): Aggregated dataset containing farm performance data.
        output_path (str): The file path to save the generated PDF.

    Returns:
        None
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
    story.append(Paragraph("Expected Performance Index Report", styles["Title"]))
    story.append(Spacer(1, 0.25 * inch))

    # Methodology
    story.append(Paragraph("Methodology and Purpose", styles["Heading2"]))

    methodology_text = """
    To decouple tree age from environmental suitability, we employ a Gamma Generalised Additive Model (GAM). 
    Unlike standard regression, a Gamma GAM respects the biological reality that tree size must be positive 
    and that variance increases as trees mature (heteroscedasticity). <br/><br/>
    
    By using a Log-Link function, we capture the natural growth curve. The resulting 
    Expected Performance Index (EPI) is the ratio of actual growth to the model's 
    predicted baseline. This creates a standardised metric: an EPI of 1.2 indicates 
    growth 20% above the species average for that age, isolating the environmental 
    signal for use in our MCDA weight extraction.
    """
    story.append(Paragraph(methodology_text, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    # Summary Table
    story.append(Paragraph("Model Fitting Summary", styles["Heading2"]))

    # Prepare Table Data
    table_data = [["Species", "Points", "AIC", "Deviance", "EDOF"]]
    for _, row in summary_df.iterrows():
        table_data.append(
            [
                row["species"],
                row["n_points"],
                f"{row['GAM_AIC']:.2f}",
                f"{row['GAM_deviance']:.2f}",
                f"{row['GAM_edof']:.2f}",
            ]
        )

    t = Table(table_data, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(t)
    story.append(PageBreak())

    # Species Details and Plots
    story.append(Paragraph("Species Specific Fits", styles["Heading2"]))

    df_groups = df.groupby("species")
    preds_groups = preds_df.groupby("species")

    # Initialise a counter for successful plots
    plots_added = 0

    for sp, grp in df_groups:
        # Get the corresponding predictions for this species
        preds_grp = preds_groups.get_group(sp)

        # Extract the prediction grids
        age_grid = preds_grp["age_years"].to_numpy()
        yhat_grid = preds_grp["GAM_rate_cm_yr"].to_numpy()
        lo = preds_grp["GAM_PI_lo"].to_numpy()
        hi = preds_grp["GAM_PI_hi"].to_numpy()

        # Add Plot
        plot_img = plot_growth_for_report(sp, grp, age_grid, yhat_grid, lo, hi)
        if plot_img:
            story.append(Paragraph(f"Species: {sp}", styles["Heading3"]))
            story.append(plot_img)
            story.append(Spacer(1, 0.1 * inch))

            # Increment the counter
            plots_added += 1

            # If we just added the 3rd plot (or 6th, 9th, etc.), add a page break
            if plots_added % 3 == 0:
                story.append(PageBreak())

    # Species EPI plots
    story.append(Paragraph("Species Specific Expected Performance Index Histograms", styles["Heading2"]))

    epi_groups = epi_df.groupby("species")

    # Initialise a counter for successful plots
    plots_added = 0

    for sp, grp in epi_groups:
        # Add Plot
        plot_img = plot_epi_for_report(sp, grp)
        if plot_img:
            story.append(Paragraph(f"Species: {sp}", styles["Heading3"]))
            story.append(plot_img)
            story.append(Spacer(1, 0.1 * inch))

            # Increment the counter
            plots_added += 1

            # If we just added the 3rd plot (or 6th, 9th, etc.), add a page break
            if plots_added % 3 == 0:
                story.append(PageBreak())

    # Farm-Level Aggregation & Violin Plot Section
    story.append(Paragraph("Farm-Level Performance Aggregation", styles["Heading2"]))

    # Explanation of why we aggregate
    aggregation_text = """
    <b>Aggregate to the Farm Level</b><br/><br/>
    Before feeding the Expected Performance Index (EPI) into the final weight-extraction GAM, 
    the tree-level data is grouped by farm identifier (e.g., farm_id) and species_id. This achieves two vital things:<br/><br/>
    1. Noise Reduction: Individual trees exhibit random variance (e.g., one tree got struck by lightning, 
    another had an isolated fungal infection). Averaging the EPI of all trees of a specific species on a 
    single farm smooths out that individual noise, resulting in a highly stable "Farm Performance Score."<br/><br/>
    2. Alignment with Features: The environmental features (Rainfall, Temperature, Soil suitability) 
    are scored at the farm level, not the individual tree level. The target variable (EPI) must perfectly 
    align with these inputs for accurate mathematical extraction.
    """
    story.append(Paragraph(aggregation_text, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    # Explanation of the Violin Plot
    violin_desc_text = """
    <b>Interpreting the Violin Plot</b><br/><br/>
    The plot below illustrates the distribution of these aggregated Farm EPI scores across different species. 
    It highlights the density of farm performance: wider sections indicate a high concentration of farms 
    achieving that specific score. The dashed vertical line at 1.0 represents the biological baseline 
    (where actual growth perfectly matches expected growth).
    """
    story.append(Paragraph(violin_desc_text, styles["Normal"]))
    story.append(Spacer(1, 0.25 * inch))

    # Add the Violin Plot
    if farm_targets is not None and not farm_targets.empty:
        violin_img = plot_farm_performance_violin(farm_targets)
        if violin_img:
            story.append(violin_img)
            story.append(Spacer(1, 0.2 * inch))
    else:
        story.append(Paragraph("<i>No farm target data available to generate distribution plot.</i>", styles["Normal"]))

    # Build the document
    doc.build(story, onFirstPage=add_header_logo)


# ==== CLI Entry Point =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Generate Expected Performance Index Report")
    parser.add_argument("input", help="Path to input CSV (e.g., farm_species_age_circumference.csv)")
    parser.add_argument("--output", "-o", default="docs/EPI_Report.pdf", help="Output PDF name")
    args = parser.parse_args()

    # Read cleaned growth rates data
    print(f"Loading data from {args.input}...")
    df = pd.read_csv(args.input)

    # Calculate a mid-point age to represent the tree's biological age during this specific growth window
    df["mid_age"] = df["first_age"] + (df["age_span"] / 2.0)

    # Rename the target variable for convenience in the script
    df.rename(columns={"net_growth_rate_cm_yr": "rate", "tree_species": "species"}, inplace=True)

    summary_rows = []
    preds_all = []
    epi_rows = []  # per-observation performance index rows

    print("Fitting models per species...")

    for sp, grp in df.groupby("species"):
        if len(grp) < 50:  # min_points_per_species
            continue

        age = grp["mid_age"].to_numpy().astype(float)
        rate = grp["rate"].to_numpy().astype(float)

        # Fit GAM
        name, model, stats = fit_species_gams(age, rate)

        row = {"species": sp, "n_points": len(grp)}
        for k in ["AIC", "deviance", "edof"]:
            row[f"GAM_{k}"] = stats.get(k, np.nan)
        summary_rows.append(row)

        # Predictions on a grid
        age_grid = np.linspace(1, min(20, float(np.nanmax(age)) * 1.05), 601)
        yhat_grid, lo, hi = gam_predict(model, age_grid)

        preds = pd.DataFrame(
            {
                "species": sp,
                "age_years": age_grid,
                "GAM_rate_cm_yr": yhat_grid,
                "GAM_PI_lo": lo if lo is not None else np.nan,
                "GAM_PI_hi": hi if hi is not None else np.nan,
            }
        )
        preds_all.append(preds)

        # EPI for each observed tree
        x = age.reshape(-1, 1)
        rate_hat = model.predict(x)

        # Ratio-based Expected Performance Index
        epi = rate / np.maximum(rate_hat, 1e-9)

        epi_df = pd.DataFrame(
            {
                "species": sp,
                "species_id": grp["species_id"].iloc[0],
                "farm_id": grp["farm_id"].to_numpy(),
                "epi": epi,
            }
        )
        epi_rows.append(epi_df)

    summary_df = pd.DataFrame(summary_rows)

    preds_df = pd.concat(preds_all, ignore_index=True)

    epi_df = pd.concat(epi_rows, ignore_index=True)

    # Sort by species_id and farm_id for better readability in the report
    epi_df = epi_df.sort_values(by=["species_id", "farm_id"], ascending=[True, True])

    # Aggregate to the Farm Level too:
    # 1. Reduce noise: Individual trees have random variance (e.g., one tree got struck by lightning, another had an isolated fungal infection).
    # Averaging the EPI of all 50 Mahogany trees on Farm A smooths out that individual noise and gives a highly stable "Farm Performance Score."
    # 2. Align with features: The environmental features (Rainfall, Temperature, Soil) are scored at the farm level, not the tree level.
    # The target must perfectly align with the inputs.
    farm_targets = epi_df.groupby(["farm_id", "species_id", "species"])["epi"].mean().reset_index().copy()

    # Rename for clarity
    farm_targets.rename(columns={"epi": "farm_mean_epi"}, inplace=True)

    try:
        farm_targets.drop(columns=["species"]).to_csv("notebooks/aggregated_epi_data.csv", index=False)
        print("[saved] Aggregated EPI data exported to: notebooks/aggregated_epi_data.csv")
    except Exception as e:
        print(f"ERROR: Could not save CSV: {e}")

    print(f"Generating PDF report: {args.output}...")
    generate_pdf_report(df, summary_df, preds_df, epi_df, farm_targets, args.output)

    print("Done.")


if __name__ == "__main__":
    main()
