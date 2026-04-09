import marimo

app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import plotly.graph_objects as go
    return go, mo, np


@app.cell
def _(mo):
    nominal_rate = mo.ui.slider(start=0.05, stop=0.50, step=0.01, value=0.17,
                                 show_value=True, label="Drop rate (nominal)")
    num_floors = mo.ui.slider(start=5, stop=50, step=5, value=20,
                               show_value=True, label="Number of floors")
    num_runs = mo.ui.slider(start=1000, stop=10000, step=1000, value=5000,
                             show_value=True, label="Simulation runs")
    base_power_gain = mo.ui.slider(start=1, stop=20, step=1, value=5,
                                    show_value=True, label="Base power per drop")
    mo.vstack([
        mo.md("## Roguelike Run Variance"),
        mo.md("Simulate thousands of runs with PRD (pseudo-random distribution) drops. See how swingy the outcomes are."),
        mo.hstack([nominal_rate, num_floors]),
        mo.hstack([num_runs, base_power_gain]),
    ])
    return base_power_gain, nominal_rate, num_floors, num_runs


@app.cell
def _(np):
    def prd_constant(p):
        """Binary search for PRD constant C given nominal probability p.

        Finds C such that effective_rate = 1/E[attempts] equals p.
        """
        if p <= 0:
            return 0.0
        if p >= 1:
            return 1.0
        lo, hi = 0.0, p
        for _ in range(100):
            mid = (lo + hi) / 2
            max_n = max(1, int(np.ceil(1.0 / mid))) if mid > 0 else 1
            expected_attempts = 0.0
            prob_not_yet = 1.0
            for n in range(1, max_n + 1):
                p_n = min(1.0, mid * n)
                expected_attempts += n * p_n * prob_not_yet
                prob_not_yet *= (1 - p_n)
            effective_p = 1.0 / expected_attempts if expected_attempts > 0 else 0
            if effective_p > p:
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2

    def simulate_prd(n_runs, n_floors, C, power_fn, rng):
        """Vectorized Monte Carlo: simulate n_runs in parallel."""
        power = np.full(n_runs, 10.0)
        attempts = np.zeros(n_runs)
        for floor in range(1, n_floors + 1):
            attempts += 1
            rolls = rng.random(n_runs)
            procs = rolls < np.minimum(1.0, C * attempts)
            power[procs] += power_fn(floor)
            attempts[procs] = 0
        return power

    def simulate_true_random(n_runs, n_floors, p, power_fn, rng):
        """Vectorized Monte Carlo with true random (no PRD)."""
        power = np.full(n_runs, 10.0)
        for floor in range(1, n_floors + 1):
            rolls = rng.random(n_runs)
            procs = rolls < p
            power[procs] += power_fn(floor)
        return power
    return prd_constant, simulate_prd, simulate_true_random


@app.cell
def _(base_power_gain, nominal_rate, np, num_floors, num_runs, prd_constant,
      simulate_prd, simulate_true_random):
    C = prd_constant(nominal_rate.value)
    _rng = np.random.default_rng(42)
    _power_fn = lambda floor: base_power_gain.value * floor ** 0.5

    prd_results = simulate_prd(num_runs.value, num_floors.value, C, _power_fn, _rng)
    _rng2 = np.random.default_rng(42)
    random_results = simulate_true_random(num_runs.value, num_floors.value,
                                           nominal_rate.value, _power_fn, _rng2)
    return C, prd_results, random_results


@app.cell
def _(go, mo, np, num_floors, prd_results, random_results):
    _fig = go.Figure()
    _fig.add_trace(go.Histogram(x=prd_results, name="PRD", opacity=0.7,
                                marker_color="#636EFA", nbinsx=40))
    _fig.add_trace(go.Histogram(x=random_results, name="True Random", opacity=0.7,
                                marker_color="#EF553B", nbinsx=40))
    _fig.update_layout(
        title=f"Player Power Distribution at Floor {num_floors.value}",
        xaxis_title="Total Power",
        yaxis_title="Count",
        barmode="overlay",
        hovermode="x unified",
    )
    _prd_std = np.std(prd_results)
    _rand_std = np.std(random_results)
    mo.vstack([
        mo.md("### Power Distribution — PRD vs True Random"),
        mo.md(f"PRD standard deviation: **{_prd_std:.1f}**. True random: **{_rand_std:.1f}**. PRD is **{_rand_std/_prd_std:.1f}x tighter** — fewer extreme outliers."),
        _fig,
    ])
    return


@app.cell
def _(C, mo, nominal_rate, np, prd_results, random_results):
    def _percentiles(data):
        return {p: np.percentile(data, p) for p in [10, 25, 50, 75, 90]}

    _prd_pct = _percentiles(prd_results)
    _rand_pct = _percentiles(random_results)

    _rows = "\n".join(
        f"| p{p} | {_prd_pct[p]:.1f} | {_rand_pct[p]:.1f} |"
        for p in [10, 25, 50, 75, 90]
    )
    mo.md(f"""### Percentile Table

| Percentile | PRD | True Random |
|---|---|---|
{_rows}

**Interpretation:**
- p10 = unlucky run (bottom 10%). p90 = lucky run (top 10%).
- The gap between p10 and p90 is the "swinginess" of the system.
- PRD p10-p90 range: **{_prd_pct[90]-_prd_pct[10]:.1f}**. True random: **{_rand_pct[90]-_rand_pct[10]:.1f}**.

**PRD constant:** C = {C:.5f} for nominal rate {nominal_rate.value:.0%}. This means first attempt has {C:.1%} chance, second has {2*C:.1%}, etc. Guaranteed proc by attempt {int(np.ceil(1/C))}.

**Reference:** Dota 2 uses C=0.03980 for 17% bash. Three consecutive procs at 17% under PRD: ~1 in 10,000. Under true random: ~1 in 200.
""")
    return


if __name__ == "__main__":
    app.run()
