import pandas as pd

from .preprocessing import (
    outside_range,
    select_model_features,
)


def generate_warnings(species_name, temp, rain, elev, slope, ph, optima_df, slope_min, slope_max) -> list[str]:
    """Generate warnings for unsuitable environmental conditions."""

    warnings = []

    if not (slope_min <= slope <= slope_max):
        warnings.append("Slope is outside the observed farm conditions")

    row = optima_df.loc[optima_df["species_name"] == species_name]

    if row.empty:
        warnings.append("Species not found in optimal range table")
        return warnings

    r = row.iloc[0]

    if not (r["rainfall_min"] <= rain <= r["rainfall_max"]):
        warnings.append("Rainfall is outside the species' optimal range")

    if not (r["temp_min"] <= temp <= r["temp_max"]):
        warnings.append("Temperature is outside the species' optimal range")

    if not (r["ph_min"] <= ph <= r["ph_max"]):
        warnings.append("Soil pH is outside the species' optimal range")

    if not (r["alt_min"] <= elev <= r["alt_max"]):
        warnings.append("Altitude is outside the species' optimal range")

    return warnings


def prepare_prediction_input(species_name, temp, rain, elev, slope, ph, trunk_circumference, planted_month, age_months, optima_df) -> pd.DataFrame:
    """Prepare the 13 input features for survival prediction."""

    opt_row = optima_df.loc[optima_df["species_name"] == species_name]

    if opt_row.empty:
        rain_outside = 0.0
        temp_outside = 0.0
        elev_outside = 0.0
        ph_outside = 0.0
    else:
        r = opt_row.iloc[0]

        rain_outside = float(outside_range(rain, r["rainfall_min"], r["rainfall_max"]))

        temp_outside = float(outside_range(temp, r["temp_min"], r["temp_max"]))

        elev_outside = float(outside_range(elev, r["alt_min"], r["alt_max"]))

        ph_outside = float(outside_range(ph, r["ph_min"], r["ph_max"]))

    sample = pd.DataFrame(
        [
            {
                "temp_mean": temp,
                "rain_mean": rain,
                "elev_mean": elev,
                "slope_mean": slope,
                "ph": ph,
                "correct_tree_species_name": species_name,
                "trunk_circumference": trunk_circumference,
                "planted_month": planted_month,
                "age_months": age_months,
                "rain_outside_opt": rain_outside,
                "temp_outside_opt": temp_outside,
                "elev_outside_opt": elev_outside,
                "ph_outside_opt": ph_outside,
            }
        ]
    )

    return select_model_features(sample)


def predict_survival(species_name, temp, rain, elev, slope, ph, trunk_circumference, planted_month, age_months, optima_df, pipeline, threshold, slope_min, slope_max) -> dict:
    """Predict tree survival probability and generate warnings."""

    warnings = generate_warnings(species_name, temp, rain, elev, slope, ph, optima_df, slope_min, slope_max)

    sample = prepare_prediction_input(species_name, temp, rain, elev, slope, ph, trunk_circumference, planted_month, age_months, optima_df)

    # Calculate survival probability
    prob_survived = float(pipeline.predict_proba(sample)[0][1])

    # Apply the tuned decision threshold
    prediction = "Survived" if prob_survived > 1 - threshold else "Died"

    return {"survival_probability": prob_survived * 100, "prediction": prediction, "warnings": warnings}
