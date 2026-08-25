from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.exclusion_rules import SpeciesDependency, SpeciesExclusionRule
from src.models.species import Species
from src.schemas.exclusion_rules import (
    SpeciesDependencyCreate,
    SpeciesDependencyUpdate,
    SpeciesExclusionRuleCreate,
    SpeciesExclusionRuleUpdate,
)


async def _validate_species_exists(db: AsyncSession, species_id: int) -> None:
    result = await db.execute(select(Species.id).where(Species.id == species_id))
    if result.scalar_one_or_none() is None:
        raise ValueError(f"Species with id {species_id} not found")


async def _validate_dependency(
    db: AsyncSession,
    focal_species_id: int,
    required_partner_id: int,
) -> None:
    if focal_species_id == required_partner_id:
        raise ValueError("A species cannot depend on itself")

    await _validate_species_exists(db, focal_species_id)
    await _validate_species_exists(db, required_partner_id)


async def get_all_exclusion_rules(
    db: AsyncSession,
) -> list[SpeciesExclusionRule]:
    result = await db.execute(select(SpeciesExclusionRule).order_by(SpeciesExclusionRule.id))
    return list(result.scalars().all())


async def get_exclusion_rule_by_id(
    db: AsyncSession,
    rule_id: int,
) -> SpeciesExclusionRule | None:
    result = await db.execute(select(SpeciesExclusionRule).where(SpeciesExclusionRule.id == rule_id))
    return result.scalar_one_or_none()


async def create_exclusion_rule(
    db: AsyncSession,
    payload: SpeciesExclusionRuleCreate,
) -> SpeciesExclusionRule:
    await _validate_species_exists(db, payload.species_id)

    rule = SpeciesExclusionRule(**payload.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


async def update_exclusion_rule(
    db: AsyncSession,
    rule_id: int,
    payload: SpeciesExclusionRuleUpdate,
) -> SpeciesExclusionRule | None:
    rule = await get_exclusion_rule_by_id(db, rule_id)

    if rule is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    if any(value is None for value in update_data.values()):
        raise ValueError("Exclusion rule fields cannot be null")

    if "species_id" in update_data:
        await _validate_species_exists(db, update_data["species_id"])

    for field, value in update_data.items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)
    return rule


async def delete_exclusion_rule(
    db: AsyncSession,
    rule_id: int,
) -> bool:
    rule = await get_exclusion_rule_by_id(db, rule_id)

    if rule is None:
        return False

    await db.delete(rule)
    await db.commit()
    return True


async def get_all_dependencies(
    db: AsyncSession,
) -> list[SpeciesDependency]:
    result = await db.execute(select(SpeciesDependency).order_by(SpeciesDependency.id))
    return list(result.scalars().all())


async def get_dependency_by_id(
    db: AsyncSession,
    dependency_id: int,
) -> SpeciesDependency | None:
    result = await db.execute(select(SpeciesDependency).where(SpeciesDependency.id == dependency_id))
    return result.scalar_one_or_none()


async def create_dependency(
    db: AsyncSession,
    payload: SpeciesDependencyCreate,
) -> SpeciesDependency:
    await _validate_dependency(
        db,
        payload.focal_species_id,
        payload.required_partner_id,
    )

    dependency = SpeciesDependency(**payload.model_dump())
    db.add(dependency)
    await db.commit()
    await db.refresh(dependency)
    return dependency


async def update_dependency(
    db: AsyncSession,
    dependency_id: int,
    payload: SpeciesDependencyUpdate,
) -> SpeciesDependency | None:
    dependency = await get_dependency_by_id(db, dependency_id)

    if dependency is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    if any(value is None for value in update_data.values()):
        raise ValueError("Dependency fields cannot be null")

    focal_species_id = update_data.get(
        "focal_species_id",
        dependency.focal_species_id,
    )
    required_partner_id = update_data.get(
        "required_partner_id",
        dependency.required_partner_id,
    )

    await _validate_dependency(
        db,
        focal_species_id,
        required_partner_id,
    )

    for field, value in update_data.items():
        setattr(dependency, field, value)

    await db.commit()
    await db.refresh(dependency)
    return dependency


async def delete_dependency(
    db: AsyncSession,
    dependency_id: int,
) -> bool:
    dependency = await get_dependency_by_id(db, dependency_id)

    if dependency is None:
        return False

    await db.delete(dependency)
    await db.commit()
    return True
