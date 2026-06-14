"""Unit + integration tests for the global trial ledger (factory §4.1)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from alpha_research.backtests.runners.sector_rotation import (
    build_weights as _real_build,
)
from alpha_research.backtests.strategies.manifest import StrategyManifest
from alpha_research.pool.registry import PoolRegistry
from alpha_research.review.ledger import (
    TrialLedger,
    derive_hypothesis_id,
    manifest_spec_hash,
)
from alpha_research.review.pipeline import run_review

UNIVERSE = ["XLK", "XLF", "XLE", "XLV"]
PARAMS = {
    "mom_lookback": 60,
    "mom_skip": 10,
    "rs_lookback": 30,
    "macro_window": 20,
    "tilt_scale": 0.6,
    "max_weight": 0.5,
}


def wrapper_weights(prices, macro, params):
    """A *different entrypoint* that is economically identical to the real one.

    Used to prove the multi-impl cross-check counts as a single trial: same
    spec, different runner code, same ``manifest_hash``.
    """
    return _real_build(prices, macro, params)


def _make_manifest(strategy_id="ledger_test", entrypoint=None, **overrides):
    payload = {
        "strategy_id": strategy_id,
        "name": "Ledger Test Strategy",
        "track": "etf_rotation",
        "universe": UNIVERSE,
        "entrypoint": entrypoint
        or "alpha_research.backtests.runners.sector_rotation:build_weights",
        "params": dict(PARAMS),
        "benchmark": "SPY",
        "n_trials": 3,
        "description": "synthetic ledger test",
    }
    payload.update(overrides)
    return StrategyManifest.model_validate(payload)


def _price_loader(n=420, seed=42):
    def loader(tickers, start, end):
        rng = np.random.default_rng(seed)
        idx = pd.bdate_range("2022-01-03", periods=n)
        return pd.DataFrame(
            {t: 100.0 * np.cumprod(1 + rng.normal(0.0004, 0.011, n)) for t in tickers},
            index=idx,
        )

    return loader


def _macro_loader(series_ids, start, end, index):
    return {sid: pd.Series(0.0, index=index) for sid in series_ids}


@pytest.fixture
def ledger(test_db):
    return TrialLedger(session=test_db)


@pytest.fixture
def pool(test_db):
    return PoolRegistry(session=test_db)


@pytest.mark.unit
class TestHypothesisId:
    @pytest.mark.parametrize(
        "strategy_id,expected",
        [
            ("sector_rotation_v1", "sector_rotation"),
            ("sector_rotation_v12", "sector_rotation"),
            ("momentum", "momentum"),
            ("carry_v2_implb", "carry"),
            ("trend_impl3", "trend"),
            ("vol_carry_v1_v2", "vol_carry"),  # repeated strip
        ],
    )
    def test_strips_version_and_impl_markers(self, strategy_id, expected):
        assert derive_hypothesis_id(strategy_id) == expected


@pytest.mark.unit
class TestSpecHash:
    def test_entrypoint_excluded_so_reimplementations_match(self):
        a = _make_manifest("momentum_v1", entrypoint="pkg.a:build")
        b = _make_manifest("momentum_v1", entrypoint="pkg.b:build")
        assert manifest_spec_hash(a) == manifest_spec_hash(b)

    def test_param_change_changes_hash(self):
        a = _make_manifest("momentum_v1")
        b = _make_manifest("momentum_v1", params={**PARAMS, "mom_lookback": 90})
        assert manifest_spec_hash(a) != manifest_spec_hash(b)

    def test_different_hypothesis_namespaces_the_hash(self):
        a = _make_manifest("momentum_v1")
        b = _make_manifest("reversal_v1")  # same params, different idea
        assert manifest_spec_hash(a) != manifest_spec_hash(b)


@pytest.mark.unit
class TestTrialLedger:
    def test_floor_dominates_first_trial(self, ledger):
        plan = ledger.plan_trial("momentum", "hashA", n_trials_floor=5)
        assert plan["version"] == 1
        assert plan["is_new_spec"] is True
        assert plan["n_trials_effective"] == 5  # floor > 1 distinct spec

    def test_distinct_specs_accumulate_trials(self, ledger):
        ledger.plan_trial("momentum", "hashA", 1)
        ledger.record(
            hypothesis_id="momentum",
            strategy_id="momentum_v1",
            family="etf_rotation",
            version=1,
            manifest_hash="hashA",
            run_id="run1",
            verdict="REVISE",
            sharpe=0.4,
            psr=0.6,
            dsr=0.3,
            n_trials_declared=1,
            n_trials_effective=1,
        )
        # A second, economically different spec for the same idea = 2 trials.
        plan = ledger.plan_trial("momentum", "hashB", n_trials_floor=1)
        assert plan["version"] == 2
        assert plan["is_new_spec"] is True
        assert plan["n_trials_effective"] == 2

    def test_reruns_of_same_spec_do_not_inflate_trials(self, ledger):
        ledger.plan_trial("momentum", "hashA", 1)
        ledger.record(
            hypothesis_id="momentum",
            strategy_id="momentum_v1",
            family="etf_rotation",
            version=1,
            manifest_hash="hashA",
            run_id="run1",
            verdict="REVISE",
            sharpe=0.4,
            psr=0.6,
            dsr=0.3,
            n_trials_declared=1,
            n_trials_effective=1,
        )
        plan = ledger.plan_trial("momentum", "hashA", n_trials_floor=1)
        assert plan["version"] == 1  # same spec reuses its version
        assert plan["is_new_spec"] is False
        assert plan["prior_runs_this_version"] == 1
        assert plan["n_trials_effective"] == 1  # not inflated by a re-run

    def test_list_rows_scopes_by_hypothesis(self, ledger):
        for hyp, h in [("momentum", "hA"), ("momentum", "hB"), ("reversal", "hC")]:
            ledger.record(
                hypothesis_id=hyp,
                strategy_id=f"{hyp}_v1",
                family="etf_rotation",
                version=1,
                manifest_hash=h,
                run_id=f"run_{h}",
                verdict="REVISE",
                sharpe=0.1,
                psr=0.5,
                dsr=0.2,
                n_trials_declared=1,
                n_trials_effective=1,
            )
        assert len(ledger.list_rows(hypothesis_id="momentum")) == 2
        assert len(ledger.list_rows()) == 3


@pytest.mark.unit
class TestLedgerWiredIntoReview:
    def _kwargs(self, tmp_path, pool):
        return dict(
            output_dir=str(tmp_path),
            price_loader=_price_loader(),
            macro_loader=_macro_loader,
            pool=pool,
            tearsheet=False,
        )

    def test_review_writes_a_trial_row_and_artifact(self, tmp_path, pool, ledger):
        result = run_review(
            _make_manifest("ledger_demo_v1"),
            ledger=ledger,
            **self._kwargs(tmp_path, pool),
        )
        rows = ledger.list_rows(hypothesis_id="ledger_demo")
        assert len(rows) == 1
        assert rows.iloc[0]["run_id"] == result["run_id"]
        assert rows.iloc[0]["version"] == 1

        artifact = json.loads(
            (Path(result["artifacts"]["run_dir"]) / "trial_ledger.json").read_text()
        )
        assert artifact["hypothesis_id"] == "ledger_demo"
        assert artifact["ledger_available"] is True

    def test_multi_impl_same_spec_counts_as_one_trial(self, tmp_path, pool, ledger):
        kwargs = self._kwargs(tmp_path, pool)
        # Two independent implementations of ONE idea (different entrypoint,
        # identical economics): the cross-check, not a search.
        run_review(_make_manifest("mi_v1"), ledger=ledger, **kwargs)
        second = run_review(
            _make_manifest(
                "mi_v1", entrypoint="tests.unit.test_trial_ledger:wrapper_weights"
            ),
            ledger=ledger,
            **kwargs,
        )
        # Two ledger rows, but the same spec version and trial count == floor.
        rows = ledger.list_rows(hypothesis_id="mi")
        assert len(rows) == 2
        assert set(rows["version"]) == {1}
        assert second["battery"]["n_trials_effective"] == 3  # the manifest floor

    def test_distinct_specs_deflate_dsr_more(self, tmp_path, pool, ledger):
        kwargs = self._kwargs(tmp_path, pool)
        first = run_review(
            _make_manifest("decay_v1", n_trials=1), ledger=ledger, **kwargs
        )
        # A genuinely different spec for the same idea -> effective trials rises.
        second = run_review(
            _make_manifest(
                "decay_v2", n_trials=1, params={**PARAMS, "mom_lookback": 120}
            ),
            ledger=ledger,
            **kwargs,
        )
        assert first["battery"]["n_trials_effective"] == 1
        assert second["battery"]["n_trials_effective"] == 2
        # More trials deflate the DSR for an otherwise-comparable Sharpe.
        assert second["battery"]["dsr"] <= second["battery"]["psr"] + 1e-9
