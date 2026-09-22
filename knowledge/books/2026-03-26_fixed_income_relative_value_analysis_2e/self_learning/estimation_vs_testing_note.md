# Estimation vs. Hypothesis Testing — Quick Reference

**Date:** 2026-04-23

---

## Core Distinction

| Aspect | MLE (Estimation) | Hypothesis Testing |
|--------|------------------|-------------------|
| **Question** | "What is θ?" | "Is θ = θ₀ plausible?" |
| **Output** | θ̂ = 0.05, 95% CI [0.02, 0.08] | Reject/Fail to reject H₀, p-value |
| **Information** | Magnitude + uncertainty | Binary decision |
| **Use case** | Building models, predictions | Testing specific claims |

---

## When to Use Each

### Use MLE (Estimation) — Default Approach
- **Want to know the parameter value** (most common)
- Building trading models → need μ̂ for forecasting
- Estimating risk parameters → need σ̂ for VaR
- Comparing strategies → need effect sizes
- **No specific hypothesis to test**

**Workflow:**
1. Estimate θ̂ via MLE
2. Get confidence interval (bootstrap or asymptotic)
3. Report: θ̂ = 0.05 [0.02, 0.08]

### Use Hypothesis Testing — Specific Claims Only
- **Testing a specific theoretical prediction** (e.g., theory says μ = 0)
- **Regulatory/compliance thresholds** (e.g., "Is risk < 5%?")
- **Benchmark comparisons** (e.g., "Does strategy beat zero?")
- **Need binary decision** (approve/reject, yes/no)
- **Formal p-value required** (publication, regulation)

**Workflow:**
1. State H₀: θ = θ₀
2. Compute test statistic from data
3. Compare to null distribution (bootstrap or theoretical)
4. Reject or fail to reject

---

## Key Insights

### 1. **They're Complementary, Not Substitutes**
- Estimation tells you **what** the parameter is
- Testing tells you **whether a specific claim is plausible**

### 2. **Modern Statistics Favors Estimation**
- **Old approach (1950s-1990s):** Heavy focus on p-values
- **Modern approach (2000s+):** Focus on effect sizes + confidence intervals
- **Why:** Estimation is more informative (magnitude, not just yes/no)

### 3. **Confidence Intervals Implicitly Test Many Hypotheses**
- CI [0.02, 0.08] implicitly rejects all θ₀ outside this range
- More informative than testing a single θ₀

### 4. **Bootstrap Under H₀ is Not "Biased"**
- Both classical tests and bootstrap assume H₀ to construct null distribution
- Classical: derives distribution mathematically
- Bootstrap: approximates distribution via simulation
- Both give H₀ "benefit of the doubt" by design (conservative)

---

## Example: Trading Strategy Drift

### Estimation Approach (Preferred):
```
Drift estimate: μ̂ = 0.05
95% CI: [0.02, 0.08]
```
**Interpretation:**
- Best estimate is 0.05
- Uncertainty quantified
- Clearly positive (0 not in CI)
- **Actionable:** Use μ̂ = 0.05 in forecasting

### Testing Approach:
```
H₀: μ = 0
p-value = 0.003
Reject H₀
```
**Interpretation:**
- Strategy beats zero
- **But doesn't tell you HOW MUCH**
- Less actionable for model building

---

## Practical Recommendation

**Default workflow:**
1. **Always estimate** θ̂ via MLE + confidence interval
2. **Add hypothesis testing only if:**
   - You have a specific θ₀ to test (theory, benchmark, threshold)
   - Binary decision required
   - Formal p-value needed

**For financial modeling:**
- Primary tool: MLE + bootstrap CI
- Secondary tool: Hypothesis testing for specific claims

---

## Bootstrap Clarification

### Where Does Randomness Come From?

**In parametric bootstrap for stochastic processes (e.g., diffusion models):**

```
dX_t = μ dt + σ dW_t
```

Under H₀: μ = μ₀ (fixed), but:
- Each bootstrap iteration generates a new Brownian path W_t
- Different W_t paths → different realized data → different μ̂*
- **Randomness comes from the stochastic term (dW_t), not from "not knowing μ₀"**

### Why Test If It's "Just Noise"?

The test answers: **"Is the difference between μ̂ and μ₀ explainable by noise alone, or is there real signal?"**

- Noise creates uncertainty in your estimator μ̂
- Bootstrap quantifies: "How much can noise make μ̂ deviate from μ₀?"
- If observed μ̂ is too extreme → unlikely to be just noise → reject H₀

---

## Summary

- **Estimation (MLE):** Use for finding parameter values (default approach)
- **Hypothesis Testing:** Use for testing specific claims (supplementary)
- **Both are valid:** They serve different purposes, not competing methods
- **Modern practice:** Emphasize estimation + confidence intervals over pure hypothesis testing
