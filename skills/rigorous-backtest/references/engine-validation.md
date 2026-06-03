# Engine Validation

Use a validation-adapter model, not an engine-replacement model.

## Engine Roles

## `local`

Role:
- primary research engine

Best for:
- portfolio-level strategy iteration
- optimizer-heavy work
- current notebook workflows

Confidence provided:
- research validity

Confidence missing unless cross-checked:
- execution realism

## `backtrader`

Role:
- first validation engine

Best for:
- execution timing checks
- walk-forward validation
- trade-log and broker-semantics cross-checks

Borrowed discipline:
- explicit “what is known when” timing
- next-bar execution framing
- slippage and analyzer-based validation

## `qlib`

Role:
- adapter-ready profile for research-workflow validation

Best for:
- cross-sectional and ranking-style strategies
- train/valid/test workflow discipline
- artifact and recorder-style reproducibility

Use in this repo:
- portability and workflow design reference now
- runtime adapter later, only where signals can be expressed in Qlib’s prediction-to-portfolio style

## `vnpy`

Role:
- adapter-ready profile for execution-realism validation

Best for:
- CTA-like or execution-sensitive strategies
- order/trade/daily-PnL artifact discipline
- realistic slippage, commission, and accounting fields

Use in this repo:
- portability and realism design reference now
- runtime adapter later for execution-sensitive strategies

## Required Engine Confidence Section

Every `rigorous` and `highly-rigorous` report must state one of:

- `engine_confidence: local_only`
- `engine_confidence: local_plus_backtrader`
- `engine_confidence: local_plus_profile_portability`
- `engine_confidence: backtrader_primary`

Also state:

- what the validation engine added
- what it still does not prove

## Validation Rules

- `specific`: validation engine optional
- `rigorous`: validation engine required for execution-sensitive or fragile strategies
- `highly-rigorous`: validation stance required for all strategies

If engines disagree materially:
- downgrade the verdict
- state which assumption changed the result
- do not hide the divergence in the summary
