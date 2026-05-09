import pytest
from shapely.geometry import Polygon

from src.models.waterways import Waterway
from src.schemas.constants import RIPARIAN_BUFFER_M
from src.services.riparian import get_riparian_flags


@pytest.fixture(scope="function")
async def seeded_db(async_session):
    """
    Insert a single straight waterway line into PostGIS.
    CRS: EPSG:4326
    """

    waterway = Waterway(
        name="Test River",
        waterway="river",
        geometry=("SRID=4326;LINESTRING (126.6700 -8.6430, 126.6710 -8.6430)"),
    )

    async_session.add(waterway)
    await async_session.flush()

    yield async_session


async def test_riparian_true_within_buffer(seeded_db):
    """Test that a farm within the riparian buffer is correctly flagged as riparian."""
    farm = Polygon(
        [
            (126.6701, -8.6431),
            (126.6701, -8.6429),
            (126.6703, -8.6429),
            (126.6703, -8.6431),
        ]
    )

    result = await get_riparian_flags(seeded_db, farm)

    assert result["riparian"] is True
    assert result["distance_to_nearest_waterway_m"] < RIPARIAN_BUFFER_M


async def test_riparian_false_outside_buffer(seeded_db):
    """Test that a farm outside the riparian buffer is correctly flagged as non-riparian."""
    farm = Polygon(
        [
            (126.6720, -8.6450),
            (126.6720, -8.6445),
            (126.6725, -8.6445),
            (126.6725, -8.6450),
        ]
    )

    result = await get_riparian_flags(seeded_db, farm)

    assert result["riparian"] is False
    assert result["distance_to_nearest_waterway_m"] >= RIPARIAN_BUFFER_M
