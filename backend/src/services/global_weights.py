import csv
import io
from uuid import uuid4

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.global_weights import GlobalWeights, GlobalWeightsRun
from src.schemas.global_weights import GlobalWeightsCSVMeta, GlobalWeightsCSVRow
from src.services.species import get_recommend_config


class GlobalWeightsCSVError(Exception):
    """Custom exception for errors encountered during Global Weights CSV import."""

    pass


def parse_global_weights_csv(file) -> tuple[GlobalWeightsCSVMeta, list[GlobalWeightsCSVRow]]:
    reader = csv.DictReader(file)

    # DictReader is silent on empty files
    if reader.fieldnames is None:
        raise GlobalWeightsCSVError("CSV file is empty or missing a header row")

    required_columns = {
        "feature",
        "mean_weight",
        "ci_lower",
        "ci_upper",
    }

    missing_columns = required_columns - set(reader.fieldnames or [])
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise GlobalWeightsCSVError(f"CSV is missing required columns: {missing}")

    # Grab the raw feature keys expected by the system
    config_data = get_recommend_config()
    expected_features = set(config_data.get("features", {}).keys())

    # Track what we actually find in the CSV
    found_features = set()

    meta = None
    rows: list[GlobalWeightsCSVRow] = []

    for i, raw in enumerate(reader):
        feature = raw.get("feature", "")

        if i == 0 and feature == "__META__":
            bootstraps = raw.get("bootstraps")
            bootstrap_early_stopped = raw.get("bootstrap_early_stopped")

            if not bootstraps or not bootstrap_early_stopped:
                raise GlobalWeightsCSVError("META row must define bootstraps and bootstrap_early_stopped")

            value = bootstrap_early_stopped.strip().lower()
            if value not in {"true", "false"}:
                raise GlobalWeightsCSVError("META row bootstrap_early_stopped must be 'true' or 'false'")

            meta = GlobalWeightsCSVMeta(
                bootstraps=int(bootstraps),
                bootstrap_early_stopped=value == "true",
            )

            continue
        # Reject unknown features
        if feature not in expected_features:
            raise GlobalWeightsCSVError(f"Row {i + 1} has unknown feature: '{feature}'")
        try:
            row = GlobalWeightsCSVRow(
                feature=raw["feature"],
                mean_weight=float(raw["mean_weight"]),
                ci_lower=float(raw["ci_lower"]),
                ci_upper=float(raw["ci_upper"]),
            )
            rows.append(row)

            # Record the feature we just successfully parsed
            found_features.add(feature)

        except ValidationError as e:
            messages = [err.get("msg").replace("Value error, ", "") for err in e.errors()]
            error_text = " | ".join(messages)

            # Note: use i + 1 because i is 0-indexed, and row 1 is the CSV header.
            raise GlobalWeightsCSVError(f"Row {i + 1} {feature}: {error_text}")

        except ValueError:
            # Catches letters where a float should be (e.g., float("abc"))
            raise GlobalWeightsCSVError(f"Row {i + 1} {feature}: contains invalid numbers.")

    if meta is None:
        raise GlobalWeightsCSVError("CSV is missing required __META__ row")

    # Check for missing features
    missing_features = expected_features - found_features
    if missing_features:
        missing_str = ", ".join(sorted(list(missing_features)))
        raise GlobalWeightsCSVError(f"CSV is missing required features: {missing_str}")

    return meta, rows


def ensure_text_stream(file):
    if isinstance(file, io.TextIOBase):
        return file  # already text
    return io.TextIOWrapper(file, encoding="utf-8")


async def import_global_weights_from_csv(
    db: AsyncSession,
    csv_file,
    dataset_hash: str,
):
    # Convert UploadFile.file (bytes) → text stream
    text_stream = ensure_text_stream(csv_file)

    meta, weight_rows = parse_global_weights_csv(text_stream)

    # Create new run
    run = GlobalWeightsRun(
        id=uuid4(),
        dataset_hash=dataset_hash,
        bootstraps=meta.bootstraps,
        bootstrap_early_stopped=meta.bootstrap_early_stopped,
        source="Imported from CSV",
    )

    db.add(run)
    await db.flush()

    for row in weight_rows:
        db.add(
            GlobalWeights(
                run_id=run.id,
                feature=row.feature,
                mean_weight=row.mean_weight,
                ci_lower=row.ci_lower,
                ci_upper=row.ci_upper,
                ci_width=row.ci_upper - row.ci_lower,
                touches_zero=row.ci_lower == 0,
            )
        )

    await db.commit()
    return run.id


async def get_latest_global_weights(db: AsyncSession) -> dict[str, float] | None:
    run = await db.execute(select(GlobalWeightsRun).order_by(GlobalWeightsRun.created_at.desc()).limit(1))
    run = run.scalar_one_or_none()

    if not run:
        return None

    weights = await db.execute(select(GlobalWeights).where(GlobalWeights.run_id == run.id))

    return {w.feature: w.mean_weight for w in weights.scalars().all()}
