# Chapter 2 Q&A - Fixed Income Relative Value Analysis

## Questions Answered

### Q1: How to do MLE (PMLE) and method of moments in parameter estimation specifically after determining functional forms?

**Answer:**

FIRV Chapter 2 makes an important distinction:

- if the chosen SDE has an analytical transition density, use exact MLE
- if the transition density is not available in closed form, use PMLE/QMLE

That is exactly why, in the `EUR 5Y5Y - GBP 5Y5Y` swaption-volatility example, the authors first inspect the drift and diffusion diagnostic graphs in Figures `2.20` and `2.21`, decide that an OU process is adequate, and then use **exact MLE**, not PMLE, because the OU transition density is analytical.

#### 1. Start from the continuous-time model

For the OU specification used in the chapter:

$$
dX_t = \kappa(\mu - X_t)\,dt + \nu\,dW_t
$$

where:

- $X_t$ is the spread or volatility difference
- $\mu$ is the long-run mean
- $\kappa$ is the speed of mean reversion
- $\nu$ is the instantaneous volatility

The chapter also discusses the general SDE form

$$
dX_t = f(X_t)\,dt + g(X_t)\,dW_t
$$

and the estimation problem is: after choosing $f$ and $g$, how do we pin down the unknown parameters?

#### 2. Method of moments

The method-of-moments logic in Chapter 2 is:

1. derive theoretical moments implied by the SDE
2. compute matching empirical moments from the data
3. solve for the parameters that match theory to sample

For the stationary OU process:

$$
\mathbb{E}[X_t] = \mu, \qquad
\operatorname{Var}(X_t) = \frac{\nu^2}{2\kappa}
$$

and the lag-$\Delta$ autocorrelation is

$$
\rho(\Delta) = e^{-\kappa \Delta}
$$

So a simple moment-based estimator is:

$$
\hat \mu = \bar X,
\qquad
\hat \kappa = -\frac{1}{\Delta}\ln \hat \rho(\Delta),
\qquad
\hat \nu = \sqrt{2\hat \kappa\,\widehat{\operatorname{Var}}(X)}
$$

This is mathematically clean, but Chapter 2's point is that moment matching is only one admissible criterion. It is not automatically the best one for every trading problem.

#### 3. Exact MLE for OU

For OU, the conditional distribution is known exactly:

$$
X_{t+\Delta}\mid X_t
\sim
\mathcal{N}\!\left(
\mu + e^{-\kappa \Delta}(X_t-\mu),
\;
\frac{\nu^2}{2\kappa}\left(1-e^{-2\kappa\Delta}\right)
\right)
$$

So if we define

$$
m_t(\theta)=\mu + e^{-\kappa \Delta}(X_t-\mu),
\qquad
s^2(\theta)=\frac{\nu^2}{2\kappa}\left(1-e^{-2\kappa\Delta}\right),
$$

with parameter vector $\theta=(\mu,\kappa,\nu)$, the exact log-likelihood for observations $\{X_0,\dots,X_n\}$ is

$$
\ell(\theta)
=
-\frac{n}{2}\log(2\pi)
-\frac{n}{2}\log s^2(\theta)
-\frac{1}{2s^2(\theta)}
\sum_{i=0}^{n-1}\left(X_{i+1}-m_i(\theta)\right)^2
$$

You then maximize $\ell(\theta)$ numerically.

This is the mathematically correct OU MLE that the chapter uses in the swaption example after concluding from Figures `2.20` and `2.21` that the OU form is acceptable.

#### 4. PMLE for general drift/diffusion specifications

Once you move away from the closed-form OU case and let

$$
dX_t = f(X_t;\theta)\,dt + g(X_t;\theta)\,dW_t,
$$

the transition density is usually not available analytically. FIRV says this is where **PMLE** becomes the practical workhorse.

Using the Euler discretization over a small step $\Delta$:

$$
X_{t+\Delta}
\approx
X_t + f(X_t;\theta)\Delta + g(X_t;\theta)\sqrt{\Delta}\,\varepsilon_{t+\Delta},
\qquad
\varepsilon_{t+\Delta}\sim \mathcal{N}(0,1)
$$

Therefore the **pseudo** transition density is

$$
X_{t+\Delta}\mid X_t
\approx
\mathcal{N}\!\left(
X_t + f(X_t;\theta)\Delta,
\;
g(X_t;\theta)^2 \Delta
\right)
$$

and the pseudo log-likelihood is

$$
\ell_{\mathrm{PMLE}}(\theta)
=
-\frac12 \sum_{i=0}^{n-1}
\left[
\log\!\bigl(2\pi g(X_i;\theta)^2\Delta\bigr)
+
\frac{\left(X_{i+1}-X_i-f(X_i;\theta)\Delta\right)^2}
{g(X_i;\theta)^2\Delta}
\right]
$$

This is the exact object you maximize in PMLE.

#### 5. Why the Gaussian approximation is reasonable

Chapter 2's justification is local normality:

- over very small time intervals, diffusion increments are dominated by the Brownian term
- Brownian increments are Gaussian
- if $f$ and $g$ are smooth and $\Delta$ is small, the one-step transition density is well approximated by a Gaussian

That is why FIRV explicitly says PMLE with **daily data** is usually very close to exact MLE in practice.

The trade-off is:

- exact MLE: statistically cleaner, but often unavailable
- PMLE: tractable and usually accurate enough with daily data

The chapter is also explicit that PMLE estimators are generally not guaranteed to be consistent in full generality, and their asymptotic distribution is often not known in closed form. The book's stance is pragmatic: for daily financial data, this cost is usually small relative to the tractability gain.

#### 6. Concrete FIRV Chapter 2 example

For the `EUR 5Y5Y - GBP 5Y5Y` swaption-volatility spread, after the diagnostic-graph step the chapter reports MLE estimates approximately equal to:

- long-run mean: $\hat\mu \approx 1.046$
- instantaneous volatility: $\hat\nu \approx 28.25$
- speed of mean reversion: $\hat\kappa \approx 16.5$

Those estimates are then used to derive:

- half-life: about `15.4` calendar days
- conditional transition densities: Figure `2.22`
- first-passage densities: Figures `2.23` and `2.24`

That is the chapter's actual methodology:

1. diagnose $f$ and $g$
2. choose OU
3. use exact MLE because OU has analytical transition density
4. use the fitted SDE to price execution decisions

#### 7. Python skeleton

```python
import numpy as np
from scipy.optimize import minimize

def ou_neg_loglik(params, x, dt):
    mu, kappa, nu = params
    if kappa <= 0 or nu <= 0:
        return np.inf

    beta = np.exp(-kappa * dt)
    m = mu + beta * (x[:-1] - mu)
    s2 = (nu**2 / (2.0 * kappa)) * (1.0 - beta**2)

    resid = x[1:] - m
    nll = 0.5 * np.sum(np.log(2.0 * np.pi * s2) + resid**2 / s2)
    return nll

def pmle_neg_loglik(params, x, dt, f, g):
    # f and g are user-specified drift/diffusion functions
    theta = params
    mu_step = x[:-1] + f(x[:-1], theta) * dt
    var_step = (g(x[:-1], theta)**2) * dt
    if np.any(var_step <= 0):
        return np.inf

    resid = x[1:] - mu_step
    nll = 0.5 * np.sum(np.log(2.0 * np.pi * var_step) + resid**2 / var_step)
    return nll

# OU exact MLE
x = np.asarray(spread_series, dtype=float)
dt = 1.0 / 365.0
res = minimize(ou_neg_loglik, x0=[x.mean(), 10.0, x.std()], args=(x, dt))
mu_hat, kappa_hat, nu_hat = res.x
half_life_days = np.log(2.0) / kappa_hat * 365.0
```

**Bottom line:** for FIRV Chapter 2, the general rule is **PMLE for general daily-data SDEs, exact MLE when the chosen specification has analytical transition densities, as OU does**.

---

### Q2: How do we simulate if we do not know the estimated coefficient in the first place?

**Answer:**

This section of FIRV is about **parametric bootstrap / Monte Carlo inference conditional on a null model**, not about magically simulating before any parameter value exists.

The logic is:

1. choose a null hypothesis about the parameters
2. simulate data from that null model
3. re-estimate the parameters on each simulated sample
4. use the resulting empirical distribution to measure estimation error or test hypotheses

#### 1. The null-hypothesis object

Suppose your model is

$$
dX_t = f(X_t;\theta)\,dt + g(X_t;\theta)\,dW_t
$$

with unknown parameter vector $\theta$.

You must first specify a null value $\theta_0$. There are two common cases:

- **plug-in inference**: set $\theta_0=\hat\theta$, the estimate from real data
- **hypothesis testing**: set $\theta_0$ to the parameter values implied by the hypothesis you want to test

Examples:

- $H_0$: the true process is OU with $(\mu,\kappa,\nu)=(\hat\mu,\hat\kappa,\hat\nu)$
- $H_0$: no mean reversion, i.e. $\kappa=0$
- $H_0$: constant diffusion is adequate

You are **not** simulating the distribution of the coefficient first. You are **assuming a coefficient under $H_0$**, then asking what distribution your estimator would have if that hypothesis were true.

#### 2. Exact simulation setup

Let the observed sample have length $n+1$ with sampling interval $\Delta$ and starting value $X_0=x_0$.

For bootstrap replication $b=1,\dots,B$:

1. simulate a synthetic path
   $$
   X_0^{*(b)} = x_0,\qquad
   X_{i+1}^{*(b)} \sim p_\Delta(\,\cdot \mid X_i^{*(b)};\theta_0)
   $$
   for $i=0,\dots,n-1$
2. estimate the parameter from the simulated path:
   $$
   \hat\theta^{*(b)} = \hat\theta\!\left(X_0^{*(b)},\dots,X_n^{*(b)}\right)
   $$

The empirical distribution

$$
\{\hat\theta^{*(1)},\dots,\hat\theta^{*(B)}\}
$$

approximates the sampling distribution of $\hat\theta$ under $H_0:\theta=\theta_0$.

#### 3. Why this answers the "but we don't know the coefficient" confusion

Because the chapter is not saying:

- "simulate before estimating"

It is saying:

- "after specifying a null coefficient vector, simulate repeated samples to understand the estimator's error **under that null**"

That is exactly the same logic as any classical parametric Monte Carlo test.

#### 4. What you get from the bootstrap distribution

Once you have the replications, you can compute:

- standard errors:
  $$
  \widehat{\operatorname{se}}(\hat\theta_j)
  =
  \sqrt{\frac{1}{B-1}\sum_{b=1}^B
  \left(\hat\theta_j^{*(b)}-\bar\theta_j^*\right)^2}
  $$
- percentile confidence intervals
- bias estimates:
  $$
  \widehat{\operatorname{Bias}}(\hat\theta_j)
  =
  \bar\theta_j^* - \theta_{0,j}
  $$
- hypothesis tests by checking where the real-data estimate sits relative to the null-simulation distribution

#### 5. Exact OU example aligned to Chapter 2

Suppose the fitted OU parameters from the swaption-volatility example are:

$$
\theta_0 = (\mu,\kappa,\nu) = (1.046, 16.5, 28.25)
$$

Then under the null that the observed spread really follows that OU process, you simulate many synthetic `EUR 5Y5Y - GBP 5Y5Y` paths of the **same length as the real sample**, re-estimate $(\mu,\kappa,\nu)$ from each path, and inspect the empirical distribution of those estimates.

So the simulation loop is:

$$
X_{i+1}^{*(b)}
=
\mu + e^{-\kappa \Delta}(X_i^{*(b)}-\mu)
+
\sqrt{\frac{\nu^2}{2\kappa}\left(1-e^{-2\kappa\Delta}\right)}\,\varepsilon_{i+1}^{(b)}
$$

with $\varepsilon_{i+1}^{(b)}\sim\mathcal N(0,1)$.

#### 6. Python skeleton

```python
import numpy as np

def simulate_ou_exact(x0, mu, kappa, nu, dt, n_steps, rng):
    beta = np.exp(-kappa * dt)
    step_vol = np.sqrt((nu**2 / (2.0 * kappa)) * (1.0 - beta**2))
    x = np.empty(n_steps + 1)
    x[0] = x0
    for i in range(n_steps):
        x[i + 1] = mu + beta * (x[i] - mu) + step_vol * rng.normal()
    return x

def bootstrap_ou_sampling_distribution(x_real, mu0, kappa0, nu0, dt, B=10000, seed=0):
    rng = np.random.default_rng(seed)
    n_steps = len(x_real) - 1
    x0 = x_real[0]

    out = np.empty((B, 3))
    for b in range(B):
        x_sim = simulate_ou_exact(x0, mu0, kappa0, nu0, dt, n_steps, rng)
        out[b] = estimate_ou_mle(x_sim, dt)   # your exact MLE routine
    return out

# real-data estimate from Chapter 2 style workflow
mu_hat, kappa_hat, nu_hat = estimate_ou_mle(x_real, dt)
boot = bootstrap_ou_sampling_distribution(
    x_real, mu_hat, kappa_hat, nu_hat, dt, B=5000
)

se = boot.std(axis=0, ddof=1)
ci = np.quantile(boot, [0.025, 0.975], axis=0)
```

**Bottom line:** you do not need the coefficient's distribution before simulating. You need only a **null parameter value**, and the simulation produces the estimator distribution **conditional on that null**.

---

### Q3: How to compute transition probability using stochastic simulation? Why average terminal values?

**Answer:**

Your confusion comes from mixing up:

- the **one-step numerical simulation rule**
- the **multi-horizon transition density**

The transition density is not just a "step-wise property." It is the full conditional distribution of the state at a future horizon $T$, given the state today.

#### 1. Definition of transition density

For a Markov diffusion $X_t$, the transition density from current state $x_0$ at time $0$ to horizon $T$ is

$$
p_T(x \mid x_0)
$$

such that for any measurable set $A$,

$$
\mathbb P(X_T \in A \mid X_0 = x_0)
=
\int_A p_T(x \mid x_0)\,dx
$$

So when FIRV says "if we'd like to know the mean of a transition density, we can simulate sample paths and calculate the sample average of the terminal values," it means:

- simulate many independent paths from the same start $x_0$
- stop all paths at the same horizon $T$
- the cross-sectional distribution of terminal values approximates $p_T(\cdot \mid x_0)$

#### 2. Why terminal values across many paths represent the transition density

Fix a start value $X_0=x_0$ and horizon $T$.
For simulation replication $m=1,\dots,N$, generate one path:

$$
X_0^{(m)} = x_0,\quad
X_{\delta}^{(m)},\quad
X_{2\delta}^{(m)},\dots,\quad
X_T^{(m)}
$$

where $\delta=T/M$ is a small simulation step.

Each terminal value $X_T^{(m)}$ is one draw from the conditional law of $X_T \mid X_0=x_0$.
Therefore:

$$
X_T^{(1)},\dots,X_T^{(N)}
\stackrel{\text{approx}}{\sim}
p_T(\cdot\mid x_0)
$$

That is why you average terminal values:

$$
\widehat{\mathbb E}[X_T\mid X_0=x_0]
=
\frac{1}{N}\sum_{m=1}^N X_T^{(m)}
$$

and estimate variance similarly:

$$
\widehat{\operatorname{Var}}(X_T\mid X_0=x_0)
=
\frac{1}{N-1}\sum_{m=1}^N
\left(X_T^{(m)}-\bar X_T\right)^2
$$

#### 3. Monte Carlo convergence

Let $Y_m = X_T^{(m)}$.
If the paths are simulated independently and $Y_m$ is integrable, then by the strong law of large numbers:

$$
\frac1N\sum_{m=1}^N Y_m
\xrightarrow{\text{a.s.}}
\mathbb E[X_T\mid X_0=x_0]
$$

More generally, for any integrable test function $\varphi$:

$$
\frac1N\sum_{m=1}^N \varphi(Y_m)
\xrightarrow{\text{a.s.}}
\mathbb E[\varphi(X_T)\mid X_0=x_0]
=
\int \varphi(x)\,p_T(x\mid x_0)\,dx
$$

Three important choices are:

- $\varphi(x)=x$ gives the conditional mean
- $\varphi(x)=x^2$ gives the second moment
- $\varphi(x)=\mathbf 1_{\{x\le a\}}$ gives the conditional CDF at $a$

So the chapter's statement is mathematically exact, not heuristic.

#### 4. Full transition density via KDE

Once you have terminal values $\{Y_m\}_{m=1}^N$, FIRV recommends either:

- a histogram: Figure `2.13`
- a Gaussian kernel density estimate: Figures `2.14` and `2.15`

The Gaussian KDE is:

$$
\hat p_h(x\mid x_0)
=
\frac{1}{Nh}\sum_{m=1}^N
K\!\left(\frac{x-Y_m}{h}\right)
$$

where $K(u)=\frac{1}{\sqrt{2\pi}}e^{-u^2/2}$ is the Gaussian kernel and $h$ is the bandwidth.

This is exactly what the chapter describes:

- every terminal value contributes to every evaluation point $x$
- nearby terminal values contribute more
- far-away terminal values contribute less

#### 5. Why your "step-wise" intuition is incomplete

You are right that the simulated path is generated **step by step**.
But the object of interest is not the one-step increment density; it is the **$T$-horizon conditional density**.

Simulation uses small steps only as a numerical device to approximate:

$$
p_T(\cdot\mid x_0)
$$

The terminal values summarize the entire path evolution between $0$ and $T$ into a draw from the horizon-$T$ transition law.

#### 6. Concrete FIRV Chapter 2 example

In the swaption-volatility example, the authors calibrate the OU process to the `EUR 5Y5Y - GBP 5Y5Y` spread, then show:

- unconditional density plus several conditional densities in Figure `2.22`
- probabilities such as the chance the spread remains above `12.35` after `1` week, `1` month, and `3` months

That is exactly a transition-density application:

- same initial state: current spread `12.35`
- different horizons: `1w`, `1m`, `3m`
- quantities read from the simulated or analytical density

#### 7. Python skeleton

```python
import numpy as np
from scipy.stats import gaussian_kde

def simulate_terminal_values(simulate_path, x0, horizon, n_paths, rng):
    terminals = np.empty(n_paths)
    for m in range(n_paths):
        path = simulate_path(x0=x0, horizon=horizon, rng=rng)
        terminals[m] = path[-1]
    return terminals

rng = np.random.default_rng(0)
terminals = simulate_terminal_values(
    simulate_path=simulate_general_sde,
    x0=12.35,
    horizon=30/365,   # 30 calendar days
    n_paths=10000,
    rng=rng,
)

mean_T = terminals.mean()
std_T = terminals.std(ddof=1)
kde = gaussian_kde(terminals, bw_method=0.25)

# Example: P(X_T <= 7 | X_0 = 12.35)
prob_hit_region = np.mean(terminals <= 7.0)
```

**Bottom line:** averaging terminal values is correct because each terminal value is one Monte Carlo draw from the horizon-$T$ transition density.

---

### Q4: First passage time paradox - expected path vs expected time

**Answer:**

This is the most subtle point in the chapter. FIRV is warning you not to confuse:

1. the deterministic curve of **expected values through time**
2. the random variable **time taken to hit a specified level**

These are mathematically different objects, and confusing them leads to a paradox.

#### 1. The Paradox Statement

For an OU process starting above the mean ($x_0 > \mu$), we observe two seemingly contradictory facts:

**Fact A:** The expected path never hits $\mu$ in finite time

**Fact B:** The expected hitting time to $\mu$ is finite

**The Question:** "If the expected path never reaches $\mu$, how can individual paths hit it with a finite expected time?"

#### 2. Expected path for OU (Fact A)

For OU:

$$
dX_t = \kappa(\mu - X_t)\,dt + \nu\,dW_t
$$

the conditional mean is

$$
m(t)
:=
\mathbb E[X_t\mid X_0=x_0]
=
\mu + (x_0-\mu)e^{-\kappa t}
$$

If $x_0>\mu$, then $m(t)$ decreases exponentially toward $\mu$, but never equals $\mu$ at finite $t$:

$$
m(t)-\mu = (x_0-\mu)e^{-\kappa t} > 0
\qquad\text{for all finite } t
$$

**Interpretation:** The deterministic expected path approaches the mean asymptotically but never actually reaches it.

#### 3. First-passage time (Fact B)

For a target level $a$, define the hitting time

$$
\tau_a := \inf\{t\ge 0 : X_t = a\}
$$

This is a **random variable** — different for each sample path.

If the process is started above the mean and $a=\mu$, then despite the expected path never hitting $\mu$:

- Individual sample paths cross $\mu$ all the time (due to the diffusion term $\nu dW_t$)
- The expected hitting time $\mathbb E[\tau_\mu]$ is finite

In the book's example: $\mathbb E[\tau_\mu] \approx 38.25$ days.

#### 4. The Resolution: Two Different Mathematical Objects

The paradox arises from confusing:

**Object 1 - Expected Path:** $m(t) = \mathbb E[X_t]$
- This is the **expectation of position** at each time $t$
- A deterministic function of time
- The average position across all possible paths at time $t$
- Never reaches $\mu$ in finite time

**Object 2 - Expected Hitting Time:** $\mathbb E[\tau_\mu]$
- This is the **expectation of a random time**
- The average time it takes for a path to hit $\mu$
- Finite because individual paths hit $\mu$ frequently

**Key insight:**

$$
\text{"time when } m(t)=\mu\text{"}
\neq
\mathbb E[\tau_\mu]
$$

The time when the expected path hits $\mu$ (infinite) is NOT the same as the expected time for a path to hit $\mu$ (finite).

#### 5. Intuitive Picture

Imagine simulating 1000 paths starting at $x_0 = 12.35$ with mean $\mu = 1.046$:

**At each time $t$:**
- Some paths are above $\mu$, some below
- The **average position** $m(t)$ is still above $\mu$ (but getting closer)
- At $t = 38$ days, $m(38) > \mu$ (expected path hasn't hit yet)

**Hitting times across paths:**
- Path 1 hits $\mu$ at day 5
- Path 2 hits $\mu$ at day 20
- Path 3 hits $\mu$ at day 50
- Path 4 hits $\mu$ at day 80
- ...
- **Average hitting time** $\approx 38$ days

**The key:** The average position at day 38 is NOT equal to $\mu$, but the average time to hit $\mu$ IS 38 days.

#### 6. Why you cannot replace the random time by its mean

The key mathematical mistake would be to write

$$
\mathbb E[X_{\tau_a}] \stackrel{\text{wrong}}{=} m(\mathbb E[\tau_a])
$$

This is false because $\tau_a$ is random and $m(t)$ is nonlinear.

In fact:

$$
m(t)=\mu + (x_0-\mu)e^{-\kappa t}
$$

contains the convex function $e^{-\kappa t}$.
Since $\phi(t)=e^{-\kappa t}$ has

$$
\phi''(t)=\kappa^2 e^{-\kappa t} > 0,
$$

Jensen's inequality gives

$$
\mathbb E[e^{-\kappa \tau_a}] \ge e^{-\kappa \mathbb E[\tau_a]}
$$

So even if you tried to plug the random hitting time into the exponential-decay formula, the average of the exponential is **not** the exponential evaluated at the average time.

That is the Jensen point the chapter is gesturing toward.

#### 4. Why volatility creates asymmetry in hitting times

Suppose the process starts at $x_0=12.35$ and you want to hit $a=7$, with long-run mean near $\mu=1.046$.

From above the target, volatility affects $\tau_a$ asymmetrically:

- a favorable downward shock can hit the target quickly
- an unfavorable upward shock moves the process farther away from the target, and mean reversion must then work from an even worse starting point

That creates a **right-skewed** hitting-time distribution:

- many paths hit reasonably quickly
- some paths wander away first and take much longer

That is exactly what FIRV's first-passage densities show.

#### 5. Concrete FIRV Chapter 2 example

In the swaption-volatility example:

- current level: `12.35`
- estimated long-run mean: about `1.046`
- target `7`: Figure `2.23`
- target `1.046`: Figure `2.24`

The chapter reports:

- for target `7`, mode about `7` days and mean about `14.9` days
- for target `1.046`, mode about `26` days and mean about `38.25` days

This is the exact illustration of the paradox:

- the expected path never literally hits the mean in finite time
- but the expected hitting time to the mean is finite and, in this example, about `38.25` days

#### 6. Deterministic crossing time versus expected hitting time

For a target $a>\mu$, the deterministic time when the expected path reaches $a$ solves

$$
\mu + (x_0-\mu)e^{-\kappa t_{\text{path}}}=a
$$

so

$$
t_{\text{path}}
=
\frac{1}{\kappa}\ln\!\left(\frac{x_0-\mu}{a-\mu}\right)
$$

This is a deterministic number derived from the mean curve.
It is **not** the same object as

$$
\mathbb E[\tau_a].
$$

The two can be numerically close for some targets, but there is no theorem making them equal.

#### 7. Python skeleton

```python
import numpy as np

def first_passage_times(paths, target):
    # paths: shape (n_paths, n_steps + 1)
    hit = []
    for path in paths:
        idx = np.where(path <= target)[0]   # use >= if target is above current level
        if len(idx) > 0:
            hit.append(idx[0])
    return np.array(hit)

paths = simulate_many_ou_paths(
    x0=12.35, mu=1.046, kappa=16.5, nu=28.25,
    dt=1/365, n_steps=180, n_paths=10000
)

tau_7 = first_passage_times(paths, target=7.0) / (1/365)
tau_mu = first_passage_times(paths, target=1.046) / (1/365)

mean_tau_7 = tau_7.mean()
mean_tau_mu = tau_mu.mean()
```

**Bottom line:** the expected-value path is a deterministic function of time, while first-passage time is a random time. The nonlinearity of the exponential map and the asymmetry introduced by volatility make these fundamentally different quantities.

---

### Q5: Expected value of the process decays exponentially - what does this mean?

**Answer:**

This statement is specific to the linear OU drift used in FIRV Chapter 2.

#### 1. Start from the OU SDE

$$
dX_t = \kappa(\mu - X_t)\,dt + \nu\,dW_t
$$

Rearrange:

$$
dX_t + \kappa X_t\,dt = \kappa\mu\,dt + \nu\,dW_t
$$

Multiply by the integrating factor $e^{\kappa t}$:

$$
e^{\kappa t} dX_t + \kappa e^{\kappa t} X_t\,dt
=
\kappa\mu e^{\kappa t}\,dt + \nu e^{\kappa t}\,dW_t
$$

The left-hand side is

$$
d\!\left(e^{\kappa t}X_t\right)
$$

so integrating from $0$ to $t$ gives

$$
e^{\kappa t}X_t - X_0
=
\kappa\mu\int_0^t e^{\kappa s}\,ds
+
\nu\int_0^t e^{\kappa s}\,dW_s
$$

Since

$$
\kappa\mu\int_0^t e^{\kappa s}\,ds
=
\mu(e^{\kappa t}-1),
$$

we obtain the exact OU solution

$$
X_t
=
\mu + (X_0-\mu)e^{-\kappa t}
+
\nu\int_0^t e^{-\kappa (t-s)}\,dW_s
$$

#### 2. Take conditional expectation

Conditional on $X_0=x_0$,

$$
\mathbb E\!\left[\int_0^t e^{-\kappa(t-s)}\,dW_s \,\middle|\, X_0=x_0\right]=0
$$

so

$$
\mathbb E[X_t\mid X_0=x_0]
=
\mu + (x_0-\mu)e^{-\kappa t}
$$

This is what the chapter means by "the expected value decays exponentially."

The **distance from the mean** is

$$
\mathbb E[X_t\mid X_0=x_0]-\mu
=
(x_0-\mu)e^{-\kappa t}
$$

so the distance shrinks by the multiplicative factor $e^{-\kappa t}$.

#### 3. Half-life derivation

The half-life $t_{1/2}$ is defined by:

$$
\left|\mathbb E[X_{t_{1/2}}\mid X_0=x_0]-\mu\right|
=
\frac12 |x_0-\mu|
$$

Substitute the exponential-decay formula:

$$
|x_0-\mu| e^{-\kappa t_{1/2}}
=
\frac12 |x_0-\mu|
$$

Cancel $|x_0-\mu|$:

$$
e^{-\kappa t_{1/2}} = \frac12
$$

Take logs:

$$
t_{1/2} = \frac{\ln 2}{\kappa}
$$

#### 4. Concrete FIRV Chapter 2 example

The chapter's swaption-volatility example estimates:

- current spread: `12.35`
- long-run mean: about `1.046`
- speed of mean reversion: about `16.5`

The chapter then states the half-life is `15.4` calendar days.

That is just the half-life formula with unit conversion:

$$
t_{1/2}
=
\frac{\ln 2}{16.5}\text{ years}
\approx 0.0420\text{ years}
\approx 15.4\text{ calendar days}
$$

So the interpretation is:

- today the spread is `12.35`
- expected excess above the mean is `12.35 - 1.046 = 11.304`
- after `15.4` days, the expected excess is half that:
  $$
  \frac{11.304}{2} = 5.652
  $$
- so the expected spread after one half-life is
  $$
  1.046 + 5.652 \approx 6.698
  $$

This is exactly why the chapter says short holding periods and tight targets often dominate for OU-type trades: most of the expected convergence happens early.

#### 5. Relation to Figure 2.22

Figure `2.22` shows the conditional densities over different horizons.
The mean of each conditional density moves according to

$$
\mu + (x_0-\mu)e^{-\kappa t},
$$

while the variance grows toward the stationary variance

$$
\frac{\nu^2}{2\kappa}.
$$

So the chart is the visual version of the OU solution:

- means move exponentially toward $\mu$
- densities broaden and converge to the unconditional density

#### 6. Python skeleton

```python
import numpy as np

def ou_conditional_mean(x0, mu, kappa, t):
    return mu + (x0 - mu) * np.exp(-kappa * t)

def ou_half_life(kappa):
    return np.log(2.0) / kappa

x0 = 12.35
mu = 1.046
kappa = 16.5            # per year

t_half_years = ou_half_life(kappa)
t_half_days = t_half_years * 365.0
x_half = ou_conditional_mean(x0, mu, kappa, t_half_years)

print(t_half_days)  # about 15.4
print(x_half)       # about 6.70
```

**Bottom line:** exponential decay means the **expected distance from the mean** shrinks multiplicatively, not linearly, and the half-life is the cleanest way to summarize that speed.
