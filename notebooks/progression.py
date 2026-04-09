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
    exponent = mo.ui.slider(start=1.0, stop=3.0, step=0.1, value=1.8,
                             show_value=True, label="Growth exponent (k)")
    base_cost = mo.ui.slider(start=100, stop=2000, step=100, value=500,
                              show_value=True, label="Base cost (a)")
    income_rate = mo.ui.slider(start=1, stop=30, step=1, value=10,
                                show_value=True, label="Income per level")
    income_exp = mo.ui.slider(start=0.3, stop=1.5, step=0.1, value=0.9,
                               show_value=True, label="Income exponent")
    mo.vstack([
        mo.md("## Progression Curve Parameters"),
        mo.md("Adjust these to shape how leveling feels. The key output is **time per level** — the ratio players actually experience."),
        mo.hstack([exponent, base_cost]),
        mo.hstack([income_rate, income_exp]),
    ])
    return base_cost, exponent, income_exp, income_rate


@app.cell
def _(base_cost, exponent, income_exp, income_rate, np):
    levels = np.arange(1, 101)
    cost = base_cost.value * levels ** exponent.value
    income = income_rate.value * levels ** income_exp.value
    time_to_level = cost / income
    return cost, income, levels, time_to_level


@app.cell
def _(cost, go, income, levels, mo):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=levels, y=cost, name="XP Cost", line=dict(color="#636EFA")))
    fig.add_trace(go.Scatter(x=levels, y=income, name="Income", line=dict(color="#00CC96"),
                              yaxis="y2"))
    fig.update_layout(
        title="XP Cost vs Income",
        xaxis_title="Level",
        yaxis=dict(title="XP Cost", titlefont=dict(color="#636EFA")),
        yaxis2=dict(title="Income", titlefont=dict(color="#00CC96"),
                    overlaying="y", side="right"),
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Cost and Income Curves"),
        mo.md("Cost (left axis) is what the player pays. Income (right axis) is what they earn. The gap between them determines the grind."),
        fig,
    ])
    return


@app.cell
def _(exponent, go, income_exp, levels, mo, time_to_level):
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=levels, y=time_to_level, name="Time per Level",
                               line=dict(color="#EF553B", width=3)))
    fig2.update_layout(
        title="Time per Level (Cost / Income) — What the Player Feels",
        xaxis_title="Level",
        yaxis_title="Time (arbitrary units)",
        hovermode="x unified",
    )
    ratio = exponent.value - income_exp.value
    if ratio > 0.5:
        shape = "Rising steeply — late game becomes a heavy grind"
    elif ratio > 0:
        shape = "Rising gently — moderate pacing"
    else:
        shape = "Flat or falling — leveling gets easier over time"
    mo.vstack([
        mo.md("### Time per Level — The Curve That Matters"),
        mo.md(f"With cost exponent **{exponent.value}** and income exponent **{income_exp.value}**, the effective grind exponent is **{ratio:.1f}**. {shape}"),
        fig2,
    ])
    return


@app.cell
def _(cost, income, levels, mo, time_to_level):
    mid = len(levels) // 2
    mo.md(f"""### Summary

| Metric | Level 1 | Level {levels[mid]} | Level {levels[-1]} |
|---|---|---|---|
| XP Cost | {cost[0]:,.0f} | {cost[mid]:,.0f} | {cost[-1]:,.0f} |
| Income | {income[0]:,.1f} | {income[mid]:,.1f} | {income[-1]:,.1f} |
| Time per Level | {time_to_level[0]:,.1f} | {time_to_level[mid]:,.1f} | {time_to_level[-1]:,.1f} |
| Cost ratio (last/first) | | | {cost[-1]/cost[0]:,.0f}x |
| Time ratio (last/first) | | | {time_to_level[-1]/time_to_level[0]:,.1f}x |

**Reference points:** Pokemon uses exponent 3 (cubic). Civ 6 uses ~1.5. D&D 5e uses ~2 (quadratic). Factorio infinite research uses exponential (1.5^level) matched against exponential income growth.
""")
    return


if __name__ == "__main__":
    app.run()
