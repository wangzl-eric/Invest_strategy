"""Configuration management for the application."""
import os
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from pydantic_settings import BaseSettings
from pydantic import Field
import yaml

# Load .env file if it exists (for environment variables like FLEX_TOKEN)
try:
    from dotenv import load_dotenv
    # Load .env from project root (parent of backend directory)
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip
    pass


class IBKRConfig(BaseSettings):
    """IBKR API configuration."""
    host: str = Field(default="127.0.0.1", description="IBKR TWS/Gateway host")
    port: int = Field(default=7497, description="IBKR TWS/Gateway port (7497 for paper, 7496 for live)")
    client_id: int = Field(default=1, description="Client ID for IBKR connection")
    timeout: int = Field(default=30, description="Connection timeout in seconds")

    class Config:
        env_prefix = "IBKR_"


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    url: str = Field(
        default="sqlite:///./ibkr_analytics.db",
        description="Database connection URL"
    )
    echo: bool = Field(default=False, description="Echo SQL queries")

    class Config:
        env_prefix = "DB_"


class AppConfig(BaseSettings):
    """Application configuration."""
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    update_interval_minutes: int = Field(default=15, description="Data update interval in minutes")

    class Config:
        env_prefix = "APP_"


@dataclass
class FlexQueryDefinition:
    """Definition of a single Flex Query report."""
    id: str
    name: str
    type: str
    description: str = ""


class FlexQueryConfig(BaseSettings):
    """IBKR Flex Query Web Service configuration."""
    token: str = Field(default="", description="Flex Web Service token")
    queries: List[dict] = Field(default_factory=list, description="List of Flex Query definitions")

    # Legacy fields for backwards compatibility
    trade_query_id: str = Field(default="", description="Query ID for trade history (deprecated)")
    position_query_id: str = Field(default="", description="Query ID for positions (deprecated)")
    activity_query_id: str = Field(default="", description="Combined activity query ID (deprecated)")

    class Config:
        env_prefix = "FLEX_"

    @property
    def is_configured(self) -> bool:
        """Check if Flex Query is properly configured."""
        return bool(self.token and (self.queries or self.trade_query_id or self.activity_query_id))

    def get_all_queries(self) -> List[FlexQueryDefinition]:
        """Get all configured Flex Queries as FlexQueryDefinition objects."""
        result = []

        # New format: queries list
        for q in self.queries:
            result.append(FlexQueryDefinition(
                id=q.get('id', ''),
                name=q.get('name', f"Query {q.get('id', 'Unknown')}"),
                type=q.get('type', 'activity'),
                description=q.get('description', '')
            ))

        # Legacy format fallback (if no queries defined)
        if not result:
            if self.activity_query_id:
                result.append(FlexQueryDefinition(
                    id=self.activity_query_id,
                    name="Activity Statement",
                    type="activity"
                ))
            if self.trade_query_id and self.trade_query_id != self.activity_query_id:
                result.append(FlexQueryDefinition(
                    id=self.trade_query_id,
                    name="Trade History",
                    type="trades"
                ))
            if self.position_query_id and self.position_query_id not in [self.activity_query_id, self.trade_query_id]:
                result.append(FlexQueryDefinition(
                    id=self.position_query_id,
                    name="Positions",
                    type="positions"
                ))

        return result


class MarketDataConfig(BaseSettings):
    """Market data configuration."""
    fred_api_key: str = Field(default="", description="FRED API key for economic data")

    class Config:
        env_prefix = ""
        env_mapping = {"fred_api_key": "FRED_API_KEY"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.fred_api_key:
            self.fred_api_key = os.getenv("FRED_API_KEY", "")


class DataSourceConfig(BaseSettings):
    """Data source prioritization configuration."""
    equity: str = Field(default="ibkr", description="Primary source for equities")
    fx: str = Field(default="ibkr", description="Primary source for FX")
    futures: str = Field(default="ibkr", description="Primary source for futures")
    commodity: str = Field(default="ibkr", description="Primary source for commodities")
    rate: str = Field(default="fred", description="Primary source for rates")

    class Config:
        env_prefix = "DATA_SOURCE_"


class DataSourceFallback(BaseSettings):
    """Fallback data sources when primary is unavailable."""
    equity: str = Field(default="yfinance")
    fx: str = Field(default="yfinance")
    futures: str = Field(default="yfinance")
    commodity: str = Field(default="yfinance")
    rate: str = Field(default="yfinance")


class DuckDBConfig(BaseSettings):
    """DuckDB research configuration."""
    read_parquet_direct: bool = Field(default=True, description="Read Parquet directly without copying")
    memory_limit: int = Field(default=4096, description="Memory limit in MB")

    class Config:
        env_prefix = "DUCKDB_"


class MLflowConfig(BaseSettings):
    """MLflow experiment tracking configuration."""
    tracking_uri: str = Field(default="http://localhost:5000", description="MLflow tracking server URI")
    experiment_name: str = Field(default="quant_research", description="Default experiment name")
    disabled: str = Field(default="", description="Set to any value to disable MLflow")

    class Config:
        env_prefix = "MLFLOW_"

    @property
    def is_enabled(self) -> bool:
        return not self.disabled


class FeatureConfig(BaseSettings):
    """Feature registry configuration."""
    momentum_periods: List[int] = Field(default_factory=lambda: [20, 60, 120, 252])
    volatility_periods: List[int] = Field(default_factory=lambda: [20, 60, 252])
    correlation_periods: List[int] = Field(default_factory=lambda: [60, 120, 252])

    class Config:
        env_prefix = "FEATURE_"


class BacktestConfig(BaseSettings):
    """Backtest default configuration."""
    default_initial_capital: float = Field(default=100000)
    default_commission: float = Field(default=0.001)  # 0.1%
    default_slippage: float = Field(default=0.0005)  # 0.05%

    class Config:
        env_prefix = "BACKTEST_"


class ResearchConfig(BaseSettings):
    """Research layer configuration."""
    duckdb: DuckDBConfig = Field(default_factory=DuckDBConfig)
    mlflow: MLflowConfig = Field(default_factory=MLflowConfig)
    features: FeatureConfig = Field(default_factory=FeatureConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)

    class Config:
        env_prefix = "RESEARCH_"


class Settings:
    """Application settings."""
    def __init__(self):
        self.ibkr = IBKRConfig()
        self.database = DatabaseConfig()
        self.app = AppConfig()
        self.flex_query = FlexQueryConfig()
        self.market_data = MarketDataConfig()
        self.data_sources = DataSourceConfig()
        self.research = ResearchConfig()

    @classmethod
    def load_from_yaml(cls, config_path: Optional[Path] = None) -> "Settings":
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "app_config.yaml"

        settings = cls()

        if config_path.exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}

            if 'ibkr' in config_data:
                settings.ibkr = IBKRConfig(**config_data['ibkr'])
            if 'database' in config_data:
                settings.database = DatabaseConfig(**config_data['database'])
            if 'app' in config_data:
                settings.app = AppConfig(**config_data['app'])
            if 'flex_query' in config_data:
                # SECURITY:
                # Never load secrets (Flex token) from YAML. Secrets should come from env:
                #   FLEX_TOKEN=...
                flex_cfg = dict(config_data.get("flex_query") or {})
                flex_cfg.pop("token", None)
                settings.flex_query = FlexQueryConfig(**flex_cfg)

            # Load data source configuration
            if 'data_sources' in config_data:
                ds_cfg = config_data['data_sources']
                settings.data_sources = DataSourceConfig(**ds_cfg.get('primary', {}))
                if 'fallback' in ds_cfg:
                    settings.data_sources_fallback = DataSourceFallback(**ds_cfg['fallback'])

            # Load research configuration
            if 'research' in config_data:
                rcfg = config_data['research']
                if 'duckdb' in rcfg:
                    settings.research.duckdb = DuckDBConfig(**rcfg['duckdb'])
                if 'mlflow' in rcfg:
                    settings.research.mlflow = MLflowConfig(**rcfg['mlflow'])
                if 'features' in rcfg:
                    settings.research.features = FeatureConfig(**rcfg['features'])
                if 'backtest' in rcfg:
                    settings.research.backtest = BacktestConfig(**rcfg['backtest'])

        return settings


# Global settings instance
settings = Settings.load_from_yaml()
