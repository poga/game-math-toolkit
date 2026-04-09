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
    customer_base = mo.ui.slider(start=1, stop=20, step=1, value=5,
                                  show_value=True, label="Base customer rate")
    revenue = mo.ui.slider(start=5, stop=50, step=5, value=20,
                            show_value=True, label="Revenue per customer")
    cost_per = mo.ui.slider(start=1, stop=40, step=1, value=12,
                             show_value=True, label="Cost per customer")
    overhead = mo.ui.slider(start=0, stop=50, step=5, value=10,
                             show_value=True, label="Fixed overhead per tick")
    growth_rate = mo.ui.slider(start=0.001, stop=0.05, step=0.001, value=0.01,
                                show_value=True, label="Reputation growth rate")
    upgrade_tick = mo.ui.slider(start=50, stop=400, step=50, value=100,
                                 show_value=True, label="Upgrade event at tick")
    mo.vstack([
        mo.md("## Restaurant Tycoon Economy"),
        mo.md("A simple economy with positive feedback: reputation brings customers, customers build reputation. Does it converge or snowball?"),
        mo.hstack([customer_base, revenue]),
        mo.hstack([cost_per, overhead]),
        mo.hstack([growth_rate, upgrade_tick]),
    ])
    return cost_per, customer_base, growth_rate, overhead, revenue, upgrade_tick


@app.cell
def _(cost_per, customer_base, growth_rate, np, overhead, revenue, upgrade_tick):
    ticks = 500
    stocks = {"gold": 100.0, "reputation": 1.0}
    history = {"gold": np.zeros(ticks), "reputation": np.zeros(ticks)}
    net_flow = {"gold": np.zeros(ticks), "reputation": np.zeros(ticks)}

    for _t in range(ticks):
        customers = customer_base.value * np.log(stocks["reputation"] + 1)
        gold_in = customers * revenue.value
        gold_out = customers * cost_per.value + overhead.value
        rep_in = growth_rate.value * customers

        stocks["gold"] += gold_in - gold_out
        stocks["reputation"] += rep_in

        if stocks["gold"] < 0:
            stocks["reputation"] *= 0.95
            stocks["gold"] = 0

        if _t == int(upgrade_tick.value):
            stocks["gold"] = max(0, stocks["gold"] - 500)
            stocks["reputation"] += 10

        history["gold"][_t] = stocks["gold"]
        history["reputation"][_t] = stocks["reputation"]
        net_flow["gold"][_t] = gold_in - gold_out
        net_flow["reputation"][_t] = rep_in
    return history, net_flow, ticks


@app.cell
def _(go, history, mo, np, ticks):
    _t = np.arange(ticks)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=_t, y=history["gold"], name="Gold",
                              line=dict(color="#FFD700")))
    fig.add_trace(go.Scatter(x=_t, y=history["reputation"], name="Reputation",
                              line=dict(color="#636EFA"), yaxis="y2"))
    fig.update_layout(
        title="Stock Levels Over Time",
        xaxis_title="Tick",
        yaxis=dict(title="Gold", title_font=dict(color="#FFD700")),
        yaxis2=dict(title="Reputation", title_font=dict(color="#636EFA"),
                    overlaying="y", side="right"),
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Stock Levels"),
        mo.md("Watch for unbounded growth (snowball) or depletion (death spiral). A healthy economy levels off."),
        fig,
    ])
    return


@app.cell
def _(go, mo, net_flow, np, ticks):
    _t = np.arange(ticks)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=_t, y=net_flow["gold"], name="Gold net flow",
                               line=dict(color="#FFD700")))
    fig2.add_hline(y=0, line_dash="dash", line_color="gray",
                    annotation_text="Equilibrium")
    fig2.update_layout(
        title="Net Gold Flow (Income - Expenses)",
        xaxis_title="Tick",
        yaxis_title="Gold per tick",
        hovermode="x unified",
    )
    zero_crossings = np.where(np.diff(np.sign(net_flow["gold"])))[0]
    if len(zero_crossings) > 0:
        note = f"Gold flow crosses zero at tick(s): {', '.join(str(x) for x in zero_crossings[:5])}"
    else:
        if net_flow["gold"][-1] > 0:
            note = "Gold flow is always positive — gold accumulates forever. Add a sink or reduce income."
        else:
            note = "Gold flow is always negative — the business bleeds money. Increase revenue or cut costs."
    mo.vstack([
        mo.md("### Net Flow — Finding Equilibrium"),
        mo.md(f"When the line crosses zero, the stock is at equilibrium. {note}"),
        fig2,
    ])
    return


@app.cell
def _(history, mo):
    final_gold = history["gold"][-1]
    final_rep = history["reputation"][-1]
    peak_gold = max(history["gold"])
    min_gold = min(history["gold"])
    mo.md(f"""### Summary

| Metric | Value |
|---|---|
| Final gold | {final_gold:,.0f} |
| Final reputation | {final_rep:,.1f} |
| Peak gold | {peak_gold:,.0f} |
| Min gold | {min_gold:,.0f} |
| Gold trend | {"Accumulating" if final_gold > 200 else "Stable" if final_gold > 50 else "Depleting"} |
| Reputation trend | {"Snowballing" if final_rep > 50 else "Growing" if final_rep > 5 else "Stagnant"} |

**Key insight:** The positive feedback loop (reputation → customers → reputation) is controlled by the growth rate slider. Low values (~0.005) produce stable growth. High values (~0.03+) produce exponential snowball. The upgrade event at the configured tick shows how a one-time perturbation ripples through the system.
""")
    return


if __name__ == "__main__":
    app.run()
