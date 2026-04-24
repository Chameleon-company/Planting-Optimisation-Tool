import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_read_agroforestry_types_returns_records(
    async_client: AsyncClient,
):
    response = await async_client.get("/agroforestry-types")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert any(item["type_name"] == "boundary" for item in data)
