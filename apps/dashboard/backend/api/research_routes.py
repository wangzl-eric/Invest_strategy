"""Research API endpoints for quant research workflow.

Provides endpoints for:
- SQL queries over market data (DuckDB)
- Feature computation
- Backtest execution
- Experiment tracking
- LLM verdict generation (hybrid rule-based + LLM)
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Body, HTTPException, Query

from backend.config import settings
from backend.data_pipeline import data_pipeline
from backend.llm_verdict import generate_hybrid_verdict, run_verdict
from backend.research.duckdb_utils import get_research_db
from backend.research.features import compute_features, get_feature_registry

# Get the project root and optional skill path.
project_root = Path(__file__).resolve().parents[4]
skill_path = project_root / ".cursor" / "skills" / "quant-backtest-research"
if skill_path.exists() and str(skill_path) not in sys.path:
    sys.path.insert(0, str(skill_path))

try:
    from backend.research.backtest import (
        BacktestConfig,
        run_backtest,
        run_factor_backtest,
    )
except ModuleNotFoundError as exc:
    BacktestConfig = None
    run_backtest = None
    run_factor_backtest = None
    _BACKTEST_IMPORT_ERROR = exc
else:
    _BACKTEST_IMPORT_ERROR = None

try:
    from researcher import BacktestResearcher
except ModuleNotFoundError as exc:
    BacktestResearcher = None
    _RESEARCHER_IMPORT_ERROR = exc
else:
    _RESEARCHER_IMPORT_ERROR = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["research"])


def _optional_dependency_detail(feature: str, exc: ModuleNotFoundError) -> str:
    missing_module = getattr(exc, "name", None) or str(exc)
    return (
        f"{feature} is unavailable because optional dependency "
        f"'{missing_module}' could not be imported."
    )


def _require_backtest_support() -> None:
    if _BACKTEST_IMPORT_ERROR is not None:
        raise HTTPException(
            status_code=503,
            detail=_optional_dependency_detail(
                "Research backtesting", _BACKTEST_IMPORT_ERROR
            ),
        )


def _require_researcher_support() -> None:
    if _RESEARCHER_IMPORT_ERROR is not None:
        raise HTTPException(
            status_code=503,
            detail=_optional_dependency_detail(
                "Research report analysis", _RESEARCHER_IMPORT_ERROR
            ),
        )


# ----------------------------------------------------------------------
# Data Query Endpoints
# ----------------------------------------------------------------------


@router.get("/query")
async def research_query(
    sql: str = Query(..., description="SQL query to execute"),
    limit: int = Query(1000, description="Maximum rows to return"),
):
    """Execute a raw SQL query over market data.

    This endpoint uses DuckDB to query Parquet files directly.
    Available tables:
    - ibkr_equities, ibkr_fx, ibkr_futures, ibkr_options
    - yf_equities, yf_fx, yf_commodities, yf_rates
    - fred_treasury, fred_macro, fred_liquidity

    Example queries:
    - SELECT * FROM ibkr_equities WHERE ticker = 'AAPL' LIMIT 100
    - SELECT date, close FROM ibkr_fx WHERE ticker = 'EURUSD'
    - SELECT * FROM fred_macro WHERE series_id = 'CPIAUCSL'
    """
    try:
        with get_research_db() as db:
            # Add limit to query
            query = sql.strip()
            if "LIMIT" not in query.upper():
                query = f"{query} LIMIT {limit}"

            result = db.execute(query)
            return {
                "status": "success",
                "row_count": len(result),
                "data": result.to_dict(orient="records"),
            }
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/prices")
async def get_research_prices(
    dataset: Optional[str] = Query(None, description="Canonical dataset key"),
    tickers: Optional[str] = Query(None, description="Comma-separated tickers"),
    asset_class: Optional[str] = Query(
        None, description="Asset class (equity, fx, futures, commodity)"
    ),
    source: str = Query("ibkr", description="Data source (ibkr, yf)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(1000, description="Maximum rows"),
    refresh_if_missing: bool = Query(
        False,
        description="If true, refresh from source before returning when local data is empty",
    ),
):
    """Query locally stored research prices through the unified data pipeline."""
    try:
        ticker_list = tickers.split(",") if tickers else None
        local_req = data_pipeline.build_local_request(
            dataset=dataset,
            source=source,
            asset_class=asset_class,
            identifiers=ticker_list,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            refresh_if_missing=refresh_if_missing,
        )
        df = data_pipeline.query_local(local_req)

        if limit and len(df) > limit:
            df = df.tail(limit)

        return {
            "status": "success",
            "row_count": len(df),
            "data": df.to_dict(orient="records"),
        }
    except Exception as e:
        logger.error(f"Price query failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/returns")
async def get_research_returns(
    tickers: str = Query(..., description="Comma-separated tickers"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    periods: int = Query(1, description="Return periods"),
):
    """Calculate returns for given tickers."""
    try:
        ticker_list = tickers.split(",")

        with get_research_db() as db:
            df = db.get_returns(
                tickers=ticker_list,
                start_date=start_date,
                end_date=end_date,
                periods=periods,
            )

        return {
            "status": "success",
            "row_count": len(df),
            "data": df.to_dict(orient="records"),
        }
    except Exception as e:
        logger.error(f"Returns query failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/fred")
async def get_fred_data(
    series_ids: str = Query(..., description="Comma-separated FRED series IDs"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
):
    """Query FRED economic data."""
    try:
        series_list = series_ids.split(",")

        with get_research_db() as db:
            df = db.get_fred_series(
                series_ids=series_list, start_date=start_date, end_date=end_date
            )

        return {
            "status": "success",
            "row_count": len(df),
            "data": df.to_dict(orient="records"),
        }
    except Exception as e:
        logger.error(f"FRED query failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------------------------------------------------
# Feature Endpoints
# ----------------------------------------------------------------------


@router.get("/features")
async def list_features(
    category: Optional[str] = Query(
        None, description="Filter by category (momentum, volatility, value, quality)"
    ),
):
    """List all available features in the registry."""
    try:
        registry = get_feature_registry()

        if category:
            from backend.research.features import FeatureCategory

            cat = FeatureCategory(category.lower())
            features = registry.list_features(cat)
        else:
            features = registry.list_features()

        return {
            "status": "success",
            "count": len(features),
            "features": [
                {
                    "name": f.name,
                    "category": f.category.value,
                    "description": f.description,
                    "parameters": f.parameters,
                    "required_data": f.required_data,
                }
                for f in features
            ],
        }
    except Exception as e:
        logger.error(f"Feature list failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/features/compute")
async def compute_features_endpoint(
    data: List[Dict[str, Any]],
    feature_names: List[str] = Query(
        ..., description="List of feature names to compute"
    ),
    price_col: str = Query("close", description="Price column name"),
):
    """Compute features from price data."""
    try:
        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Compute features
        result_df = compute_features(df, feature_names, price_col)

        return {
            "status": "success",
            "row_count": len(result_df),
            "data": result_df.to_dict(orient="records"),
        }
    except Exception as e:
        logger.error(f"Feature computation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------------------------------------------------
# Backtest Endpoints
# ----------------------------------------------------------------------


@router.post("/backtest")
async def run_backtest_endpoint(
    data: List[Dict[str, Any]],
    signals: List[Dict[str, Any]],
    initial_capital: float = Query(100000, description="Initial capital"),
    commission: float = Query(0.001, description="Commission per trade"),
    slippage: float = Query(0.0005, description="Slippage"),
):
    """Run a backtest with provided price data and signals.

    Request body should contain:
    - data: List of {date, close, ...} records
    - signals: List of {date, signal} records (-1, 0, 1)
    """
    try:
        _require_backtest_support()

        # Convert to DataFrames
        price_df = pd.DataFrame(data)
        if "date" in price_df.columns:
            price_df["date"] = pd.to_datetime(price_df["date"])
            price_df = price_df.set_index("date")

        signals_df = pd.DataFrame(signals)
        if "date" in signals_df.columns:
            signals_df["date"] = pd.to_datetime(signals_df["date"])
            signals_df = signals_df.set_index("date")

        # Align signals to price data
        common_idx = price_df.index.intersection(signals_df.index)
        aligned_signals = (
            signals_df.loc[common_idx, "signal"]
            if "signal" in signals_df.columns
            else signals_df.loc[common_idx, 0]
        )

        # Create config
        config = BacktestConfig(
            initial_capital=initial_capital, commission=commission, slippage=slippage
        )

        # Run backtest
        result = run_backtest(price_df, aligned_signals, config)

        return {
            "status": "success",
            "metrics": result.metrics,
            "total_trades": len(result.trades),
            "equity_curve": result.equity_curve.to_dict(orient="records")
            if not result.equity_curve.empty
            else [],
            "trades": result.trades.to_dict(orient="records")
            if not result.trades.empty
            else [],
        }
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/backtest/factor")
async def run_factor_backtest_endpoint(
    data: List[Dict[str, Any]],
    factor_name: str = Query(..., description="Factor column name"),
    direction: str = Query("long_short", description="long_short or long_only"),
    quantile: float = Query(0.2, description="Top/bottom quantile"),
    initial_capital: float = Query(100000, description="Initial capital"),
    commission: float = Query(0.001, description="Commission"),
    slippage: float = Query(0.0005, description="Slippage"),
):
    """Run a factor-based backtest.

    Ranks securities by factor and goes long top quantile, short bottom quantile.
    """
    try:
        _require_backtest_support()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")

        # Create config
        config = BacktestConfig(
            initial_capital=initial_capital, commission=commission, slippage=slippage
        )

        # Run factor backtest
        result = run_factor_backtest(
            df,
            factor_name=factor_name,
            direction=direction,
            quantile=quantile,
            config=config,
        )

        return {
            "status": "success",
            "metrics": result.metrics,
            "total_trades": len(result.trades),
            "summary": result.summary(),
        }
    except Exception as e:
        logger.error(f"Factor backtest failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/backtest/mlflow")
async def run_backtest_with_mlflow(
    data: List[Dict[str, Any]],
    signals: List[Dict[str, Any]],
    experiment_name: Optional[str] = Query(None, description="MLflow experiment name"),
    run_params: Optional[Dict[str, Any]] = Body(None, description="Parameters to log"),
    initial_capital: float = Query(100000, description="Initial capital"),
    commission: float = Query(0.001, description="Commission"),
    slippage: float = Query(0.0005, description="Slippage"),
):
    """Run backtest and log to MLflow."""
    try:
        _require_backtest_support()

        # Run backtest
        result = await run_backtest_endpoint(
            data, signals, initial_capital, commission, slippage
        )

        # Create BacktestResult from metrics
        # (simplified - in production would pass full result)

        logger.info(
            f"Backtest completed: Sharpe={result['metrics'].get('sharpe_ratio', 0):.2f}"
        )

        return {
            "status": "success",
            "message": "Backtest completed and logged to MLflow",
            "metrics": result["metrics"],
        }
    except Exception as e:
        logger.error(f"MLflow backtest failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------------------------------------------------
# Catalog / Status Endpoints
# ----------------------------------------------------------------------


@router.get("/status")
async def get_research_status():
    """Get research infrastructure status."""
    try:
        # Check DuckDB
        duckdb_ok = True
        try:
            with get_research_db() as db:
                db.execute("SELECT 1")
        except Exception as e:
            duckdb_ok = False
            logger.warning(f"DuckDB check failed: {e}")

        # Check MLflow
        mlflow_ok = settings.research.mlflow.is_enabled

        # Get feature count
        registry = get_feature_registry()
        feature_count = len(registry.list_features())

        return {
            "status": "ok" if duckdb_ok else "degraded",
            "duckdb": "ok" if duckdb_ok else "error",
            "mlflow": "enabled" if mlflow_ok else "disabled",
            "features_registered": feature_count,
            "config": {
                "data_sources": {
                    "equity": settings.data_sources.equity,
                    "fx": settings.data_sources.fx,
                    "futures": settings.data_sources.futures,
                    "commodity": settings.data_sources.commodity,
                    "rate": settings.data_sources.rate,
                }
            },
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------
# LLM Verdict Endpoints
# ----------------------------------------------------------------------


@router.post("/verdict")
async def generate_verdict_endpoint(
    returns: List[float] = Body(..., description="List of daily returns"),
    benchmarks: Optional[Dict[str, List[float]]] = Body(
        None, description="Dict of benchmark returns {ticker: [returns]}"
    ),
    hypothesis: Optional[Dict[str, str]] = Body(
        None,
        description="Hypothesis details {statement, who_loses_money, economic_mechanism, noise_discrimination}",
    ),
    n_iterations: int = Body(1, description="Number of optimization iterations"),
    avg_turnover: float = Body(0.5, description="Average portfolio turnover"),
    use_llm: bool = Body(True, description="Whether to use LLM verdict"),
    allow_loosening: bool = Body(
        False, description="Allow LLM to loosen verdict (not recommended)"
    ),
):
    """Generate hybrid verdict (rule-based + LLM) for backtest results.

    This endpoint runs the full backtest rigor analysis and optionally
    supplements it with LLM judgment.

    **Request Body:**
    - `returns`: List of daily returns (required)
    - `benchmarks`: Dict of benchmark returns, e.g. {"SPY": [...], "QQQ": [...]} (optional)
    - `hypothesis`: Hypothesis details with keys:
      - `statement`: Strategy hypothesis
      - `who_loses_money`: Who loses money in this trade
      - `economic_mechanism`: Economic mechanism
      - `noise_discrimination`: How strategy discriminates noise
    - `n_iterations`: Number of optimization iterations (for deflated Sharpe)
    - `avg_turnover`: Average portfolio turnover (for robustness tests)
    - `use_llm`: Whether to call LLM for verdict (default: True)
    - `allow_loosening`: Allow LLM to loosen verdict (default: False)

    **Response:**
    - `rule_based`: Full rule-based analysis with all metrics and verdicts
    - `llm`: LLM verdict (if use_llm=True) with reasoning, flags, suggestions
    - `final`: Final verdict after applying override policy

    **Override Policy:**
    By default, LLM can only tighten the verdict (PROCEED → PROCEED_WITH_CAUTION
    or NEEDS_WORK), never loosen. This prevents the LLM from incorrectly
    upgrading a failing strategy to pass.

    Example:
    ```json
    {
      "returns": [0.01, -0.005, 0.02, ...],
      "benchmarks": {"SPY": [0.005, -0.002, ...]},
      "hypothesis": {
        "statement": "Momentum continues after earnings beats",
        "who_loses_money": "Slow traders who react late to news",
        "economic_mechanism": "Information diffusion - early movers profit from delayed reaction"
      },
      "n_iterations": 50,
      "avg_turnover": 0.8
    }
    ```
    """
    try:
        # Extract individual hypothesis fields from dict
        hypothesis_str = None
        who_loses = None
        mechanism = None
        noise_disc = None

        if hypothesis:
            hypothesis_str = hypothesis.get("statement")
            who_loses = hypothesis.get("who_loses_money")
            mechanism = hypothesis.get("economic_mechanism")
            noise_disc = hypothesis.get("noise_discrimination")

        result = await run_verdict(
            returns=returns,
            benchmarks=benchmarks,
            hypothesis=hypothesis_str,
            who_loses_money=who_loses,
            economic_mechanism=mechanism,
            noise_discrimination=noise_disc,
            n_iterations=n_iterations,
            avg_turnover=avg_turnover,
            use_llm=use_llm,
            allow_loosening=allow_loosening,
            print_result=False,
        )

        return {
            "status": "success",
            **result,
        }
    except Exception as e:
        logger.error(f"Verdict generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verdict/from-report")
async def generate_verdict_from_report(
    report: Dict[str, Any] = Body(..., description="BacktestReport as dict"),
    use_llm: bool = Body(True, description="Whether to use LLM verdict"),
    allow_loosening: bool = Body(
        False, description="Allow LLM to loosen verdict (not recommended)"
    ),
):
    """Generate hybrid verdict from a pre-computed BacktestReport.

    Use this endpoint if you've already run the full backtest analysis
    and just want the LLM to provide additional judgment.

    **Request Body:**
    - `report`: A BacktestReport serialized to dict (from BacktestResearcher.run_full_analysis())
    - `use_llm`: Whether to call LLM for verdict
    - `allow_loosening`: Allow LLM to loosen verdict

    **Response:**
    Same as /verdict endpoint - contains rule_based, llm, and final fields.
    """
    try:
        _require_researcher_support()

        from researcher import (
            BacktestReport,
            BetaMetrics,
            Hypothesis,
            RobustnessMetrics,
            SignificanceMetrics,
            WalkForwardMetrics,
        )

        hyp = report.get("hypothesis", {})
        sig = report.get("significance", {})
        wf = report.get("walkforward", {})
        rob = report.get("robustness", {})
        beta = report.get("beta", {})

        backtest_report = BacktestReport(
            hypothesis=Hypothesis(
                statement=hyp.get("statement", ""),
                who_loses_money=hyp.get("who_loses_money", ""),
                economic_mechanism=hyp.get("economic_mechanism", ""),
                noise_discrimination=hyp.get("noise_discrimination", ""),
                is_valid=hyp.get("is_valid", True),
                warnings=hyp.get("warnings", []),
            ),
            significance=SignificanceMetrics(
                sharpe_ratio=sig.get("sharpe_ratio", 0),
                probabilistic_sharpe=sig.get("probabilistic_sharpe", 0),
                deflated_sharpe=sig.get("deflated_sharpe", 0),
                min_required_length=sig.get("min_required_length", 0),
                threshold=sig.get("threshold", 0.5),
            ),
            walkforward=WalkForwardMetrics(
                n_windows=wf.get("n_windows", 0),
                train_months=wf.get("train_months", 12),
                test_months=wf.get("test_months", 3),
                step_months=wf.get("step_months", 1),
                mean_return=wf.get("mean_return", 0),
                return_std=wf.get("return_std", 0),
                win_rate=wf.get("win_rate", 0),
                best_return=wf.get("best_return", 0),
                worst_return=wf.get("worst_return", 0),
                crisis_included=wf.get("crisis_included", False),
            ),
            robustness=RobustnessMetrics(
                base_return=rob.get("base_return", 0),
                base_sharpe=rob.get("base_sharpe", 0),
                costs_50_return=rob.get("costs_50_return", 0),
                costs_50_sharpe=rob.get("costs_50_sharpe", 0),
                costs_100_return=rob.get("costs_100_return", 0),
                costs_100_sharpe=rob.get("costs_100_sharpe", 0),
                slippage_10_return=rob.get("slippage_10_return", 0),
                slippage_10_sharpe=rob.get("slippage_10_sharpe", 0),
                slippage_25_return=rob.get("slippage_25_return", 0),
                slippage_25_sharpe=rob.get("slippage_25_sharpe", 0),
            ),
            beta=BetaMetrics(
                spy_correlation=beta.get("spy_correlation", 0),
                qqq_correlation=beta.get("qqq_correlation", 0),
            ),
            n_iterations=report.get("n_iterations", 1),
            optimization_landscape=report.get("optimization_landscape", "FLAT"),
        )

        result = await generate_hybrid_verdict(
            report=backtest_report,
            use_llm=use_llm,
            allow_loosening=allow_loosening,
        )

        return {
            "status": "success",
            **result,
        }
    except Exception as e:
        logger.error(f"Verdict from report failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
