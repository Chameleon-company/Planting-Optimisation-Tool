# ======================================================================================
# Script to generate combined EPI data with raw MCDA scores for each feature
#
# This script uses pre-ingested datasets to calculate the raw scores
# use the API within POT for more accurate results.
# This script is meant for testing and development purposes, and is not intended for
# production use.
# ======================================================================================
from pathlib import Path

import pandas as pd

from app.orchestrators import get_raw_scores_batch

features = ["rainfall_mm", "temperature_celsius", "elevation_m", "ph", "soil_texture"]

script_dir = Path(__file__).parent
input_csv_path = script_dir / "scripts/aggregated_epi_data.csv"

# Load EPI data
epi_df = pd.read_csv(input_csv_path)

# Identify the species present in the EPI data
unique_species_in_data = epi_df["species_id"].unique().tolist()

# Get the list of unique farm IDs that need processing
unique_farm_ids = epi_df["farm_id"].unique().tolist()

# Call orchestrator with the specific species and farm IDs
# This returns a list of dicts: [{'farm_id':..., 'species_id':..., 'feat1':...}, ...]
raw_scores_list = get_raw_scores_batch(farm_id_list=unique_farm_ids, target_species_ids=unique_species_in_data)

# Convert to a Lookup DataFrame
scores_lookup_df = pd.DataFrame(raw_scores_list)

# Merge
final_df = epi_df.merge(scores_lookup_df, on=["farm_id", "species_id"], how="left")

# Now final_df has all the scan data PLUS the raw MCDA scores for every feature
output_csv_path = script_dir / "scripts/epi_farm_species_scores_data.csv"
final_df.to_csv(output_csv_path, index=False)
