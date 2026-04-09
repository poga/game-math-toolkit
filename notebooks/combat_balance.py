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
    max_gap = mo.ui.slider(start=10, stop=50, step=5, value=30,
                            show_value=True, label="Max stat gap")
    defender_hp = mo.ui.slider(start=50, stop=300, step=10, value=100,
                                show_value=True, label="Defender HP")
    base_damage = mo.ui.slider(start=10, stop=60, step=5, value=30,
                                show_value=True, label="Base damage")
    base_strength = mo.ui.slider(start=20, stop=100, step=5, value=50,
                                  show_value=True, label="Base strength (Civ 5)")
    base_armor = mo.ui.slider(start=50, stop=200, step=10, value=100,
                               show_value=True, label="Base armor (LoL)")
    mo.vstack([
        mo.md("## How Stat Gaps Decide Fights"),
        mo.md("Three combat models from shipped games. Same stat gap, different math, dramatically different feel. The **damage multiplier** chart shows how quickly a lead becomes a stomp."),
        mo.hstack([max_gap, defender_hp, base_damage]),
        mo.hstack([base_strength, base_armor]),
    ])
    return (max_gap, defender_hp, base_damage, base_strength, base_armor)


@app.cell
def _(max_gap, base_damage, base_strength, base_armor, np):
    delta = np.linspace(-max_gap.value, max_gap.value, 300)

    # Civ 6: exponential difference — damage = base * e^(Δ/25)
    civ6_mult = np.exp(delta / 25)

    # Civ 5: ratio model — R = (base + Δ) / base
    _R = (base_strength.value + delta) / base_strength.value
    civ5_mult = (((_R + 3) / 4) ** 4 + 1) / 2

    # LoL: hyperbolic armor — effective_armor = base_armor - Δ
    _eff = base_armor.value - delta
    _lol_raw = 100 / np.maximum(1, 100 + _eff)
    _lol_base = 100 / (100 + base_armor.value)
    lol_mult = _lol_raw / _lol_base

    # Absolute damage for hits-to-kill
    civ6_damage = base_damage.value * civ6_mult
    civ5_damage = base_damage.value * civ5_mult
    lol_damage = base_damage.value * lol_mult

    return (delta, civ6_mult, civ5_mult, lol_mult,
            civ6_damage, civ5_damage, lol_damage)


@app.cell
def _(delta, civ6_mult, civ5_mult, lol_mult, go, mo):
    _fig = go.Figure()
    _fig.add_trace(go.Scatter(x=delta, y=civ6_mult, name="Civ 6 (exponential)",
                               line=dict(color="#636EFA", width=3)))
    _fig.add_trace(go.Scatter(x=delta, y=civ5_mult, name="Civ 5 (ratio)",
                               line=dict(color="#00CC96", width=2)))
    _fig.add_trace(go.Scatter(x=delta, y=lol_mult, name="LoL (hyperbolic)",
                               line=dict(color="#EF553B", width=2)))
    _fig.add_hline(y=1.0, line_dash="dash", line_color="gray",
                    annotation_text="Equal strength")
    _fig.add_hline(y=2.0, line_dash="dot", line_color="orange",
                    annotation_text="2x damage (stomp threshold)")
    _fig.update_layout(
        title="Damage Multiplier vs Stat Gap — How Fast a Lead Becomes a Stomp",
        xaxis_title="Stat advantage (attacker - defender)",
        yaxis_title="Damage multiplier (1.0 = equal)",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Damage Curve — The Feel Chart"),
        mo.md("Civ 6's exponential punishes stat gaps hard. LoL's hyperbolic stays forgiving. Civ 5 is in between. The 2x line is where fights stop being competitive."),
        _fig,
    ])
    return


@app.cell
def _(delta, civ6_damage, civ5_damage, lol_damage, defender_hp, go, mo, np):
    _hp = defender_hp.value
    _civ6_htk = np.ceil(_hp / civ6_damage)
    _civ5_htk = np.ceil(_hp / civ5_damage)
    _lol_htk = np.ceil(_hp / lol_damage)
    _fig = go.Figure()
    _fig.add_trace(go.Scatter(x=delta, y=_civ6_htk, name="Civ 6",
                               line=dict(color="#636EFA", width=2)))
    _fig.add_trace(go.Scatter(x=delta, y=_civ5_htk, name="Civ 5",
                               line=dict(color="#00CC96", width=2)))
    _fig.add_trace(go.Scatter(x=delta, y=_lol_htk, name="LoL",
                               line=dict(color="#EF553B", width=2)))
    _fig.add_hline(y=1, line_dash="dash", line_color="red",
                    annotation_text="One-shot kill")
    _fig.update_layout(
        title=f"Hits to Kill ({_hp} HP Defender)",
        xaxis_title="Stat advantage",
        yaxis_title="Hits needed",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Hits to Kill — When Combat Becomes Trivial"),
        mo.md("Fewer hits = faster kills. The gap between curves shows which model is more snowbally. Civ 6 reaches one-shot territory fastest."),
        _fig,
    ])
    return


@app.cell
def _(delta, civ6_mult, civ5_mult, lol_mult, base_damage, defender_hp,
      max_gap, mo, np):
    def _threshold(mult_arr, target):
        _mask = mult_arr >= target
        if np.any(_mask):
            return f"+{delta[_mask][0]:.0f}"
        return f"> +{max_gap.value}"

    def _oneshot(mult_arr):
        _hits = np.ceil(defender_hp.value / (base_damage.value * mult_arr))
        _mask = _hits <= 1
        if np.any(_mask):
            return f"+{delta[_mask][0]:.0f}"
        return f"> +{max_gap.value}"

    _civ6_dbl = 25 * np.log(2)

    mo.md(f"""### Summary

| Metric | Civ 6 | Civ 5 | LoL |
|---|---|---|---|
| 2x damage at | +{_civ6_dbl:.1f} | {_threshold(civ5_mult, 2.0)} | {_threshold(lol_mult, 2.0)} |
| One-shot at | {_oneshot(civ6_mult)} | {_oneshot(civ5_mult)} | {_oneshot(lol_mult)} |
| Comeback zone (mult < 2x) | up to +{_civ6_dbl:.0f} | up to {_threshold(civ5_mult, 2.0)} | up to {_threshold(lol_mult, 2.0)} |

**Formulas:**
- **Civ 6:** `damage = 30 * e^(delta/25)` — exponential difference. Damage doubles every {_civ6_dbl:.1f} points. Flanking +2, General +5, Corps +10, Army +17.
- **Civ 5:** `damage = 30 * ((((R+3)/4)^4 + 1) / 2)` where R = attacker/defender — ratio model, smoother at extremes.
- **LoL:** `reduction = armor / (armor + 100)` — hyperbolic. Each point of armor adds equal effective HP. k=100 is the half-effectiveness point.

**Design insight:** Pick exponential (Civ 6) when stat gaps should snowball. Pick hyperbolic (LoL) when you want items to always matter equally. Pick ratio (Civ 5) for a middle ground.
""")
    return


if __name__ == "__main__":
    app.run()
