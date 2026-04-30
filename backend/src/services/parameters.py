from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.parameters import Parameter
from src.models.species import Species
from src.schemas.parameters import ParameterCreate, ParameterUpdate


async def get_all_parameters(db: AsyncSession) -> list[Parameter]:
    result = await db.execute(select(Parameter).order_by(Parameter.species_id, Parameter.id))
    return list(result.scalars().all())


async def get_parameter_by_id(db: AsyncSession, parameter_id: int) -> Parameter | None:
    result = await db.execute(select(Parameter).where(Parameter.id == parameter_id))
    return result.scalar_one_or_none()


async def get_parameters_by_species(db: AsyncSession, species_id: int) -> list[Parameter]:
    result = await db.execute(select(Parameter).where(Parameter.species_id == species_id).order_by(Parameter.id))
    return list(result.scalars().all())


async def _validate_species_exists(db: AsyncSession, species_id: int) -> None:
    """Raises ValueError if the given species_id does not exist."""
    result = await db.execute(select(Species).where(Species.id == species_id))
    if result.scalar_one_or_none() is None:
        raise ValueError(f"Species with id {species_id} not found")


async def create_parameter(db: AsyncSession, payload: ParameterCreate) -> Parameter:
    await _validate_species_exists(db, payload.species_id)

    new_param = Parameter(
        species_id=payload.species_id,
        feature=payload.feature,
        score_method=payload.score_method,
        weight=payload.weight,
        trap_left_tol=payload.trap_left_tol,
        trap_right_tol=payload.trap_right_tol,
    )
    db.add(new_param)
    await db.commit()

    result = await db.execute(select(Parameter).where(Parameter.id == new_param.id))
    return result.scalar_one()


async def update_parameter(db: AsyncSession, parameter_id: int, payload: ParameterUpdate) -> Parameter | None:
    result = await db.execute(select(Parameter).where(Parameter.id == parameter_id))
    param = result.scalar_one_or_none()

    if param is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    # If species_id is being changed, make sure the new one exists
    if "species_id" in update_data:
        await _validate_species_exists(db, update_data["species_id"])

    for field, value in update_data.items():
        setattr(param, field, value)

    await db.commit()

    refreshed = await db.execute(select(Parameter).where(Parameter.id == parameter_id))
    return refreshed.scalar_one()


async def delete_parameter(db: AsyncSession, parameter_id: int) -> bool:
    result = await db.execute(select(Parameter).where(Parameter.id == parameter_id))
    param = result.scalar_one_or_none()

    if param is None:
        return False

    await db.delete(param)
    await db.commit()
    return True
