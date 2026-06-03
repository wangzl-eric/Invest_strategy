from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_market_data_store_uses_repo_root_data_dir():
    from backend import market_data_store

    assert market_data_store._BASE_DIR == REPO_ROOT / "data" / "market_data"


def test_research_duckdb_uses_repo_root_data_dir():
    from backend.research import duckdb_utils

    assert duckdb_utils.DATA_DIR == REPO_ROOT / "data" / "market_data"


def test_quant_data_settings_default_to_repo_root_data_lake(monkeypatch):
    monkeypatch.delenv("DATA_LAKE_ROOT", raising=False)
    monkeypatch.delenv("QDATA_META_DB_URL", raising=False)
    monkeypatch.delenv("QDATA_DUCKDB_PATH", raising=False)

    from quant_data.qconfig import QuantDataSettings

    settings = QuantDataSettings.from_env()
    assert settings.data_lake_root == REPO_ROOT / "data_lake"
    assert settings.duckdb_path == REPO_ROOT / "data_lake" / "research.duckdb"
