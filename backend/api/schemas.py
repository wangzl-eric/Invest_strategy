"""Pydantic schemas for API request/response models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AccountSummaryResponse(BaseModel):
    """Account summary response."""
    account_id: str
    timestamp: datetime
    total_cash_value: Optional[float] = None
    net_liquidation: Optional[float] = None
    buying_power: Optional[float] = None
    gross_position_value: Optional[float] = None
    available_funds: Optional[float] = None
    excess_liquidity: Optional[float] = None
    equity: Optional[float] = None


class PositionResponse(BaseModel):
    """Position response."""
    id: int
    account_id: str
    timestamp: datetime
    symbol: str
    sec_type: Optional[str] = None
    currency: Optional[str] = None
    exchange: Optional[str] = None
    quantity: float
    avg_cost: Optional[float] = None
    market_price: Optional[float] = None
    market_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None


class PnLResponse(BaseModel):
    """PnL response."""
    id: int
    account_id: str
    date: datetime
    realized_pnl: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    total_pnl: Optional[float] = None
    net_liquidation: Optional[float] = None
    total_cash: Optional[float] = None


class PnLTimeSeriesPoint(BaseModel):
    """Cleaned PnL time series point for charts."""
    timestamp: datetime = Field(..., description="Timestamp of the snapshot")
    realized_pnl: float = Field(0.0, description="Realized PnL at this time")
    unrealized_pnl: float = Field(0.0, description="Unrealized PnL at this time")
    total_pnl: float = Field(0.0, description="Total PnL (realized + unrealized)")
    net_liquidation: Optional[float] = Field(
        None, description="Net liquidation value (equity) at this time"
    )
    total_cash: Optional[float] = Field(
        None, description="Total cash in the account at this time"
    )


class TradeResponse(BaseModel):
    """Trade response."""
    id: int
    account_id: str
    exec_id: str
    exec_time: datetime
    symbol: str
    sec_type: Optional[str] = None
    currency: Optional[str] = None
    side: str
    shares: float
    price: float
    avg_price: Optional[float] = None
    cum_qty: Optional[float] = None
    commission: Optional[float] = 0.0
    realized_pnl: Optional[float] = None
    realized_pnl_base: Optional[float] = None


class PerformanceMetricResponse(BaseModel):
    """Performance metric response."""
    id: int
    account_id: str
    date: datetime
    daily_return: Optional[float] = None
    cumulative_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: Optional[float] = None
    avg_win: Optional[float] = None
    avg_loss: Optional[float] = None
    profit_factor: Optional[float] = None


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None


# =============================================================================
# Performance Analytics Schemas
# =============================================================================

class HistogramData(BaseModel):
    """Histogram data for returns distribution."""
    bins: List[float] = Field(default_factory=list, description="Bin center values")
    counts: List[int] = Field(default_factory=list, description="Count per bin")


class DistributionStatistics(BaseModel):
    """Statistical measures for returns distribution."""
    mean: float = Field(0.0, description="Mean daily return")
    std: float = Field(0.0, description="Standard deviation of returns")
    skewness: float = Field(0.0, description="Skewness of returns")
    kurtosis: float = Field(0.0, description="Kurtosis of returns")
    var_95: float = Field(0.0, description="Value at Risk (95% confidence)")
    cvar_95: float = Field(0.0, description="Conditional VaR / Expected Shortfall (95%)")
    min: float = Field(0.0, description="Minimum return")
    max: float = Field(0.0, description="Maximum return")
    positive_days: int = Field(0, description="Number of positive return days")
    negative_days: int = Field(0, description="Number of negative return days")
    total_days: int = Field(0, description="Total number of days")


class ReturnsDistributionResponse(BaseModel):
    """Returns distribution data for histogram and statistics."""
    histogram: HistogramData
    statistics: DistributionStatistics
    percentiles: Dict[str, float] = Field(default_factory=dict)


class RollingMetricsResponse(BaseModel):
    """Rolling performance metrics time series."""
    dates: List[str] = Field(default_factory=list)
    rolling_sharpe: List[float] = Field(default_factory=list)
    rolling_volatility: List[float] = Field(default_factory=list)
    rolling_return: List[float] = Field(default_factory=list)


class BenchmarkTimeSeriesData(BaseModel):
    """Time series data for benchmark comparison chart."""
    dates: List[str] = Field(default_factory=list)
    portfolio_cumulative: List[float] = Field(default_factory=list)
    benchmark_cumulative: List[float] = Field(default_factory=list)


class BenchmarkComparisonResponse(BaseModel):
    """Benchmark comparison metrics and time series."""
    portfolio_sharpe: Optional[float] = None
    benchmark_sharpe: Optional[float] = None
    beta: Optional[float] = Field(None, description="Portfolio beta vs benchmark")
    alpha: Optional[float] = Field(None, description="Annualized alpha")
    information_ratio: Optional[float] = None
    tracking_error: Optional[float] = None
    correlation: Optional[float] = None
    data_points: int = 0
    portfolio_cumulative_return: Optional[float] = None
    benchmark_cumulative_return: Optional[float] = None
    time_series: Optional[BenchmarkTimeSeriesData] = None
    error: Optional[str] = None


class SP500DataPoint(BaseModel):
    """Single data point for S&P 500 time series."""
    date: str
    close: float
    daily_return: Optional[float] = None
    cumulative_return: Optional[float] = None


class SP500DataResponse(BaseModel):
    """S&P 500 benchmark data response."""
    symbol: str = "^GSPC"
    name: str = "S&P 500"
    data: List[SP500DataPoint] = Field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_return: Optional[float] = None
    annualized_return: Optional[float] = None


class PerformanceAnalyticsResponse(BaseModel):
    """Comprehensive performance analytics response."""
    account_id: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    data_points: int = 0
    
    # Summary metrics
    total_return: Optional[float] = Field(None, description="Total cumulative return")
    annualized_return: Optional[float] = Field(None, description="Annualized return")
    volatility: Optional[float] = Field(None, description="Annualized volatility")
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    calmar_ratio: Optional[float] = Field(None, description="Return / Max Drawdown")
    
    # Time series data
    returns_series: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Daily returns time series"
    )
    equity_series: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Equity/NAV time series"
    )
    
    # Distribution
    distribution: Optional[ReturnsDistributionResponse] = None
    
    # Rolling metrics
    rolling_metrics: Optional[RollingMetricsResponse] = None
    
    # Benchmark comparison
    benchmark_comparison: Optional[BenchmarkComparisonResponse] = None


# =============================================================================
# Advanced Analytics Schemas
# =============================================================================

class OptimizationWeightsResponse(BaseModel):
    """Portfolio optimization weights response."""
    asset: str
    weight: float


class OptimizationResponse(BaseModel):
    """Portfolio optimization result."""
    method: str
    weights: List[OptimizationWeightsResponse]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    constraints_satisfied: bool
    optimization_status: str


class FactorLoadingResponse(BaseModel):
    """Factor loading for an asset."""
    asset: str
    factor: str
    loading: float


class FactorAnalysisResponse(BaseModel):
    """Factor analysis result."""
    factor_loadings: List[FactorLoadingResponse]
    factor_returns: Dict[str, float]
    r_squared: Dict[str, float]
    factor_names: List[str]


class StyleAnalysisResponse(BaseModel):
    """Style analysis result."""
    style_weights: Dict[str, float]
    r_squared: float
    tracking_error: float


class AttributionResponse(BaseModel):
    """Performance attribution result."""
    total_attribution: float
    factor_attribution: Optional[Dict[str, float]] = None
    sector_attribution: Optional[Dict[str, float]] = None
    region_attribution: Optional[Dict[str, float]] = None
    security_attribution: Optional[Dict[str, float]] = None


class MonteCarloPercentilesResponse(BaseModel):
    """Monte Carlo simulation percentiles."""
    p5: float
    p25: float
    p50: float
    p75: float
    p95: float


class MonteCarloResponse(BaseModel):
    """Monte Carlo simulation result."""
    initial_value: float
    expected_final_value: float
    percentiles: MonteCarloPercentilesResponse
    probability_of_loss: float
    var_95: float
    cvar_95: float
    n_simulations: int
    n_periods: int


# =============================================================================
# Alert Schemas
# =============================================================================

class AlertRuleCreate(BaseModel):
    """Request schema for creating an alert rule."""
    account_id: str
    name: str
    description: Optional[str] = None
    rule_type: str = Field(..., description="PNL_THRESHOLD, DAILY_LOSS_LIMIT, POSITION_SIZE, DRAWDOWN, VOLATILITY, CORRELATION")
    rule_config: Dict[str, Any] = Field(..., description="Rule configuration as JSON object")
    severity: str = Field("WARN", description="INFO, WARN, ERROR, CRITICAL")
    channel_ids: List[int] = Field(default_factory=list, description="List of channel IDs")
    cooldown_minutes: int = Field(60, description="Cooldown period in minutes")
    escalation_enabled: bool = False
    escalation_after_minutes: int = 30
    escalation_channel_ids: List[int] = Field(default_factory=list)


class AlertRuleUpdate(BaseModel):
    """Request schema for updating an alert rule."""
    name: Optional[str] = None
    description: Optional[str] = None
    rule_config: Optional[Dict[str, Any]] = None
    severity: Optional[str] = None
    channel_ids: Optional[List[int]] = None
    enabled: Optional[bool] = None
    cooldown_minutes: Optional[int] = None
    escalation_enabled: Optional[bool] = None
    escalation_after_minutes: Optional[int] = None
    escalation_channel_ids: Optional[List[int]] = None


class AlertRuleResponse(BaseModel):
    """Response schema for alert rule."""
    id: int
    account_id: str
    name: str
    description: Optional[str] = None
    rule_type: str
    rule_config: Dict[str, Any]
    enabled: bool
    severity: str
    channel_ids: str
    cooldown_minutes: int
    escalation_enabled: bool
    escalation_after_minutes: int
    escalation_channel_ids: str
    created_at: datetime
    updated_at: datetime


class AlertResponse(BaseModel):
    """Response schema for alert."""
    id: int
    rule_id: int
    account_id: str
    severity: str
    message: str
    context: Dict[str, Any]
    status: str
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    notifications_sent: bool
    notification_attempts: int
    last_notification_at: Optional[datetime] = None
    escalated: bool
    escalated_at: Optional[datetime] = None
    created_at: datetime


class AlertHistoryResponse(BaseModel):
    """Response schema for alert history."""
    id: int
    alert_id: int
    rule_id: int
    account_id: str
    event_type: str
    message: Optional[str] = None
    context: Dict[str, Any]
    created_at: datetime


class AlertChannelCreate(BaseModel):
    """Request schema for creating an alert channel."""
    account_id: str
    name: str
    channel_type: str = Field(..., description="EMAIL, SMS, PUSH, SLACK, TEAMS, WEBHOOK")
    config: Dict[str, Any] = Field(..., description="Channel configuration as JSON object")
    enabled: bool = True


class AlertChannelUpdate(BaseModel):
    """Request schema for updating an alert channel."""
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class AlertChannelResponse(BaseModel):
    """Response schema for alert channel."""
    id: int
    account_id: str
    name: str
    channel_type: str
    config: Dict[str, Any]
    enabled: bool
    created_at: datetime
    updated_at: datetime

