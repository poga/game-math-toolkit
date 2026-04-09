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
    elasticity = mo.ui.slider(start=0.1, stop=1.0, step=0.05, value=0.75,
                               show_value=True, label="Elasticity (k)")
    demand_base = mo.ui.slider(start=5, stop=30, step=1, value=15,
                                show_value=True, label="Base demand")
    supply_base = mo.ui.slider(start=5, stop=30, step=1, value=12,
                                show_value=True, label="Base supply")
    volatility = mo.ui.slider(start=0.0, stop=5.0, step=0.5, value=2.0,
                               show_value=True, label="Demand volatility")
    mo.vstack([
        mo.md("## Market Pricing — Bounded Elastic Model"),
        mo.md("Victoria 3-style pricing: `P = P_base * (1 + k * clamp(ratio, -1, +1))`. Prices stay within a fixed band. No hyperinflation, no deflation."),
        mo.hstack([p_base, elasticity]),
        mo.hstack([demand_base, supply_base]),
        volatility,
    ])
    return demand_base, elasticity, p_base, supply_base, volatility


@app.cell
def _(demand_base, elasticity, np, p_base, supply_base, volatility):
    ticks = 200
    _rng = np.random.default_rng(42)

    prices = np.zeros(ticks)
    buys = np.zeros(ticks)
    sells = np.zeros(ticks)

    for _t in range(ticks):
        _demand_noise = _rng.normal(0, volatility.value)
        _buy = max(1, demand_base.value + _demand_noise)
        _sell = max(1, supply_base.value + _rng.normal(0, 1))
        buys[_t] = _buy
        sells[_t] = _sell

        _ratio = (_buy - _sell) / max(1, min(_buy, _sell))
        _clamped = max(-1, min(1, _ratio))
        prices[_t] = p_base.value * (1 + elasticity.value * _clamped)
    return buys, prices, sells, ticks


@app.cell
def _(elasticity, go, mo, np, p_base, prices, ticks):
    _t = np.arange(ticks)
    _upper_bound = p_base.value * (1 + elasticity.value)
    _lower_bound = p_base.value * (1 - elasticity.value)
    _fig = go.Figure()
    _fig.add_trace(go.Scatter(x=_t, y=prices, name="Price",
                              line=dict(color="#636EFA", width=2)))
    _fig.add_hline(y=p_base.value, line_dash="dash", line_color="gray",
                   annotation_text="Base price")
    _fig.add_hline(y=_upper_bound, line_dash="dot", line_color="red",
                   annotation_text=f"Upper bound ({_upper_bound:.0f})")
    _fig.add_hline(y=_lower_bound, line_dash="dot", line_color="green",
                   annotation_text=f"Lower bound ({_lower_bound:.0f})")
    _fig.update_layout(
        title="Price Over Time (Bounded)",
        xaxis_title="Tick",
        yaxis_title="Price",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Price Movement"),
        mo.md(f"Price is bounded between **{_lower_bound:.0f}** and **{_upper_bound:.0f}** ({(1-elasticity.value)*100:.0f}% to {(1+elasticity.value)*100:.0f}% of base). No matter how extreme the demand shock, the price never leaves this band."),
        _fig,
    ])
    return


@app.cell
def _(buys, go, mo, np, sells, ticks):
    _t = np.arange(ticks)
    _fig2 = go.Figure()
    _fig2.add_trace(go.Scatter(x=_t, y=buys, name="Buy orders (demand)",
                               line=dict(color="#EF553B")))
    _fig2.add_trace(go.Scatter(x=_t, y=sells, name="Sell orders (supply)",
                               line=dict(color="#00CC96")))
    _fig2.update_layout(
        title="Supply vs Demand",
        xaxis_title="Tick",
        yaxis_title="Orders per tick",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Supply and Demand"),
        mo.md("When demand (red) exceeds supply (green), prices rise. When supply exceeds demand, prices fall. The clamping prevents extreme ratios from producing extreme prices."),
        _fig2,
    ])
    return


@app.cell
def _(elasticity, mo, np, p_base, prices):
    _avg_price = np.mean(prices)
    _price_std = np.std(prices)
    _pct_above_base = np.mean(prices > p_base.value) * 100
    _upper = p_base.value * (1 + elasticity.value)
    _lower = p_base.value * (1 - elasticity.value)
    mo.md(f"""### Summary

| Metric | Value |
|---|---|
| Base price | {p_base.value} |
| Price band | {_lower:.0f} — {_upper:.0f} |
| Average price | {_avg_price:.1f} |
| Price std dev | {_price_std:.1f} |
| Time above base | {_pct_above_base:.0f}% |

**Design levers:**
- **Elasticity (k):** Controls how wide the price band is. Victoria 3 uses k=0.75 (25%-175% band). Lower k → stickier prices. Higher k → more responsive.
- **Volatility:** Controls demand noise. High volatility + high elasticity = wild price swings within bounds. Low volatility = prices hover near base.
- **Base price:** The anchor. All other prices are relative to this. Victoria 3 example: Grain=20, Tools=40.

**Key insight:** Bounds matter more than curves. Victoria 3's entire market is held inside a 25%-175% band on purpose. The simulation can be deep and still refuse to let the economy explode.
""")
    return


if __name__ == "__main__":
    app.run()
