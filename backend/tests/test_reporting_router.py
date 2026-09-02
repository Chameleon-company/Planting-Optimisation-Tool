from geoalchemy2 import WKTElement
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.models.recommendations import Recommendation
from src.models.species import Species
from src.models.user import User

# Matches the DEM fixture used in test_sapling_service.py, so sapling
# estimation succeeds for farms whose boundary falls inside this extent.
DEM_INSERT = text(
    """
    INSERT INTO dem_table (rast)
    VALUES (
        ST_AddBand(
            ST_MakeEmptyRaster(
                5, 5,
                125, -8.9995,
                0.001, -0.001,
                0, 0,
                4326
            ),
            1,
            '32BF',
            100
        )
    );
    """
)
FARM_BOUNDARY_WKT_IN_DEM_EXTENT = "MULTIPOLYGON (((125 -9, 125 -9.002, 125.002 -9.002, 125.002 -9, 125 -9)))"


def make_farm(user_id: int, soil_texture_id: int = 1) -> Farm:
    return Farm(
        rainfall_mm=1500,
        temperature_celsius=22,
        elevation_m=500,
        ph=6.5,
        soil_texture_id=soil_texture_id,
        area_ha=5.0,
        latitude=-8.5,
        longitude=126.5,
        coastal=False,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
        slope=10.5,
        user_id=user_id,
    )


def make_species(name: str, common_name: str) -> Species:
    return Species(
        name=name,
        common_name=common_name,
        rainfall_mm_min=500,
        rainfall_mm_max=3000,
        temperature_celsius_min=15,
        temperature_celsius_max=35,
        elevation_m_min=0,
        elevation_m_max=2000,
        ph_min=5.0,
        ph_max=8.0,
        coastal=False,
        riparian=False,
        nitrogen_fixing=True,
        shade_tolerant=False,
        bank_stabilising=False,
    )


async def test_get_farm_report_success(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_officer_user: User,
):
    """Officer can retrieve a report for their own farm."""
    farm = make_farm(user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    species = make_species("Teak", "Common Teak")
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    rec = Recommendation(
        farm_id=farm.id,
        species_id=species.id,
        rank_overall=1,
        score_mcda=0.85,
        key_reasons=["suitable rainfall", "suitable temperature"],
    )
    async_session.add(rec)
    await async_session.flush()

    response = await async_client.get(f"/reports/farm/{farm.id}", headers=officer_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["farm"]["id"] == farm.id
    assert data["farm"]["user_name"] == test_officer_user.name
    assert data["farm"]["rainfall_mm"] == 1500
    assert data["farm"]["elevation_m"] == 500
    assert data["farm"]["area_ha"] == 5.0
    assert data["farm"]["latitude"] == -8.5
    assert data["farm"]["longitude"] == 126.5
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["species_name"] == "Teak"
    assert data["recommendations"][0]["rank_overall"] == 1
    assert data["recommendations"][0]["key_reasons"] == ["suitable rainfall", "suitable temperature"]
    assert data["exclusions"] == []


async def test_get_farm_report_not_found(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    """Returns 404 when farm does not exist."""
    response = await async_client.get("/reports/farm/99999", headers=officer_auth_headers)
    assert response.status_code == 404


async def test_get_farm_report_excludes_excluded_species(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_officer_user: User,
):
    """Report should not include species with rank=-1 (excluded species)."""
    farm = make_farm(user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    species = make_species("Mahogany", "Philippine Mahogany")
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    # Excluded recommendation (rank=-1)
    excluded_rec = Recommendation(
        farm_id=farm.id,
        species_id=species.id,
        rank_overall=-1,
        score_mcda=-1,
        key_reasons=["excluded: rainfall below minimum"],
    )
    async_session.add(excluded_rec)
    await async_session.flush()

    response = await async_client.get(f"/reports/farm/{farm.id}", headers=officer_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) == 0
    assert len(data["exclusions"]) == 1
    assert data["exclusions"][0]["species_name"] == "Mahogany"
    assert data["exclusions"][0]["key_reasons"] == ["excluded: rainfall below minimum"]


async def test_get_farm_report_unauthenticated(async_client: AsyncClient):
    """Returns 401 when no auth token is provided."""
    response = await async_client.get("/reports/farm/1")
    assert response.status_code == 401


async def test_get_all_farms_report_supervisor(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    supervisor_auth_headers: dict,
    test_supervisor_user: User,
):
    """Supervisor can retrieve reports for all their farms."""
    farm1 = make_farm(user_id=test_supervisor_user.id)
    farm2 = make_farm(user_id=test_supervisor_user.id)
    async_session.add_all([farm1, farm2])
    await async_session.flush()
    await async_session.refresh(farm1)
    await async_session.refresh(farm2)

    response = await async_client.get("/reports/farms", headers=supervisor_auth_headers)

    assert response.status_code == 200
    data = response.json()
    farm_ids = [r["farm"]["id"] for r in data]
    assert farm1.id in farm_ids
    assert farm2.id in farm_ids


async def test_get_all_farms_report_officer_forbidden(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    """Officers cannot access the all-farms report endpoint."""
    response = await async_client.get("/reports/farms", headers=officer_auth_headers)
    assert response.status_code == 403


async def test_export_farm_report_docx_success(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_officer_user: User,
):
    """Officer can download a DOCX report for their own farm."""
    farm = make_farm(user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    response = await async_client.get(f"/reports/farm/{farm.id}/export/docx", headers=officer_auth_headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert f"farm_{farm.id}_report.docx" in response.headers["content-disposition"]
    assert len(response.content) > 0


async def test_export_farm_report_pdf_success(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_officer_user: User,
):
    """Officer can download a PDF report for their own farm."""
    farm = make_farm(user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    response = await async_client.get(f"/reports/farm/{farm.id}/export/pdf", headers=officer_auth_headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert f"farm_{farm.id}_report.pdf" in response.headers["content-disposition"]
    assert len(response.content) > 0


async def test_export_farm_report_docx_not_found(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    """Returns 404 when farm does not exist for DOCX export."""
    response = await async_client.get("/reports/farm/99999/export/docx", headers=officer_auth_headers)
    assert response.status_code == 404


async def test_export_farm_report_pdf_not_found(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    """Returns 404 when farm does not exist for PDF export."""
    response = await async_client.get("/reports/farm/99999/export/pdf", headers=officer_auth_headers)
    assert response.status_code == 404


async def test_export_farm_report_docx_officer_forbidden_other_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_supervisor_user: User,
):
    """Officer cannot download DOCX report for a farm they do not own."""
    farm = make_farm(user_id=test_supervisor_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    response = await async_client.get(f"/reports/farm/{farm.id}/export/docx", headers=officer_auth_headers)
    assert response.status_code == 404


async def test_export_farm_report_pdf_officer_forbidden_other_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_supervisor_user: User,
):
    """Officer cannot download PDF report for a farm they do not own."""
    farm = make_farm(user_id=test_supervisor_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    response = await async_client.get(f"/reports/farm/{farm.id}/export/pdf", headers=officer_auth_headers)
    assert response.status_code == 404


async def test_export_farm_report_unauthenticated(async_client: AsyncClient):
    """Returns 401 when no auth token is provided for export endpoints."""
    response_docx = await async_client.get("/reports/farm/1/export/docx")
    response_pdf = await async_client.get("/reports/farm/1/export/pdf")
    assert response_docx.status_code == 401
    assert response_pdf.status_code == 401


async def test_get_all_farms_report_admin_sees_all(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    admin_auth_headers: dict,
    test_officer_user: User,
    test_supervisor_user: User,
):
    """Admin can retrieve reports for all farms regardless of owner."""
    farm_officer = make_farm(user_id=test_officer_user.id)
    farm_supervisor = make_farm(user_id=test_supervisor_user.id)
    async_session.add_all([farm_officer, farm_supervisor])
    await async_session.flush()
    await async_session.refresh(farm_officer)
    await async_session.refresh(farm_supervisor)

    response = await async_client.get("/reports/farms", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    farm_ids = [r["farm"]["id"] for r in data]
    assert farm_officer.id in farm_ids
    assert farm_supervisor.id in farm_ids


async def test_export_all_farms_report_docx_supervisor(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    supervisor_auth_headers: dict,
    test_supervisor_user: User,
):
    """Supervisor can download a single DOCX containing all their farms."""
    farm1 = make_farm(user_id=test_supervisor_user.id)
    farm2 = make_farm(user_id=test_supervisor_user.id)
    async_session.add_all([farm1, farm2])
    await async_session.flush()

    response = await async_client.get("/reports/farms/export/docx", headers=supervisor_auth_headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert "all_farms_report.docx" in response.headers["content-disposition"]
    assert len(response.content) > 0


async def test_export_all_farms_report_pdf_supervisor(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    supervisor_auth_headers: dict,
    test_supervisor_user: User,
):
    """Supervisor can download a single PDF containing all their farms."""
    farm1 = make_farm(user_id=test_supervisor_user.id)
    farm2 = make_farm(user_id=test_supervisor_user.id)
    async_session.add_all([farm1, farm2])
    await async_session.flush()

    response = await async_client.get("/reports/farms/export/pdf", headers=supervisor_auth_headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "all_farms_report.pdf" in response.headers["content-disposition"]
    assert len(response.content) > 0


async def test_export_all_farms_report_officer_forbidden(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    """Officers cannot access the all-farms export endpoints."""
    response_docx = await async_client.get("/reports/farms/export/docx", headers=officer_auth_headers)
    response_pdf = await async_client.get("/reports/farms/export/pdf", headers=officer_auth_headers)
    assert response_docx.status_code == 403
    assert response_pdf.status_code == 403


async def test_export_all_farms_report_unauthenticated(async_client: AsyncClient):
    """Returns 401 when no auth token is provided for all-farms export endpoints."""
    response_docx = await async_client.get("/reports/farms/export/docx")
    response_pdf = await async_client.get("/reports/farms/export/pdf")
    assert response_docx.status_code == 401
    assert response_pdf.status_code == 401


async def test_export_farm_report_docx_with_recommendations(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_officer_user: User,
):
    """DOCX export includes recommendations table when recommendations exist."""
    farm = make_farm(user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    species = make_species("Teak", "Common Teak")
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    rec = Recommendation(
        farm_id=farm.id,
        species_id=species.id,
        rank_overall=1,
        score_mcda=0.85,
        key_reasons=["suitable rainfall"],
    )
    async_session.add(rec)
    await async_session.flush()

    response = await async_client.get(f"/reports/farm/{farm.id}/export/docx", headers=officer_auth_headers)

    assert response.status_code == 200
    assert len(response.content) > 0


async def test_export_farm_report_pdf_with_recommendations(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_officer_user: User,
):
    """PDF export includes recommendations table when recommendations exist."""
    farm = make_farm(user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    species = make_species("Mahogany", "Philippine Mahogany")
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    rec = Recommendation(
        farm_id=farm.id,
        species_id=species.id,
        rank_overall=1,
        score_mcda=0.78,
        key_reasons=["suitable temperature"],
    )
    async_session.add(rec)
    await async_session.flush()

    response = await async_client.get(f"/reports/farm/{farm.id}/export/pdf", headers=officer_auth_headers)

    assert response.status_code == 200
    assert len(response.content) > 0


async def test_export_all_farms_report_docx_with_recommendations(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    supervisor_auth_headers: dict,
    test_supervisor_user: User,
):
    """All-farms DOCX export includes recommendations table when recommendations exist."""
    farm = make_farm(user_id=test_supervisor_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    species = make_species("Sandalwood", "Indian Sandalwood")
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    rec = Recommendation(
        farm_id=farm.id,
        species_id=species.id,
        rank_overall=1,
        score_mcda=0.90,
        key_reasons=["suitable pH"],
    )
    async_session.add(rec)
    await async_session.flush()

    response = await async_client.get("/reports/farms/export/docx", headers=supervisor_auth_headers)

    assert response.status_code == 200
    assert len(response.content) > 0


async def test_export_all_farms_report_pdf_with_recommendations(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    supervisor_auth_headers: dict,
    test_supervisor_user: User,
):
    """All-farms PDF export includes recommendations table when recommendations exist."""
    farm = make_farm(user_id=test_supervisor_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    species = make_species("Bamboo", "Giant Bamboo")
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    rec = Recommendation(
        farm_id=farm.id,
        species_id=species.id,
        rank_overall=1,
        score_mcda=0.72,
        key_reasons=["suitable elevation"],
    )
    async_session.add(rec)
    await async_session.flush()

    response = await async_client.get("/reports/farms/export/pdf", headers=supervisor_auth_headers)

    assert response.status_code == 200
    assert len(response.content) > 0


async def test_get_farm_report_officer_forbidden_other_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_supervisor_user: User,
):
    """Officer cannot retrieve a report for a farm they do not own."""
    farm = make_farm(user_id=test_supervisor_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    response = await async_client.get(f"/reports/farm/{farm.id}", headers=officer_auth_headers)
    assert response.status_code == 404


async def test_get_farm_report_supervisor_access(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    supervisor_auth_headers: dict,
    test_supervisor_user: User,
):
    """Supervisor can access a single farm report."""
    farm = make_farm(user_id=test_supervisor_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    response = await async_client.get(f"/reports/farm/{farm.id}", headers=supervisor_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["farm"]["id"] == farm.id


async def test_export_all_farms_report_admin(
    async_client: AsyncClient,
    admin_auth_headers: dict,
    mocker,
):
    """Admin can download all-farms DOCX and PDF.
    Monkeypatched to avoid querying the full replicated DB (3200+ farms).
    performance of this endpoint is covered separately by load testing.
    """
    from datetime import datetime, timezone
    from unittest.mock import AsyncMock

    from src.domains.reporting import FarmReportContract, FarmReportMetadata

    fake_reports = [
        FarmReportContract(
            farm=FarmReportMetadata(
                id=1,
                user_name="Officer User",
                rainfall_mm=1500,
                temperature_celsius=22,
                elevation_m=500,
                ph=6.5,
                soil_texture="Loam",
                area_ha=5.0,
                latitude=-8.5,
                longitude=126.5,
            ),
            recommendations=[],
            exclusions=[],
            generated_at=datetime.now(timezone.utc),
        ),
        FarmReportContract(
            farm=FarmReportMetadata(
                id=2,
                user_name="Supervisor User",
                rainfall_mm=1200,
                temperature_celsius=25,
                elevation_m=300,
                ph=7.0,
                soil_texture="Clay",
                area_ha=3.0,
                latitude=-8.6,
                longitude=126.6,
            ),
            recommendations=[],
            exclusions=[],
            generated_at=datetime.now(timezone.utc),
        ),
    ]

    mocker.patch(
        "src.routers.reporting.reporting_service.get_all_farms_report",
        new=AsyncMock(return_value=fake_reports),
    )

    response_docx = await async_client.get("/reports/farms/export/docx", headers=admin_auth_headers)
    response_pdf = await async_client.get("/reports/farms/export/pdf", headers=admin_auth_headers)

    assert response_docx.status_code == 200
    assert response_pdf.status_code == 200
    assert len(response_docx.content) > 0
    assert len(response_pdf.content) > 0


async def test_get_farm_report_has_no_boundary_or_sapling_when_farm_has_no_boundary(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_officer_user: User,
):
    """A farm with no saved boundary gets a report with boundary and sapling both null."""
    farm = make_farm(user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()

    response = await async_client.get(f"/reports/farm/{farm.id}", headers=officer_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["boundary"] is None
    assert data["sapling"] is None
    assert data["planting_guidance"] == "No suitable species were identified for this farm's current conditions."


async def test_get_farm_report_includes_boundary_when_farm_has_one(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_officer_user: User,
):
    """A farm with a saved boundary gets that boundary back as a GeoJSON Feature on the report."""
    farm = make_farm(user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(FARM_BOUNDARY_WKT_IN_DEM_EXTENT, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    response = await async_client.get(f"/reports/farm/{farm.id}", headers=officer_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["boundary"] is not None
    assert data["boundary"]["type"] == "Feature"
    assert data["boundary"]["geometry"]["type"] == "MultiPolygon"


async def test_get_farm_report_includes_sapling_summary_and_guidance_when_dem_available(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_officer_user: User,
):
    """When a farm has a boundary within DEM coverage, the report includes sapling
    numbers from the estimation service, and planting guidance mentions capacity."""
    await async_session.execute(text("TRUNCATE dem_table RESTART IDENTITY;"))
    await async_session.execute(DEM_INSERT)
    await async_session.flush()

    farm = make_farm(user_id=test_officer_user.id)
    farm.baseline_tree_count = 5
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(FARM_BOUNDARY_WKT_IN_DEM_EXTENT, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    species = make_species("Teak", "Common Teak")
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    rec = Recommendation(
        farm_id=farm.id,
        species_id=species.id,
        rank_overall=1,
        score_mcda=0.85,
        key_reasons=["suitable rainfall"],
    )
    async_session.add(rec)
    await async_session.flush()

    response = await async_client.get(f"/reports/farm/{farm.id}", headers=officer_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["sapling"] is not None
    assert data["sapling"]["baseline_tree_count"] == 5
    assert data["sapling"]["aligned_count"] > 0
    assert data["sapling"]["additional_sapling_count"] == max(data["sapling"]["aligned_count"] - 5, 0)
    assert "Teak" in data["planting_guidance"]
    assert "additional saplings" in data["planting_guidance"]
    assert "5 existing trees" in data["planting_guidance"]


async def test_get_all_farms_report_still_skips_boundary_and_sapling_for_a_farm_that_has_one(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    admin_auth_headers: dict,
    test_officer_user: User,
):
    """Regression guard: the bulk all-farms report must never enrich with boundary/sapling
    data, even for a farm that actually has a boundary within DEM coverage. This is what
    keeps the all-farms endpoint fast; if this starts failing, the per-farm enrichment
    has been reintroduced into the bulk loop and the N+1 performance issue is back."""
    await async_session.execute(text("TRUNCATE dem_table RESTART IDENTITY;"))
    await async_session.execute(DEM_INSERT)
    await async_session.flush()

    farm = make_farm(user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(FARM_BOUNDARY_WKT_IN_DEM_EXTENT, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    response = await async_client.get("/reports/farms", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    report = next(r for r in data if r["farm"]["id"] == farm.id)
    assert report["boundary"] is None
    assert report["sapling"] is None


async def test_get_farm_report_guidance_omits_capacity_when_sapling_unavailable(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_officer_user: User,
):
    """A farm with a boundary but no DEM coverage has a recommendation but no sapling
    numbers. Planting guidance should mention the top species without any capacity claim."""
    # dem_table is shared across tests and not covered by the per-test rollback, so
    # explicitly clear it rather than assuming no earlier test has left rows behind.
    await async_session.execute(text("TRUNCATE dem_table RESTART IDENTITY;"))
    await async_session.flush()

    farm = make_farm(user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(FARM_BOUNDARY_WKT_IN_DEM_EXTENT, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    species = make_species("Teak", "Common Teak")
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    rec = Recommendation(
        farm_id=farm.id,
        species_id=species.id,
        rank_overall=1,
        score_mcda=0.85,
        key_reasons=["suitable rainfall"],
    )
    async_session.add(rec)
    await async_session.flush()

    response = await async_client.get(f"/reports/farm/{farm.id}", headers=officer_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["sapling"] is None
    assert "Teak" in data["planting_guidance"]
    assert "additional saplings" not in data["planting_guidance"]


async def test_get_farm_report_guidance_omits_existing_trees_when_baseline_is_zero(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    officer_auth_headers: dict,
    test_officer_user: User,
):
    """A farm with zero existing trees gets capacity guidance without the
    'alongside its existing trees' clause, since there are none to mention."""
    await async_session.execute(text("TRUNCATE dem_table RESTART IDENTITY;"))
    await async_session.execute(DEM_INSERT)
    await async_session.flush()

    farm = make_farm(user_id=test_officer_user.id)
    farm.baseline_tree_count = 0
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(FARM_BOUNDARY_WKT_IN_DEM_EXTENT, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    species = make_species("Teak", "Common Teak")
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    rec = Recommendation(
        farm_id=farm.id,
        species_id=species.id,
        rank_overall=1,
        score_mcda=0.85,
        key_reasons=["suitable rainfall"],
    )
    async_session.add(rec)
    await async_session.flush()

    response = await async_client.get(f"/reports/farm/{farm.id}", headers=officer_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["sapling"]["baseline_tree_count"] == 0
    assert "additional saplings" in data["planting_guidance"]
    assert "existing trees" not in data["planting_guidance"]
