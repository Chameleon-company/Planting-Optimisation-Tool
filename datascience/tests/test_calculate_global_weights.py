import pandas as pd
import pytest

from scripts import calculate_global_weights as cgw


def test_bootstrap_skips_zero_coefficient_model_and_continues(monkeypatch):
    calls = {"count": 0}

    def fake_fit_elastic_net_weights(df, config):
        calls["count"] += 1

        if calls["count"] == 1:
            raise ValueError("Elastic Net importance sum is zero. Coefficients are all null.")

        return pd.Series(
            [0.6, 0.4],
            index=config.env_cols,
            name="elastic_net_weight",
        )

    monkeypatch.setattr(
        cgw,
        "fit_elastic_net_weights",
        fake_fit_elastic_net_weights,
    )

    df = pd.DataFrame({"farm_id": [1, 1, 2, 2]})
    config = cgw.MCDAConfig(env_cols=["env_1", "env_2"])

    boot, early_stop, _ = cgw.bootstrap_global_weights_early_stop(
        df,
        config,
        method="elastic_net",
        max_boot=2,
    )

    assert calls["count"] == 2
    assert len(boot) == 1
    assert early_stop is False


def test_bootstrap_raises_when_all_models_have_zero_coefficients(monkeypatch):
    def fake_fit_elastic_net_weights(df, config):
        raise ValueError("Elastic Net importance sum is zero. Coefficients are all null.")

    monkeypatch.setattr(
        cgw,
        "fit_elastic_net_weights",
        fake_fit_elastic_net_weights,
    )

    df = pd.DataFrame({"farm_id": [1, 1, 2, 2]})
    config = cgw.MCDAConfig(env_cols=["env_1", "env_2"])

    with pytest.raises(
        ValueError,
        match="No valid bootstrap models were generated.",
    ):
        cgw.bootstrap_global_weights_early_stop(
            df,
            config,
            method="combined",
            max_boot=3,
        )


@pytest.mark.parametrize("method", ["elastic_net", "combined"])
def test_bootstrap_reraises_unrelated_value_errors(monkeypatch, method):
    def raise_unrelated_error(*args, **kwargs):
        raise ValueError("Unrelated model error")

    if method == "elastic_net":
        monkeypatch.setattr(
            cgw,
            "fit_elastic_net_weights",
            raise_unrelated_error,
        )
    else:
        monkeypatch.setattr(
            cgw,
            "fit_combined_weights",
            raise_unrelated_error,
        )

    df = pd.DataFrame({"farm_id": [1, 2]})
    config = cgw.MCDAConfig(env_cols=["env_1", "env_2"])

    with pytest.raises(ValueError, match="Unrelated model error"):
        cgw.bootstrap_global_weights_early_stop(
            df,
            config,
            method=method,
            max_boot=1,
        )
