import builtins
from unittest.mock import MagicMock

import numpy as np
import pytest

from ahp_cli import AhpCli


@pytest.fixture
def features():
    """Return a list of (full_name, short_name) tuples for test features."""
    # (full_name, short_name)
    return [
        ("rainfall_mm", "rainfall"),
        ("temperature_celsius", "temperature"),
        ("soil_texture", "soil"),
    ]


@pytest.fixture
def species():
    """Return a sample species record for testing."""
    return {
        "id": 1,
        "name": "Eucalyptus globulus",
        "common_name": "Blue Gum",
    }


def test_get_user_input_accepts_fraction(monkeypatch):
    """Test that get_user_input correctly parses a fraction input."""
    cli = AhpCli()

    inputs = iter(["1/3"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    val = cli.get_user_input("A", "B")
    assert pytest.approx(val) == 1 / 3


def test_get_user_input_retries_until_valid(monkeypatch):
    """Test that get_user_input retries on invalid input until a valid value is entered."""
    cli = AhpCli()

    inputs = iter(["abc", "10", "5"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    val = cli.get_user_input("A", "B")
    assert val == 5.0


def test_run_profile_saves_on_consistent(monkeypatch, features, species):
    """Test that run_profile saves results when consistency is acceptable."""
    cli = AhpCli()
    cli.features = features

    # Always return preference = 1
    monkeypatch.setattr(builtins, "input", lambda _: "1")

    # Mock AHP core result
    mock_result = {
        "weights": np.array([0.3, 0.4, 0.3]),
        "consistency_ratio": 0.05,
        "is_consistent": True,
    }
    cli.core.calculate_weights = MagicMock(return_value=mock_result)

    # Mock save_results
    cli.data.save_results = MagicMock(return_value="data/species_params.csv")

    cli.run_profile(species)

    cli.core.calculate_weights.assert_called_once()
    cli.data.save_results.assert_called_once_with(
        species["id"],
        features,
        mock_result["weights"],
    )


def test_run_profile_does_not_save_on_inconsistent(monkeypatch, features, species):
    """Test that run_profile does not save results when consistency is poor."""
    cli = AhpCli()
    cli.features = features

    monkeypatch.setattr(builtins, "input", lambda _: "1")

    mock_result = {
        "weights": np.array([0.2, 0.5, 0.3]),
        "consistency_ratio": 0.25,
        "is_consistent": False,
    }
    cli.core.calculate_weights = MagicMock(return_value=mock_result)
    cli.data.save_results = MagicMock()

    cli.run_profile(species)

    cli.data.save_results.assert_not_called()


def test_start_quit_immediately(monkeypatch):
    """Test that start method can handle immediate quit input."""
    cli = AhpCli()

    cli.data.load_config = MagicMock(
        return_value=(
            [("height", "Height")],
            [{"id": 1, "name": "Test", "common_name": "Test"}],
        )
    )

    monkeypatch.setattr(builtins, "input", lambda _: "q")

    cli.start()

    cli.data.load_config.assert_called_once()


def test_start_select_species_then_quit(monkeypatch):
    """Test that start method allows selecting a species and then quitting."""
    cli = AhpCli()

    cli.data.load_config = MagicMock(
        return_value=(
            [("height", "Height")],
            [{"id": 1, "name": "Test", "common_name": "Test"}],
        )
    )

    cli.run_profile = MagicMock()

    inputs = iter(["1", "q"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    cli.start()

    cli.run_profile.assert_called_once()
