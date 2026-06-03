# Portfolio Field

**Focus:** Portfolio construction, optimization, and rebalancing strategies

## Key Questions

- How to build optimal portfolios?
- What's the right balance between risk and return?
- How often to rebalance?
- How to incorporate constraints?
- Mean-variance vs risk parity vs equal weight?

## Data Sources

### Primary
- **Multi-asset ETFs** - Stocks, bonds, commodities, alternatives
- **Historical returns** - For optimization inputs
- **Covariance matrices** - For risk modeling

### Secondary
- **Factor returns** - For factor-based portfolios
- **Transaction costs** - For rebalancing analysis

## Common Analyses

### 1. Mean-Variance Optimization
```python
from portfolio.optimizer import PortfolioOptimizer
optimizer = PortfolioOptimizer(returns, method='mean_variance')
weights = optimizer.optimize(target_return=0.08)
```

### 2. Risk Parity
```python
# Equal risk contribution
optimizer = PortfolioOptimizer(returns, method='risk_parity')
weights = optimizer.optimize()
```

### 3. Rebalancing Analysis
```python
# Compare rebalancing frequencies
monthly_returns = backtest_rebalance(weights, returns, freq='M')
quarterly_returns = backtest_rebalance(weights, returns, freq='Q')
```

### 4. Efficient Frontier
```python
# Plot risk-return tradeoff
target_returns = np.linspace(0.05, 0.15, 20)
frontier = [optimizer.optimize(target_return=r) for r in target_returns]
```

## Study Templates

- `notebooks/portfolio_optimization.ipynb` - MVO and alternatives
- `notebooks/rebalancing_frequency.ipynb` - Optimal rebalancing
- `notebooks/risk_parity.ipynb` - Risk parity portfolios
- `notebooks/efficient_frontier.ipynb` - Risk-return tradeoff

## Completed Studies

See `studies/INDEX.md` for full list.

## Promising Studies (Research Candidates)

None yet - this is a new field.

## Related Fields

- **Correlation** - Key input for optimization
- **Volatility** - Risk targeting and vol scaling
- **Momentum** - Momentum-based tilts
- **Macro** - Regime-based allocation

## References

- "Portfolio Selection" (Markowitz)
- "Risk Parity Fundamentals" (Qian)
- "A Practitioner's Guide to Asset Allocation" (Ang)

## Notes

- Mean-variance is sensitive to input estimates
- Use shrinkage for covariance estimation
- Consider transaction costs in rebalancing
- Risk parity often more robust than MVO
- Equal weight is hard to beat out-of-sample
