import io

import pandas as pd
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.epi import EpiInputRow
from src.services.farm import get_farm_by_id
from src.services.raw_scoring import get_raw_scores
from src.services.species import get_recommend_config, get_species_by_ids


class EpiCSVError(Exception):
    """Custom exception for errors encountered during EPI CSV import."""

    pass


def validate_epi_dataframe(df: pd.DataFrame) -> None:
    """
    Validate EPI input CSV structure and row-level data.

    Raises EpiCSVError with a clear message if validation fails.
    """

    required_cols = {"farm_id", "species_id", "farm_mean_epi"}
    missing = required_cols - set(df.columns)

    if missing:
        raise EpiCSVError(f"Missing required columns: {sorted(missing)}")

    errors = []

    for i, row in df[list(required_cols)].iterrows():
        try:
            EpiInputRow(**row.to_dict())
        except ValidationError as e:
            messages = [err.get("msg").replace("Value error, ", "") for err in e.errors()]
            error_text = " | ".join(messages)
            errors.append(f"Row {i + 1}: {error_text}")

    if errors:
        raise EpiCSVError("Invalid EPI CSV data:\n" + "\n".join(errors[:10]))


async def process_epi_csv(
    db: AsyncSession,
    csv_bytes: bytes,
) -> bytes:
    """Process EPI CSV data and return enriched CSV with raw scores."""
    cfg = get_recommend_config()

    # Read CSV
    try:
        epi_df = pd.read_csv(io.BytesIO(csv_bytes))
    except Exception as e:
        raise EpiCSVError(f"Error reading EPI CSV: {str(e)}")

    # Validate schema
    validate_epi_dataframe(epi_df)

    # Identify scope
    unique_species_ids = epi_df["species_id"].unique().tolist()
    unique_farm_ids = epi_df["farm_id"].unique().tolist()

    # Fetch existing records
    existing_farms = await get_farm_by_id(db, unique_farm_ids)
    existing_species = await get_species_by_ids(db, unique_species_ids)

    # Extract valid IDs into sets for fast comparison
    valid_farm_ids = {farm.id for farm in existing_farms}
    valid_species_ids = {species.id for species in existing_species}

    # Calculate differences to find IDs that don't exist in the DB
    missing_farms = set(unique_farm_ids) - valid_farm_ids
    missing_species = set(unique_species_ids) - valid_species_ids

    # Aggregate errors if any missing IDs are found
    db_errors = []
    if missing_farms:
        db_errors.append(f"Farm IDs not found: {sorted(missing_farms)}")
    if missing_species:
        db_errors.append(f"Species IDs not found: {sorted(missing_species)}")

    if db_errors:
        raise EpiCSVError("Database validation failed: " + " | ".join(db_errors))

    # Call existing raw-score service
    raw_scores = await get_raw_scores(db=db, farm_id_list=unique_farm_ids, cfg=cfg, target_species_ids=unique_species_ids)

    scores_df = pd.DataFrame(raw_scores)

    # Merge
    final_df = epi_df.merge(
        scores_df,
        on=["farm_id", "species_id"],
        how="left",
        validate="many_to_one",
    )

    # Export CSV
    buffer = io.StringIO()
    final_df.to_csv(buffer, index=False)
    buffer.seek(0)

    return buffer.getvalue().encode("utf-8")
