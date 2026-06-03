import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = (
    REPO_ROOT / "workstation/playground/shared/notebooks/field_study_template.py"
)


def _fake_price_frame(ticker: str, start_value: float) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=90, freq="D")
    values = [start_value + idx for idx in range(len(dates))]
    return pd.DataFrame(
        {
            "date": dates,
            "ticker": [ticker] * len(dates),
            "close": values,
        }
    )


def test_field_study_template_executes_with_stubbed_helpers(monkeypatch):
    fake_data_helpers = ModuleType("playground.data_helpers")
    fake_data_helpers.calculate_volatility = (
        lambda returns, window=20, annualize=True, method="rolling": pd.Series(
            0.2, index=returns.index
        )
    )
    fake_data_helpers.get_prices = lambda ticker, **_: (
        _fake_price_frame("SPY", 100.0)
        if ticker == "SPY"
        else _fake_price_frame("TLT", 80.0)
    )
    fake_data_helpers.refresh_prices = lambda *args, **kwargs: {
        "status": "completed",
        "rows_written": 180,
    }

    fake_viz_helpers = ModuleType("playground.shared.viz_helpers")

    def _fake_plot(*args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    fake_viz_helpers.plot_distribution = _fake_plot
    fake_viz_helpers.plot_regime_overlay = _fake_plot
    fake_viz_helpers.plot_rolling_correlation = _fake_plot
    fake_viz_helpers.plot_time_series = _fake_plot

    monkeypatch.chdir(REPO_ROOT)
    monkeypatch.setitem(sys.modules, "playground.data_helpers", fake_data_helpers)
    monkeypatch.setitem(sys.modules, "playground.shared.viz_helpers", fake_viz_helpers)

    spec = importlib.util.spec_from_file_location(
        "test_field_study_template_module", TEMPLATE_PATH
    )
    module = importlib.util.module_from_spec(spec)

    assert spec is not None
    assert spec.loader is not None

    spec.loader.exec_module(module)

    assert module.PRICE_DATASET == "equities"
    assert not module.data.empty
    assert list(module.data.columns) == ["SPY", "TLT"]
