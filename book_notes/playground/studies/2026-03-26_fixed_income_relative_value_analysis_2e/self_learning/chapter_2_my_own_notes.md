# My Own Notes and Thinking Questions — Chapter 2

> **Note:** Detailed answers to all red-flagged questions are in [`chapter_2_qa_response.md`](./chapter_2_qa_response.md)

---

## Core Concepts

### Stationarity vs Limiting Distribution

**Key insight:** Existence of limiting distribution implies stationarity, but stationarity does NOT imply existence of limiting distributions.

**Example:** Consider a scenario where $x \in \{0, 1\}$ and we design it to be non-random with periodic selection. It is stationary as its intertemporal relationship stays constant, but due to its periodic pattern $P(x_t)$ is highly dependent on $t/\theta$ where $\theta$ is the length of the period.

**Reference:** [Stack Exchange discussion](https://stats.stackexchange.com/questions/48262/what-is-the-difference-between-limiting-and-stationary-distributions)

### Mean Reversion and Alpha Generation

**Quote from book:** "Return predictability is a necessary, though not sufficient, condition for generating alpha, defined here as an atypically high, risk-adjusted return."

**Implication:** Mean reversion alone doesn't guarantee profitability — you need sufficient speed of reversion relative to volatility, costs, and carry.

### Ornstein-Uhlenbeck (OU) Process

**Parameter $\kappa$:** The strength at which the variable is pulled towards the long-run mean.

**Process specification:**
$$dX_t = \kappa(\mu - X_t)\,dt + \sigma dW_t$$

where:
- $X_t$ is the spread or dislocation measure
- $\mu$ is the long-run mean
- $\kappa$ is mean-reversion speed
- $\sigma$ is diffusion volatility

**Half-life:** $t_{1/2} = \frac{\ln 2}{\kappa}$

**Cross-reference:** See [`ch02_notes.md`](../ch02_notes.md) Section 2 for discrete-time estimation formulas.

---

## Parameter Estimation Methods

### Method of Moments (MoM) vs Maximum Likelihood Estimation (MLE)

✅ **Question ANSWERED:** How to do MLE (PMLE) and method of moments in parameter estimation specifically after determining functional forms → See [`chapter_2_qa_response.md`](./chapter_2_qa_response.md) Q1

### Pseudo Maximum Likelihood Estimation (PMLE)

**Why PMLE?** The book recommends using PMLE as the tractable and cost-effective way to approximate MLE for model specification.

**Considerations:**
1. Loss of consistency (trade-off for tractability)

**Properties:**
1. Locally normal when interval is small

**Context:** Functional specification in general may not have a closed-form representation of the likelihood function. In theory one can calculate the likelihood functions using numerical methods (e.g., solving PDE for each transition density numerically, using finite difference grids, simulations) → intractable → need to approximate likelihood function (PMLE, QMLE).

### Simulation-Based Hypothesis Testing

**Innovative approach:** The way this book conducts hypothesis testing by simulating and directly computing for estimation error rather than focusing on the analytical method (on the asymptotic limit) is kind of innovative.

✅ **Question ANSWERED:** Regarding the text: "To simulate the distributions of the drift and diffusion coefficients, under the hypothesis that these coefficients have known values, we can simulate the process so as to generate a simulated sample equal in size to our actual sample..." How do we simulate if we do not know the estimated coefficient in the first place? → See [`chapter_2_qa_response.md`](./chapter_2_qa_response.md) Q2

---

## Functional Form Selection

### Three Main Approaches

1. **Linear (e.g., OU process)**
   - Simplest specification
   - Constant drift and diffusion coefficients

2. **Polynomial with $1/x$ term**
   - More flexible
   - Mindful of how we should restrict the domain for $x$ to preserve mean reversion

3. **Non-parametric form** — Empirical approximation of the drift coefficient using historical data

**Steps for non-parametric estimation:**
1. Group by bucket (we need to correctly decide on the bucket)
2. For each bucket, compute the average subsequent change of each observation in the bucket
3. Plot with x → midpoint of the bucket, y → average subsequent change of observations
4. Select a functional form for $f(x)$ that has the ability to match the shape traced out by the above diagnostic graph

**Tip:** Useful to use various criteria to analyze twice in each instance.

**Cross-reference:** See [`ch02_notes.md`](../ch02_notes.md) Section 4 for state-dependent drift and diffusion discussion.

---

## Diagnostic Methodology

### Drift and Diffusion Graphs

**Purpose:** Reveal whether assumptions of constant parameters are appropriate.

**Quote from book:** "In practice, a diagnostic graph for the diffusion coefficient often reveals relatively high levels of volatility at high distances from the mean (see Figure 2.21 for a real-world example)."

### Volatility Heterogeneity

**Key observation:** Good entry opportunities tend to occur in times of market turmoil ("buy when there is blood on the streets"). But this also means that the assumption of a constant volatility (i.e., independent of the distance from the mean), as in an OU process, can lead to underestimating the risk of a trade and to an overestimation of its Sharpe ratio.

**Implication:** Using a diagnostic graph reveals whether the assumption of constant volatility is appropriate or needs to be corrected in order to reflect higher volatility and hence lower expected Sharpe ratios for a trade put on at extreme distance from its mean.

**Fact to be checked/played around:** In practice, a diagnostic graph for the diffusion coefficient often reveals relatively high levels of volatility at high distances from the mean.

**Implications:**
- Volatility adjustment for strategies
- Sharpe ratio adjustment

**Cross-reference:** Implement diagnostic graphs in [`01_mean_reversion.ipynb`](../01_mean_reversion.ipynb) — see notebook cells for drift/diffusion estimation.

---

## Ex Ante Analysis

### Ex Ante Sharpe Ratio

**Basic idea:** With simulation, we introduce distribution into the play → thus we can do hypothesis testing and obtain all the empirical moments → mean and standard deviation → expected Sharpe ratio.

**Tips:**
- Always consider the additional Sharpe ratio if new trades added instead of just looking at the per-trade Sharpe ratio
- The expected Sharpe ratio decreases with holding horizon → implies we should set short holding horizon and tight target (half the distance to the mean rather than the mean itself)

**Cross-reference:** See [`ch02_notes.md`](./ch02_notes.md) Section 6 for ex ante risk-adjusted return framework.

### First Passage Time

**Basic idea:** First passage time is a random variable. One approach to it is by simulation to construct a non-parametric density from it.

✅ **Question ANSWERED:** "I don't understand this: 'The key for anyone who finds the relation between these two questions paradoxical is to appreciate that they're two different questions. One question refers to the path of expected values as a function of time, whereas the other question refers to the expected values of the times taken to travel a certain distance along a sample path.'" → See [`chapter_2_qa_response.md`](./chapter_2_qa_response.md) Q4

### Transition Probability via Stochastic Simulation

✅ **Question ANSWERED:** How to compute transition probability using stochastic simulation? Why does the author say - "If we'd like to know the mean of a transition density, we can simulate sample paths and calculate the sample average of the terminal values"? How I understand is that transitional density is a step-wise property. Why do we need to average out different terminal values? → See [`chapter_2_qa_response.md`](./chapter_2_qa_response.md) Q3

### Gaussian Kernel Density Estimation

**Bandwidth parameter $h$:** Determines the smoothness of the Gaussian KDE.

**Understanding of the kernel density:** For each $x \in \text{Domain}$, the Gaussian kernel density of any point of $x$ would be the sum of all $K_i(x;h)$ where $i$ represents the $i$-th data point (path).

**


---

## Execution Strategy

### General Experience Tips

1. **Set target to halfway to the long-run mean**
   - Balances expected convergence vs holding time

2. **Use 2-sigma band → dynamic for the SDE**
   - Entry thresholds based on statistical significance

3. **Scaling in and out of a position as it moves away and toward its mean**
   - Embodies the idea of mean reversion: The further away from the mean, the higher the expected Sharpe ratio, hence the higher the size should be

**Cross-reference:** See [`ch02_notes.md`](./ch02_notes.md) Section 7 for execution optimization framework.


**How to quantify the mean-reverting behaviour**


1. Unconditional Density and transition densities with for different time horizons
   - As time horizon increases, the mean converge to the long run mean and the distribution of transition probability converge to the 
2. Sharpe Ratio
   - Sharpe Ratio tends to decline over time --> best risk-adjusted opportunity is at short horizons and most of the performance in the trade is expected to come in the early days
3. First Passage Time Density
   - can use them for profit targets or stop levels
   - Can customize first passage time as "hitting x before hitting y"

---

## Worked Example: Swaption IV Case

**Instrument:** IV of 5y5y swaption (5Y Options on 5Y Swaps) denominated in EUR and GBP respectively.

### Step-by-Step Workflow

**1. Visual inspection**
- Eyeball the time series and the difference and the volatility on the difference to monitor the mean-reverting behavior and its stability

**2. First-order non-parametric estimate of both drift and diffusion coefficient using diagnostic graph methodology**

What to expect:
- Average change to be negative when above long-run average and vice versa
  - Otherwise, there is no obvious strong linearity → need to consider non-linear specification for drift coefficient
- Check if the average standard deviation possesses non-linearity (volatility scales up when position is far from the long-run mean). If so we need to model the non-linearity

**3. Parameter Estimation**

Estimate:
1. The long-run mean
2. Speed of mean-reversion (represented in half-life)
3. Instantaneous volatility of the spread

In the example we assumed an OU process, hence the transition density has closed-form representation → we can use MLE to estimate the parameter.

**4. Expected value dynamics**

✅ **Question ANSWERED:** Expected value of the process decays exponentially? I don't understand this part... → See [`chapter_2_qa_response.md`](./chapter_2_qa_response.md) Q5

**5. Unconditional mean (stationary mean?)**

**6. First passage time for setting stop order and make statistical inference by CI and probability**

**Cross-reference:** Replicate this workflow in [`01_mean_reversion.ipynb`](./01_mean_reversion.ipynb) using Treasury butterfly proxy.

---

## Questions & Answers

All detailed answers to red-flagged questions are documented in [`chapter_2_qa_response.md`](./chapter_2_qa_response.md):

- **Q1:** MLE (PMLE) and method of moments in parameter estimation
- **Q2:** Simulation setup for hypothesis testing when coefficients are unknown
- **Q3:** Computing transition probability using stochastic simulation
- **Q4:** First passage time paradox explanation
- **Q5:** Expected value exponential decay

---

## Cross-References

### Related Files
- [`ch02_notes.md`](./ch02_notes.md) — Comprehensive chapter notes with framework summary
- [`chapter_2_qa_response.md`](./chapter_2_qa_response.md) — Detailed Q&A responses
- [`01_mean_reversion.ipynb`](./01_mean_reversion.ipynb) — Practical implementation notebook

### Key Notebook Cells
- Drift estimation → Cell [TBD]
- Diffusion diagnostics → Cell [TBD]
- First passage time simulation → Cell [TBD]
- Ex ante Sharpe ratio calculation → Cell [TBD]

### Book Sections
- Section 2.1: Mean Reversion vs Random Walk
- Section 2.2: Discrete-Time Estimation
- Section 2.3: Conditional Expectations and Variance
- Section 2.4: State-Dependent Drift and Diffusion
- Section 2.5: Distribution Forecasting and First-Passage Logic
- Section 2.6: Ex Ante Risk-Adjusted Return
