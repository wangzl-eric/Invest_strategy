#!/usr/bin/env python3
"""Generate notebook scaffolds for the Fixed Income Relative Value book study."""

from __future__ import annotations

from pathlib import Path
import textwrap
import nbformat as nbf


REPO_ROOT = Path("/Users/zelin/Desktop/PA Investment/Invest_strategy")
STUDY_DIR = REPO_ROOT / "workstation" / "playground" / "studies" / "2026-03-26_fixed_income_relative_value_analysis_2e"
PDF_PATH = (
    "/Users/zelin/Desktop/阅读学习/"
    "Fixed Income Relative Value Analysis + Website A Practitioner’s Guide to the Theory, Tools, and Trades 2nd.pdf"
)

KERNELSPEC = {
    "display_name": "Python 3 (ipykernel)",
    "language": "python",
    "name": "python3",
}

LANGUAGE_INFO = {
    "name": "python",
    "version": "3.10",
}


def md(text: str):
    return nbf.v4.new_markdown_cell(textwrap.dedent(text).strip() + "\n")


def code(text: str):
    return nbf.v4.new_code_cell(textwrap.dedent(text).strip() + "\n")


COMMON_IMPORTS = """
from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

REPO_ROOT = Path("/Users/zelin/Desktop/PA Investment/Invest_strategy")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from alpha_research.quant_data.api import get_data

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["figure.figsize"] = (12, 5)
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

START = "2024-02-26"
END = "2026-02-27"
BOOK_PDF = Path(r\"\"\"/Users/zelin/Desktop/阅读学习/Fixed Income Relative Value Analysis + Website A Practitioner’s Guide to the Theory, Tools, and Trades 2nd.pdf\"\"\")

print("Expected environment: conda activate ibkr-analytics && export PYTHONPATH=.")
print("Book PDF exists:", BOOK_PDF.exists())
print("Repo root:", REPO_ROOT)
"""


COMMON_HELPERS = "\n".join(
    [
        'FRED_DIR = REPO_ROOT / "data" / "market_data" / "fred"',
        'PRICES_DIR = REPO_ROOT / "data" / "market_data" / "prices"',
        "",
        'def _filter_date(frame: pd.DataFrame, start=START, end=END, date_col="date"):',
        "    out = frame.copy()",
        "    out[date_col] = pd.to_datetime(out[date_col])",
        "    return out[(out[date_col] >= start) & (out[date_col] <= end)]",
        "",
        "def load_fred_series(series_ids, start=START, end=END):",
        "    frames = []",
        '    for parquet_file in sorted(FRED_DIR.glob("*.parquet")):',
        "        df = pd.read_parquet(parquet_file)",
        '        if "series_id" not in df.columns:',
        "            continue",
        '        sub = df[df["series_id"].isin(series_ids)]',
        "        if not sub.empty:",
        "            frames.append(_filter_date(sub, start=start, end=end))",
        "",
        "    if not frames:",
        "        return pd.DataFrame()",
        "",
        '    joined = pd.concat(frames, ignore_index=True).drop_duplicates(["date", "series_id"])',
        "    wide = (",
        '        joined.pivot(index="date", columns="series_id", values="value")',
        "        .sort_index()",
        '        .apply(pd.to_numeric, errors="coerce")',
        "    )",
        '    wide.index = pd.to_datetime(wide.index)',
        "    return wide",
        "",
        'def load_local_price_series(tickers, start=START, end=END, value_col="close"):',
        "    frames = []",
        '    for parquet_file in sorted(PRICES_DIR.glob("*.parquet")):',
        "        df = pd.read_parquet(parquet_file)",
        '        if "ticker" not in df.columns or value_col not in df.columns:',
        "            continue",
        '        sub = df[df["ticker"].isin(tickers)]',
        "        if not sub.empty:",
        "            frames.append(_filter_date(sub, start=start, end=end))",
        "",
        "    if not frames:",
        "        return pd.DataFrame()",
        "",
        '    joined = pd.concat(frames, ignore_index=True).drop_duplicates(["date", "ticker"])',
        "    wide = (",
        '        joined.pivot(index="date", columns="ticker", values=value_col)',
        "        .sort_index()",
        '        .apply(pd.to_numeric, errors="coerce")',
        "    )",
        '    wide.index = pd.to_datetime(wide.index)',
        "    return wide",
    ]
)


NOTEBOOKS = {
    "01_mean_reversion.ipynb": [
        md(
            """
            # 01 Mean Reversion

            **Book:** *Fixed Income Relative Value Analysis (2nd ed.)*  
            **Focus:** Chapter 2 mean reversion scaffold with a practical local proxy for the book's USD swap butterfly examples.

            This notebook uses the locally available Treasury `2s5s10s` butterfly (`2 * DGS5 - DGS2 - DGS10`) as a stand-in for a USD swaps butterfly until direct swap-curve data is added to the lake.
            """
        ),
        md(
            """
            ## Goals

            1. Load a real fixed-income spread proxy from local data.
            2. Build a reusable Ornstein-Uhlenbeck fitting workflow.
            3. Scaffold diagnostics, conditional expectation, and simple trade-rule placeholders.
            4. Record what should be swapped out once USD swap data becomes available.
            """
        ),
        code(COMMON_IMPORTS),
        code(COMMON_HELPERS),
        code(
            """
            curve = load_fred_series(["DGS2", "DGS5", "DGS10", "SOFR"])
            curve["UST_2s5s10s_bfly"] = 2 * curve["DGS5"] - curve["DGS2"] - curve["DGS10"]

            spread = curve[["DGS2", "DGS5", "DGS10", "SOFR", "UST_2s5s10s_bfly"]].dropna().copy()
            spread.tail()
            """
        ),
        md(
            """
            ## Plot the proxy spread

            The book's examples often use swap-curve structures. Here we start with the Treasury proxy to validate the notebook plumbing and OU workflow.
            """
        ),
        code(
            """
            ax = spread["UST_2s5s10s_bfly"].plot(title="Treasury 2s5s10s Butterfly Proxy")
            ax.set_ylabel("yield spread (bp-equivalent units in percent)")
            plt.show()
            """
        ),
        md(
            """
            ## Simple OU fit scaffold

            We fit the discrete-time approximation:

            \\[
            X_{t+1} = a + b X_t + \\varepsilon_t
            \\]

            and recover continuous-time OU parameters:

            - mean-reversion speed `theta`
            - long-run mean `mu`
            - innovation volatility proxy `sigma`
            """
        ),
        code(
            """
            def fit_ou(series: pd.Series, dt: float = 1.0):
                x = series.dropna().astype(float)
                x_t = x.iloc[:-1].to_numpy()
                x_tp1 = x.iloc[1:].to_numpy()
                X = np.column_stack([np.ones_like(x_t), x_t])
                beta, *_ = np.linalg.lstsq(X, x_tp1, rcond=None)
                a, b = beta

                b_clipped = np.clip(b, 1e-6, 0.999999)
                theta = -np.log(b_clipped) / dt
                mu = a / max(1 - b, 1e-8)

                fitted = a + b * x_t
                resid = x_tp1 - fitted
                sigma_e = resid.std(ddof=1)
                sigma = sigma_e * np.sqrt(2 * theta / max(1 - b**2, 1e-8))

                half_life = np.log(2) / max(theta, 1e-8)
                zscore = (x - x.mean()) / x.std(ddof=1)

                return {
                    "a": a,
                    "b": b,
                    "theta": theta,
                    "mu": mu,
                    "sigma_e": sigma_e,
                    "sigma": sigma,
                    "half_life": half_life,
                    "residuals": pd.Series(resid, index=x.index[1:]),
                    "zscore": zscore,
                }


            ou = fit_ou(spread["UST_2s5s10s_bfly"])
            pd.Series({k: v for k, v in ou.items() if not isinstance(v, pd.Series)})
            """
        ),
        md(
            """
            ## Diagnostics placeholders

            Use this section to add:

            - drift diagnostics from the book
            - diffusion diagnostics
            - conditional density approximations
            - first-passage-time approximations
            - execution threshold optimization
            """
        ),
        code(
            """
            spread["zscore"] = ou["zscore"]
            spread[["UST_2s5s10s_bfly", "zscore"]].tail()

            ax = spread["zscore"].plot(title="Butterfly Z-Score")
            ax.axhline(2.0, color="red", linestyle="--", alpha=0.7)
            ax.axhline(-2.0, color="red", linestyle="--", alpha=0.7)
            ax.axhline(0.0, color="black", linewidth=1.0)
            plt.show()
            """
        ),
        code(
            """
            # TODO: add a richer drift/diffusion diagnostic panel analogous to the book's Chapter 2 figures.
            # Example ideas:
            # 1. local linear or kernel estimate of drift(x)
            # 2. diffusion estimate by state bucket
            # 3. conditional expected return over holding horizons
            # 4. first-passage-time Monte Carlo or approximation
            """
        ),
        md(
            """
            ## Data gap note

            Replace the Treasury proxy with real USD swap tenors once swap-curve data is ingested.
            Suggested future inputs:

            - USD swap 2Y / 5Y / 10Y par rates
            - daily carry and roll-down estimates
            - transaction-cost assumptions for swap structures
            """
        ),
    ],
    "02_pca_yield_curve.ipynb": [
        md(
            """
            # 02 PCA Yield Curve

            **Book:** *Fixed Income Relative Value Analysis (2nd ed.)*  
            **Focus:** Chapter 3 principal component analysis for curve decomposition, residual screening, and PCA-neutral trade structures.
            """
        ),
        md(
            """
            ## Goals

            1. Load the local Treasury curve.
            2. Compute a PCA on level data or changes.
            3. Interpret factors as level / slope / curvature placeholders.
            4. Scaffold PCA-neutral residual and butterfly trade analysis.
            """
        ),
        code(COMMON_IMPORTS),
        code(COMMON_HELPERS),
        code(
            """
            tenors = ["DGS1", "DGS2", "DGS3", "DGS5", "DGS7", "DGS10", "DGS20", "DGS30"]
            curve = load_fred_series(tenors).dropna()
            curve.tail()
            """
        ),
        code(
            """
            curve.plot(title="Treasury Yield Curve Inputs")
            plt.ylabel("yield (%)")
            plt.show()
            """
        ),
        md("## PCA helper"),
        code(
            """
            def fit_pca(frame: pd.DataFrame, n_components: int = 3, use_changes: bool = True):
                x = frame.diff().dropna() if use_changes else frame.dropna()
                x = x.astype(float)
                x_centered = x - x.mean()
                cov = np.cov(x_centered.to_numpy(), rowvar=False)
                eigvals, eigvecs = np.linalg.eigh(cov)
                order = np.argsort(eigvals)[::-1]
                eigvals = eigvals[order]
                eigvecs = eigvecs[:, order]
                factors = x_centered.to_numpy() @ eigvecs[:, :n_components]

                return {
                    "input": x,
                    "cov": pd.DataFrame(cov, index=x.columns, columns=x.columns),
                    "eigenvalues": pd.Series(eigvals, index=[f"PC{i+1}" for i in range(len(eigvals))]),
                    "eigenvectors": pd.DataFrame(
                        eigvecs[:, :n_components],
                        index=x.columns,
                        columns=[f"PC{i+1}" for i in range(n_components)],
                    ),
                    "factors": pd.DataFrame(
                        factors,
                        index=x.index,
                        columns=[f"PC{i+1}" for i in range(n_components)],
                    ),
                }


            pca = fit_pca(curve, n_components=3, use_changes=True)
            pca["eigenvalues"].head(5)
            """
        ),
        code(
            """
            pca["eigenvectors"].plot(kind="bar", title="First Three PCA Eigenvectors")
            plt.ylabel("loading")
            plt.show()
            """
        ),
        md(
            """
            ## Residual construction scaffold

            Use this section to:

            - reconstruct yields from the first 1-3 factors
            - compute residuals for maturity buckets
            - build PCA-neutral butterflies or steepeners
            - compare actual spread moves with OU-style expectations from Notebook 01
            """
        ),
        code(
            """
            factors = pca["factors"]
            factors.tail()
            """
        ),
        code(
            """
            # TODO: choose a target structure, e.g. 2Y-5Y-7Y or 2Y-5Y-10Y butterfly.
            # TODO: solve for PCA-neutral weights using the first N eigenvectors.
            # TODO: compute residual history and screen for extreme dislocations.
            """
        ),
        md(
            """
            ## Stability checks

            The book emphasizes instability of eigenvectors over time. Add rolling-window PCA here and compare:

            - eigenvalue stability
            - eigenvector sign/shape stability
            - factor correlation across subperiods
            """
        ),
    ],
    "03_fitted_curves.ipynb": [
        md(
            """
            # 03 Fitted Curves

            **Book:** *Fixed Income Relative Value Analysis (2nd ed.)*  
            **Focus:** Chapter 8 fitted bond curves and their role in identifying relative-value dislocations.
            """
        ),
        md(
            """
            ## Goals

            1. Load a Treasury curve snapshot or panel.
            2. Define discount/yield curve parameterizations.
            3. Scaffold a fit procedure and residual analysis.
            4. Leave explicit TODOs for moving from Treasury proxies to cash-bond inputs.
            """
        ),
        code(COMMON_IMPORTS),
        code(COMMON_HELPERS),
        code(
            """
            tenors = {
                "1Y": "DGS1",
                "2Y": "DGS2",
                "3Y": "DGS3",
                "5Y": "DGS5",
                "7Y": "DGS7",
                "10Y": "DGS10",
                "20Y": "DGS20",
                "30Y": "DGS30",
            }
            curve = load_fred_series(list(tenors.values())).dropna()
            latest = curve.iloc[-1].rename(index={v: k for k, v in tenors.items()})
            latest
            """
        ),
        code(
            """
            maturity_years = np.array([1, 2, 3, 5, 7, 10, 20, 30], dtype=float)
            observed_yields = latest.to_numpy(dtype=float)


            def nelson_siegel_yield(t, beta0, beta1, beta2, tau):
                t = np.asarray(t, dtype=float)
                tau = max(float(tau), 1e-6)
                x = t / tau
                term1 = (1 - np.exp(-x)) / x
                term2 = term1 - np.exp(-x)
                return beta0 + beta1 * term1 + beta2 * term2


            def curve_objective(params, t, y):
                fitted = nelson_siegel_yield(t, *params)
                return np.mean((fitted - y) ** 2)


            initial_guess = np.array([observed_yields[-1], -1.0, 1.0, 2.0], dtype=float)
            initial_guess
            """
        ),
        md(
            """
            ## Fit scaffold

            If `scipy` is available, replace the placeholder fit with `scipy.optimize.minimize` or `least_squares`.
            Otherwise, keep this notebook as a curve-parameterization and residual-analysis template.
            """
        ),
        code(
            """
            try:
                from scipy.optimize import minimize
                result = minimize(curve_objective, initial_guess, args=(maturity_years, observed_yields))
                fitted_params = result.x
                fitted_curve = nelson_siegel_yield(maturity_years, *fitted_params)
                fit_summary = {
                    "success": result.success,
                    "message": result.message,
                    "objective": result.fun,
                }
            except Exception as exc:
                fitted_params = initial_guess.copy()
                fitted_curve = nelson_siegel_yield(maturity_years, *fitted_params)
                fit_summary = {"success": False, "message": repr(exc), "objective": curve_objective(initial_guess, maturity_years, observed_yields)}

            fit_summary
            """
        ),
        code(
            """
            fitted_df = pd.DataFrame(
                {
                    "maturity_years": maturity_years,
                    "observed": observed_yields,
                    "fitted": fitted_curve,
                    "residual": observed_yields - fitted_curve,
                }
            )
            fitted_df
            """
        ),
        code(
            """
            ax = fitted_df.plot(x="maturity_years", y=["observed", "fitted"], marker="o", title="Observed vs Fitted Curve")
            ax.set_ylabel("yield (%)")
            plt.show()
            """
        ),
        code(
            """
            # TODO: extend from constant-maturity yields to actual bond instruments with:
            # - coupon schedules
            # - clean/dirty prices
            # - bond-specific cashflows
            # - weighting schemes from the book
            # - residual ranking for bond selection
            """
        ),
    ],
    "04_asset_swaps.ipynb": [
        md(
            """
            # 04 Asset Swaps

            **Book:** *Fixed Income Relative Value Analysis (2nd ed.)*  
            **Focus:** Chapter 12 asset swaps, swap-spread intuition, and pricing inputs.
            """
        ),
        md(
            """
            ## Goals

            1. Load the local risk-free and funding proxies.
            2. Scaffold the inputs needed for asset swap pricing.
            3. Record what market data is still missing for a proper implementation.
            4. Leave placeholder cells for swap-spread driver analysis.
            """
        ),
        code(COMMON_IMPORTS),
        code(COMMON_HELPERS),
        code(
            """
            base_rates = load_fred_series(["SOFR", "DFEDTARU", "DGS2", "DGS5", "DGS10", "DGS30"]).dropna()
            base_rates.tail()
            """
        ),
        code(
            """
            base_rates[["SOFR", "DFEDTARU"]].plot(title="Funding and Policy Proxies")
            plt.show()
            """
        ),
        md(
            """
            ## Minimal pricing schema scaffold

            A proper asset swap implementation needs:

            - bond clean or dirty price
            - coupon schedule and accrual conventions
            - swap curve / discount curve
            - funding spread assumptions
            - package cashflow conventions

            The local lake does not yet contain the full market data required, so this notebook provides structure and placeholders.
            """
        ),
        code(
            """
            example_bond = {
                "issuer": "UST proxy",
                "maturity_years": 5.0,
                "coupon": 0.04,
                "clean_price": np.nan,  # TODO: replace with actual bond price input
                "payment_frequency": 2,
            }

            example_swap_inputs = {
                "floating_reference": "SOFR",
                "spread_guess_bp": 0.0,
                "discount_curve_proxy": "Treasury fitted curve / swap curve placeholder",
            }

            example_bond, example_swap_inputs
            """
        ),
        code(
            """
            # TODO: implement bond cashflow schedule generation.
            # TODO: implement discount-factor curve input.
            # TODO: solve for the asset swap spread that prices the package to par.
            """
        ),
        md(
            """
            ## Spread-driver placeholders

            The book highlights several swap-spread drivers. Add diagnostics here for:

            - policy / funding regime
            - Treasury richness / cheapness
            - collateral / capital proxy variables
            - cyclicality against macro indicators and stress proxies
            """
        ),
        code(
            """
            driver_panel = load_fred_series(["SOFR", "DFEDTARU", "T10Y2Y", "T10Y3M", "T10YIE", "T5YIE"]).dropna()
            driver_panel.tail()
            """
        ),
        code(
            """
            # TODO: add proxy regressions once a usable asset swap spread time series is available.
            # Candidate future data additions:
            # - SOFR asset swap spreads by tenor
            # - government/corporate cash bond prices
            # - repo / collateral specialness
            """
        ),
    ],
    "05_cross_currency_basis.ipynb": [
        md(
            """
            # 05 Cross-Currency Basis

            **Book:** *Fixed Income Relative Value Analysis (2nd ed.)*  
            **Focus:** Chapter 15 cross-currency basis swaps, CIP-style decomposition, and FX-hedged bond intuition.
            """
        ),
        md(
            """
            ## Goals

            1. Load available FX spot and USD funding proxies.
            2. Build a notebook structure for cross-currency basis analysis.
            3. Document the missing curves and basis quotes needed for a proper implementation.
            """
        ),
        code(COMMON_IMPORTS),
        code(COMMON_HELPERS),
        code(
            """
            fx = load_local_price_series(["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCAD=X"])
            usd_rates = load_fred_series(["SOFR", "DFEDTARU", "DGS2", "DGS5", "DGS10"]).dropna()

            fx.tail(), usd_rates.tail()
            """
        ),
        code(
            """
            fx.plot(title="FX Spot Proxies")
            plt.show()
            """
        ),
        md(
            """
            ## Basis decomposition scaffold

            A practical CCBS implementation needs:

            - domestic and foreign OIS/reference-rate curves
            - FX forwards or forward points
            - day-count and reset conventions
            - actual cross-currency basis quotes

            Those are not currently present in the local lake, so use this notebook as a structured placeholder.
            """
        ),
        code(
            """
            required_inputs = pd.DataFrame(
                {
                    "category": [
                        "FX spot",
                        "FX forwards",
                        "USD reference curve",
                        "foreign reference curve",
                        "CCBS quoted basis",
                    ],
                    "available_locally": [True, False, True, False, False],
                    "notes": [
                        "EURUSD / GBPUSD / USDJPY / USDCAD in local yfinance cache",
                        "not in current lake",
                        "SOFR + Treasury proxies available",
                        "not in current lake",
                        "not in current lake",
                    ],
                }
            )
            required_inputs
            """
        ),
        code(
            """
            # Placeholder covered-interest-parity style decomposition.
            # TODO:
            # 1. ingest FX forward points
            # 2. ingest EUR / GBP / JPY OIS curves
            # 3. compare implied basis to quoted basis
            # 4. analyze issuance / investment examples from the book
            """
        ),
        md(
            """
            ## Validation path

            Once data is available, extend this notebook to:

            - reconstruct synthetic funding in foreign currency
            - compare bond yields after FX hedging
            - isolate residual basis dislocations across tenor and currency
            """
        ),
    ],
}


def build_notebook(name: str, cells):
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"]["kernelspec"] = KERNELSPEC
    nb["metadata"]["language_info"] = LANGUAGE_INFO
    out = STUDY_DIR / name
    nbf.write(nb, out)


def main():
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    for name, cells in NOTEBOOKS.items():
        build_notebook(name, cells)
    print(f"Created {len(NOTEBOOKS)} notebooks in {STUDY_DIR}")


if __name__ == "__main__":
    main()
