from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import get_user_id, limiter, require_role
from src.models.global_weights import GlobalWeights, GlobalWeightsRun
from src.schemas.global_weights import GlobalWeightItemSchema, GlobalWeightsRunDetailSchema, GlobalWeightsRunSummarySchema
from src.schemas.user import Role, UserRead
from src.services.epi_processing import process_epi_csv
from src.services.global_weights import import_global_weights_from_csv

router = APIRouter(prefix="/global-weights", tags=["Global Weights"])


@router.get(
    "/runs",
    response_model=list[GlobalWeightsRunSummarySchema],
    response_model_exclude_none=True,
)
@limiter.limit("30/minute", key_func=get_user_id)
async def list_global_weights_runs(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    result = await db.execute(select(GlobalWeightsRun).order_by(GlobalWeightsRun.created_at.desc()))

    runs = result.scalars().all()

    return [
        GlobalWeightsRunSummarySchema(
            run_id=r.id,
            created_at=r.created_at,
            bootstraps=r.bootstraps,
            bootstrap_early_stopped=r.bootstrap_early_stopped,
            source=r.source,
        )
        for r in runs
    ]


@router.get(
    "/runs/{run_id}",
    response_model=GlobalWeightsRunDetailSchema,
    response_model_exclude_none=True,
)
@limiter.limit("30/minute", key_func=get_user_id)
async def get_global_weights_run(
    request: Request,
    run_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    run_result = await db.execute(select(GlobalWeightsRun).where(GlobalWeightsRun.id == run_id))
    run = run_result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=404, detail="Global weight run not found")

    weights_result = await db.execute(select(GlobalWeights).where(GlobalWeights.run_id == run.id).order_by(GlobalWeights.mean_weight.desc()))

    weights = weights_result.scalars().all()

    return GlobalWeightsRunDetailSchema(
        run_id=run.id,
        created_at=run.created_at,
        bootstraps=run.bootstraps,
        bootstrap_early_stopped=run.bootstrap_early_stopped,
        source=run.source,
        weights=[
            GlobalWeightItemSchema(
                feature=w.feature,
                mean_weight=w.mean_weight,
                ci_lower=w.ci_lower,
                ci_upper=w.ci_upper,
                ci_width=w.ci_width,
                touches_zero=w.touches_zero,
            )
            for w in weights
        ],
    )


@router.delete(
    "/runs/{run_id}",
    status_code=204,
)
@limiter.limit("10/minute", key_func=get_user_id)
async def delete_global_weights_run(
    request: Request,
    run_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    result = await db.execute(select(GlobalWeightsRun).where(GlobalWeightsRun.id == run_id))
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=404, detail="Global weight run not found")

    await db.execute(delete(GlobalWeightsRun).where(GlobalWeightsRun.id == run_id))

    await db.commit()


@router.post("/import", status_code=201)
@limiter.limit("10/minute", key_func=get_user_id)
async def import_global_weights(
    request: Request,
    file: UploadFile = File(...),
    dataset_hash: str = "manual-import",
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    run_id = await import_global_weights_from_csv(
        db=db,
        csv_file=file.file,
        dataset_hash=dataset_hash,
    )

    return {
        "status": "success",
        "run_id": run_id,
    }


@router.post("/epi-add-scores", response_class=Response)
@limiter.limit("10/minute", key_func=get_user_id)
async def score_epi_csv(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Endpoint to process an EPI CSV file and return a new CSV with scores added."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    csv_bytes = await file.read()

    output_bytes = await process_epi_csv(
        db=db,
        csv_bytes=csv_bytes,
    )

    return Response(
        content=output_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=epi_farm_species_scores_data.csv"},
    )
