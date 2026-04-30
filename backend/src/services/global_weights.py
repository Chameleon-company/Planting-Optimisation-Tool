import csv
import io
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.global_weights import GlobalWeights, GlobalWeightsRun
from src.schemas.global_weights import GlobalWeightsCSVMeta, GlobalWeightsCSVRow


def parse_global_weights_csv(file) -> tuple[GlobalWeightsCSVMeta, list[GlobalWeightsCSVRow]]:
    reader = csv.DictReader(file)

    meta = None
    rows: list[GlobalWeightsCSVRow] = []

    for i, raw in enumerate(reader):
        feature = raw.get("feature")

        if i == 0 and feature == "__META__":
            rf_bootstraps = raw.get("rf_bootstraps")
            rf_early_stopped = raw.get("rf_early_stopped")

            if not rf_bootstraps or not rf_early_stopped:
                raise ValueError("META row must define rf_bootstraps and rf_early_stopped")

            meta = GlobalWeightsCSVMeta(
                rf_bootstraps=int(rf_bootstraps),
                rf_early_stopped=rf_early_stopped.lower() == "true",
            )

            continue

        rows.append(
            GlobalWeightsCSVRow(
                feature=raw["feature"],
                mean_weight=float(raw["mean_weight"]),
                ci_lower=float(raw["ci_lower"]),
                ci_upper=float(raw["ci_upper"]),
            )
        )

    if meta is None:
        raise ValueError("CSV is missing required __META__ row")

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
        rf_bootstraps=meta.rf_bootstraps,
        rf_early_stopped=meta.rf_early_stopped,
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
