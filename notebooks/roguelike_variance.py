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
                                 show_value=True, label="Nominal drop rate")
    num_attempts = mo.ui.slider(start=20, stop=200, step=10, value=100,
                                 show_value=True, label="Number of attempts")
    num_runs = mo.ui.slider(start=1000, stop=10000, step=1000, value=5000,
                             show_value=True, label="Simulation runs")
    mo.vstack([
        mo.md("## How Drop Systems Shape Run Outcomes"),
        mo.md("Three drop systems at the same nominal rate. True random has long droughts and lucky streaks. PRD (Dota 2) tightens the spread. Pity (StS-style) guarantees a floor — but changes the effective rate."),
        mo.md("**Dota 2 reference:** 10% (C=0.01475), **17% bash** (C=0.03980), 25% crit (C=0.08474)"),
        mo.hstack([nominal_rate, num_attempts]),
        num_runs,
    ])
    return (nominal_rate, num_attempts, num_runs)


@app.cell
def _(np):
    def prd_constant(p):
        """Binary search for PRD constant C (Dota 2 method).

        Finds C such that long-run proc rate equals nominal probability p.
        """
        if p <= 0:
            return 0.0
        if p >= 1:
            return 1.0
        lo, hi = 0.0, p
        for _ in range(100):
            mid = (lo + hi) / 2
            max_n = max(1, int(np.ceil(1.0 / mid))) if mid > 0 else 1
            expected = 0.0
            survive = 1.0
            for n in range(1, max_n + 1):
                p_n = min(1.0, mid * n)
                expected += n * p_n * survive
                survive *= (1 - p_n)
            eff = 1.0 / expected if expected > 0 else 0
            if eff > p:
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2
    return (prd_constant,)


@app.cell
def _(nominal_rate, num_attempts, num_runs, np, prd_constant):
    _p = nominal_rate.value
    _n = num_attempts.value
    _runs = num_runs.value
    C = prd_constant(_p)

    # Same random rolls for all three systems — fair comparison
    _rng = np.random.default_rng(42)
    _rolls = _rng.random((_runs, _n))

    # True random: fixed probability
    random_counts = np.sum(_rolls < _p, axis=1)

    # Track counts and max drought for PRD and pity in one pass
    prd_counts = np.zeros(_runs, dtype=int)
    pity_counts = np.zeros(_runs, dtype=int)
    random_drought = np.zeros(_runs)
    prd_drought = np.zeros(_runs)
    pity_drought = np.zeros(_runs)

    _prd_att = np.zeros(_runs)
    _pity_att = np.zeros(_runs)
    _r_cur = np.zeros(_runs)
    _p_cur = np.zeros(_runs)
    _y_cur = np.zeros(_runs)

    for _i in range(_n):
        _roll = _rolls[:, _i]

        # True random drought tracking
        _r_proc = _roll < _p
        _r_cur += 1
        random_drought = np.maximum(random_drought, _r_cur)
        _r_cur[_r_proc] = 0

        # PRD: P(n) = C * n, solved so effective rate = p
        _prd_att += 1
        _p_proc = _roll < np.minimum(1.0, C * _prd_att)
        prd_counts += _p_proc
        _p_cur += 1
        prd_drought = np.maximum(prd_drought, _p_cur)
        _p_cur[_p_proc] = 0
        _prd_att[_p_proc] = 0

        # Pity (StS-style): P(n) = p * n, guaranteed by ceil(1/p)
        _pity_att += 1
        _y_proc = _roll < np.minimum(1.0, _p * _pity_att)
        pity_counts += _y_proc
        _y_cur += 1
        pity_drought = np.maximum(pity_drought, _y_cur)
        _y_cur[_y_proc] = 0
        _pity_att[_y_proc] = 0

    return (C, random_counts, prd_counts, pity_counts,
            random_drought, prd_drought, pity_drought)


@app.cell
def _(random_counts, prd_counts, pity_counts, num_attempts, go, mo, np):
    _fig = go.Figure()
    _fig.add_trace(go.Histogram(x=random_counts, name="True Random",
                                 opacity=0.6, marker_color="#EF553B",
                                 xbins=dict(size=1)))
    _fig.add_trace(go.Histogram(x=prd_counts, name="PRD (Dota 2)",
                                 opacity=0.6, marker_color="#636EFA",
                                 xbins=dict(size=1)))
    _fig.add_trace(go.Histogram(x=pity_counts, name="Pity (StS-style)",
                                 opacity=0.6, marker_color="#00CC96",
                                 xbins=dict(size=1)))
    _fig.update_layout(
        title=f"Total Drops in {num_attempts.value} Attempts — Distribution",
        xaxis_title="Number of drops",
        yaxis_title="Count",
        barmode="overlay",
        hovermode="x unified",
    )
    _r_std = np.std(random_counts)
    _p_std = np.std(prd_counts)
    _y_std = np.std(pity_counts)
    mo.vstack([
        mo.md("### Drop Distribution — The Feel Chart"),
        mo.md(f"Same rolls, different thresholds. True random sigma={_r_std:.1f}. PRD sigma={_p_std:.1f} (**{_r_std/_p_std:.1f}x tighter**). Pity sigma={_y_std:.1f} ({_r_std/_y_std:.1f}x tighter). Notice pity's distribution is shifted right — it procs MORE than the nominal rate."),
        _fig,
    ])
    return


@app.cell
def _(random_drought, prd_drought, pity_drought, C, nominal_rate, go, mo, np):
    _prd_max = int(np.ceil(1 / C))
    _pity_max = int(np.ceil(1 / nominal_rate.value))
    _fig = go.Figure()
    _fig.add_trace(go.Histogram(x=random_drought, name="True Random",
                                 opacity=0.6, marker_color="#EF553B", nbinsx=30))
    _fig.add_trace(go.Histogram(x=prd_drought, name="PRD",
                                 opacity=0.6, marker_color="#636EFA", nbinsx=30))
    _fig.add_trace(go.Histogram(x=pity_drought, name="Pity",
                                 opacity=0.6, marker_color="#00CC96", nbinsx=30))
    _fig.add_vline(x=_prd_max, line_dash="dash", line_color="#636EFA",
                    annotation_text=f"PRD guarantee ({_prd_max})")
    _fig.add_vline(x=_pity_max, line_dash="dash", line_color="#00CC96",
                    annotation_text=f"Pity guarantee ({_pity_max})")
    _fig.update_layout(
        title="Longest Drought (Max Attempts Without a Drop)",
        xaxis_title="Longest drought (attempts)",
        yaxis_title="Count",
        barmode="overlay",
    )
    mo.vstack([
        mo.md("### Longest Drought — The Worst-Case Experience"),
        mo.md(f"PRD guarantees a drop by attempt **{_prd_max}**. Pity guarantees by attempt **{_pity_max}**. True random has no guarantee — droughts of 30+ happen regularly at {nominal_rate.value:.0%}."),
        _fig,
    ])
    return


@app.cell
def _(C, nominal_rate, num_attempts, random_counts, prd_counts, pity_counts,
      random_drought, prd_drought, pity_drought, mo, np):
    def _pcts(data):
        return {p: np.percentile(data, p) for p in [10, 25, 50, 75, 90]}

    _r = _pcts(random_counts)
    _p = _pcts(prd_counts)
    _y = _pcts(pity_counts)
    _rate = nominal_rate.value
    _n = num_attempts.value
    _prd_max = int(np.ceil(1 / C))
    _pity_max = int(np.ceil(1 / _rate))

    # Effective rate: mean drops / attempts
    _r_eff = np.mean(random_counts) / _n
    _p_eff = np.mean(prd_counts) / _n
    _y_eff = np.mean(pity_counts) / _n

    # Consecutive proc probability: C^3 for PRD, p^3 for random and pity
    _r_consec = _rate ** 3
    _p_consec = C ** 3
    _y_consec = _rate ** 3

    _rows = "\n".join(
        f"| p{p} | {_r[p]:.1f} | {_p[p]:.1f} | {_y[p]:.1f} |"
        for p in [10, 25, 50, 75, 90]
    )
    mo.md(f"""### Summary

| Percentile | True Random | PRD (Dota 2) | Pity (StS) |
|---|---|---|---|
{_rows}

| Metric | True Random | PRD | Pity |
|---|---|---|---|
| Effective rate | {_r_eff:.1%} | {_p_eff:.1%} | {_y_eff:.1%} |
| Guaranteed by attempt | never | {_prd_max} | {_pity_max} |
| Max drought (observed) | {np.max(random_drought):.0f} | {np.max(prd_drought):.0f} | {np.max(pity_drought):.0f} |
| 3 consecutive procs | 1 in {1/_r_consec:,.0f} | 1 in {1/_p_consec:,.0f} | 1 in {1/_y_consec:,.0f} |
| Spread (p90 - p10) | {_r[90]-_r[10]:.1f} | {_p[90]-_p[10]:.1f} | {_y[90]-_y[10]:.1f} |

**PRD constant:** C = {C:.5f} for {_rate:.0%} nominal rate. First attempt: {C:.1%} chance. Guaranteed by attempt {_prd_max}.

**Key insight:** PRD matches the nominal rate exactly but tightens the distribution — fewer droughts AND fewer streaks. Pity is more aggressive (guaranteed by attempt {_pity_max}) but inflates the effective rate to {_y_eff:.1%}. Note: pity has the same consecutive-proc odds as true random — it prevents droughts but not streaks.

**Dota 2 reference:** C=0.01475 (10%), C=0.03980 (17% bash), C=0.08474 (25% crit).
""")
    return


if __name__ == "__main__":
    app.run()
