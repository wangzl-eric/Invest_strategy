# Subagents

Use subagents for serious work so the review is not single-threaded.

## Standard Merge Order

1. data and timing
2. signal logic and timestamp validity
3. engine and execution realism
4. stats and gates
5. optimizer comparison, if applicable
6. report and verdict synthesis

## `specific`

Launch:
- data/source sanity reviewer
- signal/lookahead reviewer

Required outputs:
- data coverage and timing caveats
- signal timestamp caveats

## `rigorous`

Launch:
- data/timing reviewer
- engine/execution reviewer
- stats/gates reviewer

Add when needed:
- optimizer reviewer for `optimizer_heavy`

Required outputs:
- timing and publication-lag findings
- execution convention and realism findings
- gate and robustness findings
- optimizer comparison findings when applicable

## `highly-rigorous`

Launch:
- data/revisions/publication-lag reviewer
- signal timestamp and normalization reviewer
- engine and execution-realism reviewer
- stats, overfitting, and gate reviewer

Add when needed:
- optimizer reviewer
- reporting reviewer for QuantStats artifact quality

Required outputs:
- explicit pass/fail or warning status from each reviewer
- escalation recommendation
- strongest contradiction found

## Escalation Power

- any reviewer can force tier escalation
- timing or stats reviewers can block approval-grade conclusions
- optimizer reviewer can block approval for optimizer-heavy strategies
- reporting reviewer can block serious reporting if artifact integrity is weak
