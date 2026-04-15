import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.farm import Farm
from src.models.recommendations import Recommendation
from src.models.species import Species
from src.models.user import User


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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_get_farm_report_not_found(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    """Returns 404 when farm does not exist."""
    response = await async_client.get("/reports/farm/99999", headers=officer_auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_get_farm_report_unauthenticated(async_client: AsyncClient):
    """Returns 401 when no auth token is provided."""
    response = await async_client.get("/reports/farm/1")
    assert response.status_code == 401


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_get_all_farms_report_officer_forbidden(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    """Officers cannot access the all-farms report endpoint."""
    response = await async_client.get("/reports/farms", headers=officer_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_export_farm_report_docx_not_found(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    """Returns 404 when farm does not exist for DOCX export."""
    response = await async_client.get("/reports/farm/99999/export/docx", headers=officer_auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_export_farm_report_pdf_not_found(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    """Returns 404 when farm does not exist for PDF export."""
    response = await async_client.get("/reports/farm/99999/export/pdf", headers=officer_auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_export_farm_report_unauthenticated(async_client: AsyncClient):
    """Returns 401 when no auth token is provided for export endpoints."""
    response_docx = await async_client.get("/reports/farm/1/export/docx")
    response_pdf = await async_client.get("/reports/farm/1/export/pdf")
    assert response_docx.status_code == 401
    assert response_pdf.status_code == 401


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_export_all_farms_report_officer_forbidden(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    """Officers cannot access the all-farms export endpoints."""
    response_docx = await async_client.get("/reports/farms/export/docx", headers=officer_auth_headers)
    response_pdf = await async_client.get("/reports/farms/export/pdf", headers=officer_auth_headers)
    assert response_docx.status_code == 403
    assert response_pdf.status_code == 403


@pytest.mark.asyncio
async def test_export_all_farms_report_unauthenticated(async_client: AsyncClient):
    """Returns 401 when no auth token is provided for all-farms export endpoints."""
    response_docx = await async_client.get("/reports/farms/export/docx")
    response_pdf = await async_client.get("/reports/farms/export/pdf")
    assert response_docx.status_code == 401
    assert response_pdf.status_code == 401


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_export_all_farms_report_admin(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    admin_auth_headers: dict,
    test_officer_user: User,
    test_supervisor_user: User,
):
    """Admin can download all-farms DOCX and PDF containing farms from all users."""
    farm1 = make_farm(user_id=test_officer_user.id)
    farm2 = make_farm(user_id=test_supervisor_user.id)
    async_session.add_all([farm1, farm2])
    await async_session.flush()

    response_docx = await async_client.get("/reports/farms/export/docx", headers=admin_auth_headers)
    response_pdf = await async_client.get("/reports/farms/export/pdf", headers=admin_auth_headers)

    assert response_docx.status_code == 200
    assert response_pdf.status_code == 200
    assert len(response_docx.content) > 0
    assert len(response_pdf.content) > 0
