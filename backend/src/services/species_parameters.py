from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.parameters import Parameter


async def get_species_parameters_as_dicts(db: AsyncSession):
    stmt = select(
        Parameter.id,
        Parameter.species_id,
        Parameter.feature,
        Parameter.score_method,
        Parameter.weight,
        Parameter.trap_left_tol,
        Parameter.trap_right_tol,
    )
    result = await db.execute(stmt)
    rows = result.mappings().all()
    return [dict(row) for row in rows]
