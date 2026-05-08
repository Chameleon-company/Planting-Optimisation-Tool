from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.raw_scoring import get_raw_scores


@pytest.fixture
def mock_cfg():
    """
    Returns a minimal configuration dictionary.
    """
    return {
        "features": {
            "ph": {
                "type": "numeric",
                "short": "ph",
                "score_method": "num_range",
                "default_weight": 0.50,
            },
            "soil_texture": {
                "type": "categorical",
                "short": "soil",
                "score_method": "cat_exact",
                "default_weight": 0.50,
            },
        },
    }


@pytest.mark.asyncio
@patch("src.services.raw_scoring.calculate_suitability")
@patch("src.services.raw_scoring.SuitabilityFarm.from_db_model")
@patch("src.services.raw_scoring.get_farm_by_id", new_callable=AsyncMock)
@patch("src.services.raw_scoring.build_rules_dict")
@patch("src.services.raw_scoring.get_species_by_ids", new_callable=AsyncMock)
@patch("src.services.raw_scoring.build_species_params_dict")
@patch("src.services.raw_scoring.get_species_parameters_as_dicts", new_callable=AsyncMock)
async def test_get_raw_scores_with_target_species(
    mock_get_params,
    mock_build_params,
    mock_get_species,
    mock_build_rules,
    mock_get_farm,
    mock_from_db_model,
    mock_calculate_suitability,
    mock_cfg,
):
    """Test get_raw_scores when specific target_species_ids are provided."""
    mock_db = AsyncMock()
    farm_id_list = [1, 2]
    target_species_ids = [10, 20]

    # Mock the returned farm entities
    mock_farm_1 = MagicMock()
    mock_farm_2 = MagicMock()
    mock_get_farm.return_value = [mock_farm_1, mock_farm_2]

    # Mock the scoring calculation to return a tuple: (dummy_data, farm_scores_list)
    mock_calculate_suitability.side_effect = [
        (None, [{"farm_id": 1, "ph": 0.8, "soil_texture": 0.6}]),
        (None, [{"farm_id": 2, "ph": 0.9, "soil_texture": 0.7}]),
    ]

    result = await get_raw_scores(
        db=mock_db,
        farm_id_list=farm_id_list,
        cfg=mock_cfg,
        target_species_ids=target_species_ids,
    )

    # Ensure the correct branch was taken for fetching species
    mock_get_species.assert_called_once_with(mock_db, target_species_ids)

    # Ensure rules were built with global_weights=None
    mock_build_rules.assert_called_once_with(
        mock_get_species.return_value,
        mock_build_params.return_value,
        mock_cfg,
        global_weights=None,
    )

    # Ensure calculation happened for both farms and results were extended correctly
    assert mock_calculate_suitability.call_count == 2
    assert result == [{"farm_id": 1, "ph": 0.8, "soil_texture": 0.6}, {"farm_id": 2, "ph": 0.9, "soil_texture": 0.7}]


@pytest.mark.asyncio
@patch("src.services.raw_scoring.calculate_suitability")
@patch("src.services.raw_scoring.SuitabilityFarm.from_db_model")
@patch("src.services.raw_scoring.get_farm_by_id", new_callable=AsyncMock)
@patch("src.services.raw_scoring.build_rules_dict")
@patch("src.services.raw_scoring.get_species_by_ids", new_callable=AsyncMock)
@patch("src.services.raw_scoring.build_species_params_dict")
@patch("src.services.raw_scoring.get_species_parameters_as_dicts", new_callable=AsyncMock)
async def test_get_raw_scores_without_target_species(
    mock_get_params,
    mock_build_params,
    mock_get_species,
    mock_build_rules,
    mock_get_farm,
    mock_from_db_model,
    mock_calculate_suitability,
    mock_cfg,
):
    """Test get_raw_scores when target_species_ids is None (fetches all species)."""
    mock_db = AsyncMock()
    farm_id_list = [1]

    # We only need 1 farm to prove the loop works
    mock_get_farm.return_value = [MagicMock()]
    mock_calculate_suitability.return_value = (None, [{"farm_id": 1, "ph": 0.5, "soil_texture": 0.6}])

    result = await get_raw_scores(
        db=mock_db,
        farm_id_list=farm_id_list,
        cfg=mock_cfg,
        target_species_ids=None,  # Explicitly None
    )

    # Ensure the 'else' branch was hit: get_species_by_ids called WITHOUT target_species_ids
    mock_get_species.assert_called_once_with(mock_db)
    assert result == [{"farm_id": 1, "ph": 0.5, "soil_texture": 0.6}]


@pytest.mark.asyncio
@patch("src.services.raw_scoring.get_farm_by_id", new_callable=AsyncMock)
@patch("src.services.raw_scoring.build_rules_dict")
@patch("src.services.raw_scoring.get_species_by_ids", new_callable=AsyncMock)
@patch("src.services.raw_scoring.build_species_params_dict")
@patch("src.services.raw_scoring.get_species_parameters_as_dicts", new_callable=AsyncMock)
async def test_get_raw_scores_empty_farms_list(
    mock_get_params,
    mock_build_params,
    mock_get_species,
    mock_build_rules,
    mock_get_farm,
    mock_cfg,
):
    """Test get_raw_scores handles an empty list of returned farms gracefully."""
    mock_db = AsyncMock()

    # Simulating the database returning no farms for the given IDs
    mock_get_farm.return_value = []

    result = await get_raw_scores(
        db=mock_db,
        farm_id_list=[999],
        cfg=mock_cfg,
    )

    # The 'for f in farms:' loop should be completely bypassed, returning an empty list
    assert result == []
