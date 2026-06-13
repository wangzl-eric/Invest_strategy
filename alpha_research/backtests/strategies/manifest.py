"""Strategy manifest: the canonical registration contract for the strategy pool.

A strategy is the pair ``(manifest.yaml, weights_fn)``:

* The **manifest** (this module) declares the spec — universe, entrypoint,
  rebalancing, cost model, data requirements, and pre-committed promotion
  rules. Manifests are git-versioned YAML files under
  ``alpha_research/research/pool/<strategy_id>/manifest.yaml``.

* The **weights function** (the manifest's ``entrypoint``) is a pure function

      weights_fn(prices, macro, params) -> pd.DataFrame

  - ``prices``: wide close-price DataFrame (DatetimeIndex x ticker columns)
    covering the manifest universe.
  - ``macro``: dict of series_id -> pd.Series (point-in-time shifted), or
    None when the manifest declares no macro requirements.
  - ``params``: the manifest ``params`` dict.

  It returns a DataFrame of **target portfolio weights** (DatetimeIndex x
  ticker columns; NaN = no position). Weights at date *t* may use only data
  with timestamp <= *t*; the review engine applies the execution-convention
  shift, so the function itself must NOT pre-shift.

The review pipeline (``alpha_research.review``) is the only supported path
from a manifest to a pool entry.
"""

from __future__ import annotations

import importlib
import re
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, field_validator

SCHEMA_VERSION = 1

_ENTRYPOINT_RE = re.compile(r"^[A-Za-z_][\w\.]*:[A-Za-z_]\w*$")
_STRATEGY_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")


class Track(str, Enum):
    """Asset-class track (EXECUTION_PLAN.md, locked decision D3)."""

    ETF_ROTATION = "etf_rotation"
    CTA_FUTURES = "cta_futures"
    FACTOR_ETF = "factor_etf"


class ExecutionConvention(str, Enum):
    """How target weights map onto realized returns.

    - ``t_close``: weights computed from data <= t are executed at the close
      of bar *t* (end-of-day trading) -> they earn the t+1 return (1-bar shift).
    - ``t+1_open`` / ``t+1_close``: executed on the next bar. With daily
      closes only, both are approximated conservatively with a 2-bar shift.
    """

    T_CLOSE = "t_close"
    T1_OPEN = "t+1_open"
    T1_CLOSE = "t+1_close"

    @property
    def shift_bars(self) -> int:
        return 1 if self is ExecutionConvention.T_CLOSE else 2


class RebalanceSpec(BaseModel):
    """Rebalancing frequency and execution convention."""

    frequency: str = "monthly"  # daily | weekly | monthly | pandas offset alias
    execution_convention: ExecutionConvention = ExecutionConvention.T_CLOSE


class CostModelSpec(BaseModel):
    """Cost model reference. ``proportional`` charges ``bps`` on turnover."""

    id: str = "proportional"  # proportional | equity_default
    bps: float = 5.0


class DataRequirement(BaseModel):
    """One data dependency of the strategy."""

    id: str  # ticker or FRED series id
    kind: str = "prices"  # prices | macro
    source: Optional[str] = None  # yfinance | fred | stooq | ... (auto if None)

    @field_validator("kind")
    @classmethod
    def _check_kind(cls, v: str) -> str:
        if v not in ("prices", "macro"):
            raise ValueError(f"kind must be 'prices' or 'macro', got '{v}'")
        return v


class PromotionRules(BaseModel):
    """Pre-committed promotion/demotion thresholds (EXECUTION_PLAN.md §6).

    Committed at registration time so promotion is mechanical, not a mood.
    ``candidate -> paper`` gates run inside the review pipeline;
    ``paper -> live`` gates are evaluated against the forward paper record.
    """

    # candidate -> paper
    min_dsr: float = 0.95  # DSR > 0 at 95% confidence
    min_psr: float = 0.90  # PSR vs SR*=0
    cost_multiplier_survival: float = 2.0  # Sharpe must stay > 0 at this multiple
    max_abs_correlation: float = 0.4  # vs any active pool strategy
    # paper -> live (evaluated outside the backtest review)
    min_paper_trading_days: int = 60
    realized_vol_tolerance: float = 0.25  # |realized - design| / design


class StrategyManifest(BaseModel):
    """The unit of registration into the strategy pool."""

    schema_version: int = SCHEMA_VERSION
    strategy_id: str
    name: str
    track: Track
    universe: List[str]
    entrypoint: str  # "package.module:function"
    params: Dict[str, Any] = Field(default_factory=dict)
    rebalance: RebalanceSpec = Field(default_factory=RebalanceSpec)
    cost_model: CostModelSpec = Field(default_factory=CostModelSpec)
    data_requirements: List[DataRequirement] = Field(default_factory=list)
    benchmark: Optional[str] = None
    naive_baseline: Optional[str] = None
    backtest_start: Optional[str] = None  # ISO date
    backtest_end: Optional[str] = None  # ISO date
    n_trials: int = 1  # declared strategy variations tried — feeds DSR honestly
    promotion_rules: PromotionRules = Field(default_factory=PromotionRules)
    proposal_path: Optional[str] = None
    author: str = ""
    created: Optional[date] = None
    description: str = ""

    @field_validator("strategy_id")
    @classmethod
    def _check_strategy_id(cls, v: str) -> str:
        if not _STRATEGY_ID_RE.match(v):
            raise ValueError(
                f"strategy_id must be a lowercase slug ([a-z0-9_]), got '{v}'"
            )
        return v

    @field_validator("entrypoint")
    @classmethod
    def _check_entrypoint(cls, v: str) -> str:
        if not _ENTRYPOINT_RE.match(v):
            raise ValueError(
                f"entrypoint must look like 'package.module:function', got '{v}'"
            )
        return v

    @field_validator("universe")
    @classmethod
    def _check_universe(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("universe must not be empty")
        if len(set(v)) != len(v):
            raise ValueError("universe contains duplicate tickers")
        return v

    @field_validator("n_trials")
    @classmethod
    def _check_n_trials(cls, v: int) -> int:
        if v < 1:
            raise ValueError("n_trials must be >= 1")
        return v

    # ------------------------------------------------------------------
    # IO + entrypoint resolution
    # ------------------------------------------------------------------

    def resolve_entrypoint(self) -> Callable:
        """Import and return the weights function declared in ``entrypoint``."""
        module_name, func_name = self.entrypoint.split(":")
        module = importlib.import_module(module_name)
        func = getattr(module, func_name, None)
        if func is None or not callable(func):
            raise ImportError(
                f"entrypoint '{self.entrypoint}' did not resolve to a callable"
            )
        return func

    def to_yaml(self) -> str:
        data = self.model_dump(mode="json")
        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_yaml())
        return path


def load_manifest(path: str | Path) -> StrategyManifest:
    """Load and validate a manifest YAML file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    raw = yaml.safe_load(path.read_text())
    if not isinstance(raw, dict):
        raise ValueError(f"Manifest {path} did not parse to a mapping")
    return StrategyManifest.model_validate(raw)


__all__ = [
    "SCHEMA_VERSION",
    "Track",
    "ExecutionConvention",
    "RebalanceSpec",
    "CostModelSpec",
    "DataRequirement",
    "PromotionRules",
    "StrategyManifest",
    "load_manifest",
]
