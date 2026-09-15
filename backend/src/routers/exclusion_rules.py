from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import get_user_id, limiter, require_role
from src.schemas.exclusion_rules import (
    SpeciesDependencyCreate,
    SpeciesDependencyRead,
    SpeciesDependencyUpdate,
    SpeciesExclusionRuleCreate,
    SpeciesExclusionRuleRead,
    SpeciesExclusionRuleUpdate,
)
from src.schemas.user import Role, UserRead
from src.services import exclusion_rules as exclusion_rules_service

router = APIRouter()

exclusion_rules_router = APIRouter(
    prefix="/exclusion-rules",
    tags=["Exclusion Rules"],
)
dependencies_router = APIRouter(
    prefix="/species-dependencies",
    tags=["Species Dependencies"],
)


@exclusion_rules_router.get(
    "",
    response_model=List[SpeciesExclusionRuleRead],
)
@limiter.limit("30/minute", key_func=get_user_id)
async def list_exclusion_rules(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Return all species exclusion rules. Requires ADMIN role."""
    return await exclusion_rules_service.get_all_exclusion_rules(db)


@exclusion_rules_router.get(
    "/{rule_id}",
    response_model=SpeciesExclusionRuleRead,
)
@limiter.limit("30/minute", key_func=get_user_id)
async def get_exclusion_rule(
    request: Request,
    rule_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Return one species exclusion rule by ID. Requires ADMIN role."""
    rule = await exclusion_rules_service.get_exclusion_rule_by_id(
        db,
        rule_id,
    )

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exclusion rule not found",
        )

    return rule


@exclusion_rules_router.post(
    "",
    response_model=SpeciesExclusionRuleRead,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute", key_func=get_user_id)
async def create_exclusion_rule(
    request: Request,
    payload: SpeciesExclusionRuleCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Create a species exclusion rule. Requires ADMIN role."""
    try:
        return await exclusion_rules_service.create_exclusion_rule(
            db,
            payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@exclusion_rules_router.patch(
    "/{rule_id}",
    response_model=SpeciesExclusionRuleRead,
)
@limiter.limit("10/minute", key_func=get_user_id)
async def update_exclusion_rule(
    request: Request,
    rule_id: int,
    payload: SpeciesExclusionRuleUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Update a species exclusion rule. Requires ADMIN role."""
    try:
        rule = await exclusion_rules_service.update_exclusion_rule(
            db,
            rule_id,
            payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exclusion rule not found",
        )

    return rule


@exclusion_rules_router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("10/minute", key_func=get_user_id)
async def delete_exclusion_rule(
    request: Request,
    rule_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Delete a species exclusion rule. Requires ADMIN role."""
    deleted = await exclusion_rules_service.delete_exclusion_rule(
        db,
        rule_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exclusion rule not found",
        )

    return


@dependencies_router.get(
    "",
    response_model=List[SpeciesDependencyRead],
)
@limiter.limit("30/minute", key_func=get_user_id)
async def list_dependencies(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Return all species dependencies. Requires ADMIN role."""
    return await exclusion_rules_service.get_all_dependencies(db)


@dependencies_router.get(
    "/{dependency_id}",
    response_model=SpeciesDependencyRead,
)
@limiter.limit("30/minute", key_func=get_user_id)
async def get_dependency(
    request: Request,
    dependency_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Return one species dependency by ID. Requires ADMIN role."""
    dependency = await exclusion_rules_service.get_dependency_by_id(
        db,
        dependency_id,
    )

    if dependency is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Species dependency not found",
        )

    return dependency


@dependencies_router.post(
    "",
    response_model=SpeciesDependencyRead,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute", key_func=get_user_id)
async def create_dependency(
    request: Request,
    payload: SpeciesDependencyCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Create a species dependency. Requires ADMIN role."""
    try:
        return await exclusion_rules_service.create_dependency(
            db,
            payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@dependencies_router.patch(
    "/{dependency_id}",
    response_model=SpeciesDependencyRead,
)
@limiter.limit("10/minute", key_func=get_user_id)
async def update_dependency(
    request: Request,
    dependency_id: int,
    payload: SpeciesDependencyUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Update a species dependency. Requires ADMIN role."""
    try:
        dependency = await exclusion_rules_service.update_dependency(
            db,
            dependency_id,
            payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    if dependency is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Species dependency not found",
        )

    return dependency


@dependencies_router.delete(
    "/{dependency_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("10/minute", key_func=get_user_id)
async def delete_dependency(
    request: Request,
    dependency_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Delete a species dependency. Requires ADMIN role."""
    deleted = await exclusion_rules_service.delete_dependency(
        db,
        dependency_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Species dependency not found",
        )

    return


router.include_router(exclusion_rules_router)
router.include_router(dependencies_router)
