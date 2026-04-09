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
    p_base = mo.ui.slider(start=10, stop=100, step=5, value=40,
                           show_value=True, label="Base price")
    k = mo.ui.slider(start=0.1, stop=1.0, step=0.05, value=0.75,
                      show_value=True, label="Elasticity (k)")
    demand_base = mo.ui.slider(start=5, stop=30, step=1, value=15,
                                show_value=True, label="Base demand")
    supply_base = mo.ui.slider(start=5, stop=30, step=1, value=12,
                                show_value=True, label="Base supply")
    volatility = mo.ui.slider(start=0.0, stop=5.0, step=0.5, value=2.0,
                               show_value=True, label="Demand volatility")
    shock_tick = mo.ui.slider(start=20, stop=250, step=10, value=100,
                               show_value=True, label="Shock at tick")
    shock_size = mo.ui.slider(start=0, stop=50, step=5, value=20,
                               show_value=True, label="Shock magnitude")
    mo.vstack([
        mo.md("## How Markets Stay Stable (or Don't)"),
        mo.md("Three pricing models respond to the same demand. Victoria 3's bounded model holds steady. The unbounded model explodes. Watch what happens at the shock tick."),
        mo.hstack([p_base, k]),
        mo.hstack([demand_base, supply_base, volatility]),
        mo.hstack([shock_tick, shock_size]),
    ])
    return (p_base, k, demand_base, supply_base, volatility, shock_tick, shock_size)


@app.cell
def _(p_base, k, demand_base, supply_base, volatility, shock_tick, shock_size, np):
    ticks = 300
    _rng = np.random.default_rng(42)

    demand = np.zeros(ticks)
    supply = np.zeros(ticks)

    for _t in range(ticks):
        demand[_t] = max(1, demand_base.value + _rng.normal(0, volatility.value))
        supply[_t] = max(1, supply_base.value + _rng.normal(0, 1))
        if _t == shock_tick.value:
            demand[_t] += shock_size.value

    _min_ds = np.maximum(1, np.minimum(demand, supply))
    ratio = (demand - supply) / _min_ds

    _k = k.value
    _p = p_base.value
    unbounded = _p * (1 + _k * ratio)
    victoria3 = _p * (1 + _k * np.clip(ratio, -1, 1))
    logarithmic = _p * (1 + _k * np.sign(ratio) * np.log1p(np.abs(ratio)))

    return (ticks, demand, supply, unbounded, victoria3, logarithmic)


@app.cell
def _(ticks, unbounded, victoria3, logarithmic, p_base, k, go, mo, np):
    _t = np.arange(ticks)
    _upper = p_base.value * (1 + k.value)
    _lower = p_base.value * (1 - k.value)
    _fig = go.Figure()
    _fig.add_trace(go.Scatter(x=_t, y=unbounded, name="Unbounded linear",
                               line=dict(color="#EF553B", width=2)))
    _fig.add_trace(go.Scatter(x=_t, y=victoria3, name="Victoria 3 (bounded)",
                               line=dict(color="#636EFA", width=3)))
    _fig.add_trace(go.Scatter(x=_t, y=logarithmic, name="Logarithmic",
                               line=dict(color="#00CC96", width=2)))
    _fig.add_hline(y=p_base.value, line_dash="dash", line_color="gray",
                    annotation_text="Base price")
    _fig.add_hline(y=_upper, line_dash="dot", line_color="gray",
                    annotation_text=f"Victoria 3 ceiling ({_upper:.0f})")
    _fig.add_hline(y=_lower, line_dash="dot", line_color="gray",
                    annotation_text=f"Victoria 3 floor ({_lower:.0f})")
    _fig.update_layout(
        title="Price Response — Same Market, Different Models",
        xaxis_title="Tick",
        yaxis_title="Price",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Price Response — The Feel Chart"),
        mo.md("All three models see the same supply and demand. Unbounded (red) can spike to infinity. Victoria 3 (blue) caps at a fixed band. Logarithmic (green) softens extremes but has no hard cap."),
        _fig,
    ])
    return


@app.cell
def _(ticks, unbounded, victoria3, logarithmic, p_base, shock_tick, go, mo, np):
    _base = p_base.value
    _threshold = _base * 0.1
    _start = min(shock_tick.value + 1, ticks)

    def _recovery(prices):
        for _t in range(_start, len(prices)):
            if abs(prices[_t] - _base) <= _threshold:
                return _t - shock_tick.value
        return ticks - shock_tick.value

    _labels = ["Unbounded", "Victoria 3", "Logarithmic"]
    _values = [_recovery(unbounded), _recovery(victoria3), _recovery(logarithmic)]
    _fig = go.Figure(data=[go.Bar(
        x=_labels, y=_values,
        marker_color=["#EF553B", "#636EFA", "#00CC96"],
    )])
    _fig.update_layout(
        title="Recovery Time After Shock (Ticks to Return Within 10% of Base)",
        yaxis_title="Ticks after shock",
    )
    mo.vstack([
        mo.md("### Price Recovery — Market Resilience"),
        mo.md(f"After the demand shock at tick {shock_tick.value}, how long until prices return to normal? Shorter = more resilient market."),
        _fig,
    ])
    return


@app.cell
def _(ticks, unbounded, victoria3, logarithmic, go, mo, np):
    _t = np.arange(ticks)
    _window = 20

    def _spread(prices):
        _result = np.zeros(len(prices))
        for _i in range(len(prices)):
            _s = max(0, _i - _window + 1)
            _result[_i] = np.max(prices[_s:_i + 1]) - np.min(prices[_s:_i + 1])
        return _result

    _fig = go.Figure()
    _fig.add_trace(go.Scatter(x=_t, y=_spread(unbounded), name="Unbounded",
                               line=dict(color="#EF553B")))
    _fig.add_trace(go.Scatter(x=_t, y=_spread(victoria3), name="Victoria 3",
                               line=dict(color="#636EFA")))
    _fig.add_trace(go.Scatter(x=_t, y=_spread(logarithmic), name="Logarithmic",
                               line=dict(color="#00CC96")))
    _fig.update_layout(
        title="Merchant Profit Window (Price Spread Over 20-Tick Window)",
        xaxis_title="Tick",
        yaxis_title="Max spread (buy low, sell high)",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Merchant Profit Window — Arbitrage Opportunity"),
        mo.md("Rolling 20-tick price range for each model. Wider spread = more profit for merchants who time trades. Bounded models cap arbitrage. Unbounded models create gold-rush windows."),
        _fig,
    ])
    return


@app.cell
def _(unbounded, victoria3, logarithmic, p_base, k, mo, np):
    _base = p_base.value
    mo.md(f"""### Summary

| Metric | Unbounded | Victoria 3 | Logarithmic |
|---|---|---|---|
| Max price | {np.max(unbounded):.1f} | {np.max(victoria3):.1f} | {np.max(logarithmic):.1f} |
| Min price | {np.min(unbounded):.1f} | {np.min(victoria3):.1f} | {np.min(logarithmic):.1f} |
| Time above 150% base | {np.sum(unbounded > _base * 1.5)} ticks | {np.sum(victoria3 > _base * 1.5)} ticks | {np.sum(logarithmic > _base * 1.5)} ticks |
| Price std dev | {np.std(unbounded):.2f} | {np.std(victoria3):.2f} | {np.std(logarithmic):.2f} |

**Formulas:**
- **Unbounded:** `P = P_base * (1 + k * ratio)` — no bounds. Demand spikes produce proportional price spikes.
- **Victoria 3:** `P = P_base * (1 + {k.value} * clamp(ratio, -1, +1))` — prices bounded to {(1-k.value)*100:.0f}%–{(1+k.value)*100:.0f}% of base. The clamp is the entire design.
- **Logarithmic:** `P = P_base * (1 + k * sign(r) * log(1+|r|))` — soft ceiling. Approaches bounds asymptotically.

**Key insight:** Victoria 3's entire economy is held inside a fixed band ({_base*(1-k.value):.0f} to {_base*(1+k.value):.0f}) on purpose. A simulation can be deep and still refuse to let the economy explode. Bounds matter more than curves.
""")
    return


if __name__ == "__main__":
    app.run()
