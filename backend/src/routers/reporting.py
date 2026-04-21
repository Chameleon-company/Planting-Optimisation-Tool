from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import get_user_id, limiter, require_role
from src.domains.reporting import FarmReportContract
from src.schemas.user import Role, UserRead
from src.services import reporting as reporting_service
from src.services import reporting_export

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/farm/{farm_id}", response_model=FarmReportContract)
@limiter.limit("10/minute", key_func=get_user_id)
async def get_farm_report(
    request: Request,
    farm_id: int,
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
    db: AsyncSession = Depends(get_db_session),
):
    """Returns a structured report of saved species recommendations for a single farm.
    Officers can only access their own farms. Supervisors and Admins can access any farm.
    """
    user_id_filter = current_user.id if current_user.role == Role.OFFICER else None
    report = await reporting_service.get_farm_report(db, farm_id, user_id=user_id_filter)

    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found or access denied")

    return report


@router.get("/farms", response_model=list[FarmReportContract])
@limiter.limit("10/minute", key_func=get_user_id)
async def get_all_farms_report(
    request: Request,
    current_user: UserRead = Depends(require_role(Role.SUPERVISOR)),
    db: AsyncSession = Depends(get_db_session),
):
    """Returns reports for all farms. Supervisors see only their own farms.
    Requires SUPERVISOR role or higher. Admins can see all farms.
    """
    if current_user.role == Role.ADMIN:
        user_id_filter = None
    else:
        user_id_filter = current_user.id

    return await reporting_service.get_all_farms_report(db, user_id=user_id_filter)


@router.get("/farms/export/docx")
@limiter.limit("10/minute", key_func=get_user_id)
async def export_all_farms_report_docx(
    request: Request,
    current_user: UserRead = Depends(require_role(Role.SUPERVISOR)),
    db: AsyncSession = Depends(get_db_session),
):
    """Downloads a single DOCX report containing all farms, one section per farm.
    Supervisors see only their own farms. Admins see all farms.
    """
    user_id_filter = None if current_user.role == Role.ADMIN else current_user.id
    reports = await reporting_service.get_all_farms_report(db, user_id=user_id_filter)

    file_bytes = reporting_export.generate_all_farms_docx(reports)

    return Response(
        content=file_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="all_farms_report.docx"'},
    )


@router.get("/farms/export/pdf")
@limiter.limit("10/minute", key_func=get_user_id)
async def export_all_farms_report_pdf(
    request: Request,
    current_user: UserRead = Depends(require_role(Role.SUPERVISOR)),
    db: AsyncSession = Depends(get_db_session),
):
    """Downloads a single PDF report containing all farms, one page per farm.
    Supervisors see only their own farms. Admins see all farms.
    """
    user_id_filter = None if current_user.role == Role.ADMIN else current_user.id
    reports = await reporting_service.get_all_farms_report(db, user_id=user_id_filter)

    file_bytes = reporting_export.generate_all_farms_pdf(reports)

    return Response(
        content=file_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="all_farms_report.pdf"'},
    )


@router.get("/farm/{farm_id}/export/docx")
@limiter.limit("10/minute", key_func=get_user_id)
async def export_farm_report_docx(
    request: Request,
    farm_id: int,
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
    db: AsyncSession = Depends(get_db_session),
):
    """Downloads a DOCX formatted report for a single farm.
    Officers can only access their own farms. Supervisors and Admins can access any farm.
    """
    user_id_filter = current_user.id if current_user.role == Role.OFFICER else None
    report = await reporting_service.get_farm_report(db, farm_id, user_id=user_id_filter)

    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found or access denied")

    file_bytes = reporting_export.generate_docx(report)
    filename = f"farm_{farm_id}_report.docx"

    return Response(
        content=file_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/farm/{farm_id}/export/pdf")
@limiter.limit("10/minute", key_func=get_user_id)
async def export_farm_report_pdf(
    request: Request,
    farm_id: int,
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
    db: AsyncSession = Depends(get_db_session),
):
    """Downloads a PDF formatted report for a single farm.
    Officers can only access their own farms. Supervisors and Admins can access any farm.
    """
    user_id_filter = current_user.id if current_user.role == Role.OFFICER else None
    report = await reporting_service.get_farm_report(db, farm_id, user_id=user_id_filter)

    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found or access denied")

    file_bytes = reporting_export.generate_pdf(report)
    filename = f"farm_{farm_id}_report.pdf"

    return Response(
        content=file_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
