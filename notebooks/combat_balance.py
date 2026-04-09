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
    base_damage = mo.ui.slider(start=10, stop=60, step=5, value=30,
                                show_value=True, label="Base damage")
    k = mo.ui.slider(start=5, stop=50, step=1, value=25,
                      show_value=True, label="Scaling factor (k)")
    defender_hp = mo.ui.slider(start=50, stop=200, step=10, value=100,
                                show_value=True, label="Defender HP")
    mo.vstack([
        mo.md("## Combat Balance — Stat Gap Impact"),
        mo.md("Exponential difference model: `damage = base * e^(delta/k)`. Each `k*ln(2)` points of advantage doubles damage. Civ 6 uses base=30, k=25."),
        mo.hstack([base_damage, k]),
        defender_hp,
    ])
    return base_damage, defender_hp, k


@app.cell
def _(base_damage, k, np):
    delta = np.linspace(-30, 30, 200)
    damage = base_damage.value * np.exp(delta / k.value)
    damage_multiplier = np.exp(delta / k.value)
    doubling_point = k.value * np.log(2)
    return damage, damage_multiplier, delta, doubling_point


@app.cell
def _(damage_multiplier, delta, doubling_point, go, k, mo):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=delta, y=damage_multiplier, name="Damage multiplier",
                              line=dict(color="#EF553B", width=3)))
    fig.add_hline(y=1.0, line_dash="dash", line_color="gray",
                   annotation_text="Equal strength")
    fig.add_hline(y=2.0, line_dash="dot", line_color="orange",
                   annotation_text="2x damage")
    fig.add_hline(y=0.5, line_dash="dot", line_color="blue",
                   annotation_text="0.5x damage")
    fig.add_vline(x=doubling_point, line_dash="dash", line_color="orange",
                   annotation_text=f"+{doubling_point:.1f} = 2x")
    fig.add_vline(x=-doubling_point, line_dash="dash", line_color="blue",
                   annotation_text=f"-{doubling_point:.1f} = 0.5x")
    fig.update_layout(
        title="Damage Multiplier vs Stat Gap",
        xaxis_title="Stat advantage (attacker - defender)",
        yaxis_title="Damage multiplier",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Damage Curve"),
        mo.md(f"With k={k.value}, damage doubles every **{doubling_point:.1f}** stat points. Positive = attacker advantage, negative = defender advantage."),
        fig,
    ])
    return


@app.cell
def _(base_damage, damage, defender_hp, delta, go, mo, np):
    hits_to_kill = np.ceil(defender_hp.value / damage)
    _fig2 = go.Figure()
    _fig2.add_trace(go.Scatter(x=delta, y=hits_to_kill, name="Hits to kill",
                               line=dict(color="#AB63FA", width=3)))
    trivial_idx = np.argmax(hits_to_kill <= 1)
    trivial_delta = delta[trivial_idx] if hits_to_kill[trivial_idx] <= 1 else None
    _fig2.update_layout(
        title=f"Hits to Kill ({defender_hp.value} HP defender)",
        xaxis_title="Stat advantage",
        yaxis_title="Hits needed",
        hovermode="x unified",
    )
    if trivial_delta is not None:
        _fig2.add_vline(x=trivial_delta, line_dash="dash", line_color="red",
                        annotation_text=f"One-shot at +{trivial_delta:.0f}")
    _equal_hits = np.ceil(defender_hp.value / base_damage.value)
    mo.vstack([
        mo.md("### Hits to Kill — When Combat Becomes Trivial"),
        mo.md(f"At equal strength: **{_equal_hits:.0f} hits** to kill. " +
              (f"One-shot threshold: **+{trivial_delta:.0f}** stat advantage." if trivial_delta is not None else "No one-shot possible in this range.")),
        _fig2,
    ])
    return


@app.cell
def _(base_damage, doubling_point, k, mo, np):
    _gaps = [0, 5, 10, 15, 20, 25, 30]
    _rows = "\n".join(
        f"| +{g} | {np.exp(g/k.value):.2f}x | {base_damage.value * np.exp(g/k.value):.0f} | {base_damage.value * np.exp(-g/k.value):.0f} |"
        for g in _gaps
    )
    mo.md(f"""### Reference Table

| Stat gap | Damage multiplier | Damage dealt | Damage taken |
|---|---|---|---|
{_rows}

**Design levers:**
- Lower k → each stat point matters more (steep curve, snowbally)
- Higher k → stat points matter less (flat curve, forgiving)
- k={k.value} means doubling point is +{doubling_point:.1f} stats
- Civ 6 uses k=25, base=30. Modifiers: flanking +2, Great General +5, Corps +10, Army +17.
""")
    return


if __name__ == "__main__":
    app.run()
