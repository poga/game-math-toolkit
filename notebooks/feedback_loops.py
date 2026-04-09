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
    ats_imp_rate = mo.ui.slider(start=0.05, stop=0.50, step=0.01, value=0.255,
                                 show_value=True, label="AtS: Impatience rate / tick")
    ats_rep_rate = mo.ui.slider(start=0.02, stop=0.20, step=0.01, value=0.08,
                                 show_value=True, label="AtS: Rep event chance / tick")
    ats_drain = mo.ui.slider(start=0.0, stop=3.0, step=0.1, value=1.0,
                              show_value=True, label="AtS: Impatience drain per rep")
    hades_hl = mo.ui.slider(start=0, stop=5, step=1, value=3,
                             show_value=True, label="Hades: Hard Labor ranks")
    hades_lc = mo.ui.slider(start=0, stop=4, step=1, value=2,
                             show_value=True, label="Hades: Lasting Consequences ranks")
    mk_catch_up = mo.ui.slider(start=0.0, stop=0.5, step=0.05, value=0.3,
                                show_value=True, label="MK: Catch-up strength")
    mo.vstack([
        mo.md("## How Feedback Loops Shape the Arc of a Run"),
        mo.md("Three feedback loop designs from shipped games. Each creates a different emotional arc — tightening vice, controlled risk, or rubber band."),
        mo.md("---"),
        mo.md("**Against the Storm** — Reputation vs Impatience race. Each rep gain drains impatience (coupled positive + negative)."),
        mo.hstack([ats_imp_rate, ats_rep_rate, ats_drain]),
        mo.md("**Hades Heat** — Player selects difficulty. Hard Labor = +20% damage/rank. Lasting Consequences = -25% healing/rank."),
        mo.hstack([hades_hl, hades_lc]),
        mo.md("**Mario Kart** — Last place gets best items. Automatic rubber band."),
        mk_catch_up,
    ])
    return (ats_imp_rate, ats_rep_rate, ats_drain,
            hades_hl, hades_lc, mk_catch_up)


@app.cell
def _(ats_imp_rate, ats_rep_rate, ats_drain,
      hades_hl, hades_lc, mk_catch_up, np):
    _rng = np.random.default_rng(42)

    # --- Against the Storm: dual-bar race ---
    _ats_n = 200
    _ats_imp_max = 14.0
    _ats_rep_max = 15.0
    ats_imp = np.zeros(_ats_n)
    ats_rep = np.zeros(_ats_n)
    _i, _r = 0.0, 0.0
    _done = False
    for _t in range(_ats_n):
        if not _done:
            _i += ats_imp_rate.value
            if _rng.random() < ats_rep_rate.value:
                _r += 1.0
                _i = max(0, _i - ats_drain.value)
            if _i >= _ats_imp_max or _r >= _ats_rep_max:
                _done = True
        ats_imp[_t] = min(_i, _ats_imp_max)
        ats_rep[_t] = min(_r, _ats_rep_max)
    ats_tension = ats_imp / _ats_imp_max

    # --- Hades: player-controlled difficulty ---
    _hades_n = 40
    _max_hp = 200.0
    _base_dmg = 25.0
    _base_heal = 30.0
    _dmg_m = 1 + 0.20 * hades_hl.value
    _heal_m = max(0.0, 1 - 0.25 * hades_lc.value)
    _hp = _max_hp
    hades_hp = np.zeros(_hades_n)
    for _rm in range(_hades_n):
        _hp -= _base_dmg * _dmg_m * _rng.uniform(0.5, 1.5)
        if _rm % 4 == 3:
            _hp = min(_max_hp, _hp + _base_heal * _heal_m)
        _hp = max(0, _hp)
        hades_hp[_rm] = _hp
    hades_tension = 1 - hades_hp / _max_hp

    # --- Mario Kart: catch-up ---
    _mk_laps = 30
    _mk_n = 8
    _base_spd = np.linspace(0.8, 1.2, _mk_n)
    _dist = np.linspace(0, 0.01, _mk_n)
    mk_positions = np.zeros((_mk_laps, _mk_n))
    for _lap in range(_mk_laps):
        _ord = np.argsort(-_dist)
        _pos = np.empty_like(_ord)
        _pos[_ord] = np.arange(1, _mk_n + 1)
        _boost = mk_catch_up.value * (_pos - 1) / (_mk_n - 1)
        _dist += _base_spd + _rng.normal(0, 0.15, _mk_n) + _boost
        mk_positions[_lap] = _pos
    mk_tension = (mk_positions[:, 0] - 1) / (_mk_n - 1)

    return (ats_tension, ats_imp, ats_rep,
            hades_tension, hades_hp,
            mk_tension, mk_positions)


@app.cell
def _(ats_tension, hades_tension, mk_tension, go, mo, np):
    _ats_x = np.linspace(0, 1, len(ats_tension))
    _hades_x = np.linspace(0, 1, len(hades_tension))
    _mk_x = np.linspace(0, 1, len(mk_tension))
    _fig = go.Figure()
    _fig.add_trace(go.Scatter(x=_ats_x, y=ats_tension,
                               name="Against the Storm (vice)",
                               line=dict(color="#636EFA", width=2)))
    _fig.add_trace(go.Scatter(x=_hades_x, y=hades_tension,
                               name="Hades (knife's edge)",
                               line=dict(color="#EF553B", width=2)))
    _fig.add_trace(go.Scatter(x=_mk_x, y=mk_tension,
                               name="Mario Kart (rubber band)",
                               line=dict(color="#00CC96", width=2)))
    _fig.add_hline(y=1.0, line_dash="dash", line_color="red",
                    annotation_text="Game over / death / last place")
    _fig.update_layout(
        title="Tension Curve — The Emotional Arc of a Run",
        xaxis_title="Run progress (0 = start, 1 = end)",
        yaxis_title="Tension (0 = safe, 1 = danger)",
        hovermode="x unified",
        yaxis_range=[-0.05, 1.1],
    )
    mo.vstack([
        mo.md("### Tension Curve — The Feel Chart"),
        mo.md("Three games, three emotional arcs. Against the Storm: steady rise (vice tightens). Hades: spiky with healing dips (controlled risk). Mario Kart: oscillating (rubber band)."),
        _fig,
    ])
    return


@app.cell
def _(ats_imp, ats_rep, go, mo, np):
    _t = np.arange(len(ats_imp))
    _fig = go.Figure()
    _fig.add_trace(go.Scatter(x=_t, y=ats_rep, name="Reputation",
                               line=dict(color="#00CC96", width=2)))
    _fig.add_trace(go.Scatter(x=_t, y=ats_imp, name="Impatience",
                               line=dict(color="#EF553B", width=2)))
    _fig.add_hline(y=15, line_dash="dot", line_color="#00CC96",
                    annotation_text="Rep target (15)")
    _fig.add_hline(y=14, line_dash="dot", line_color="#EF553B",
                    annotation_text="Impatience max (14)")
    _fig.update_layout(
        title="Against the Storm — The Dual-Bar Race",
        xaxis_title="Tick",
        yaxis_title="Bar value",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Against the Storm — Reputation vs Impatience"),
        mo.md("Fill the green bar before the red bar fills. Each reputation gain also **drains** impatience — that coupling is the entire design. Strong drain → winning cascades. Weak drain → knife fight."),
        _fig,
    ])
    return


@app.cell
def _(hades_hp, hades_hl, hades_lc, go, mo, np):
    _rooms = np.arange(1, len(hades_hp) + 1)
    _fig = go.Figure()
    _fig.add_trace(go.Scatter(x=_rooms, y=hades_hp, name="HP",
                               line=dict(color="#EF553B", width=2),
                               fill="tozeroy",
                               fillcolor="rgba(239,85,59,0.2)"))
    _fig.add_hline(y=0, line_dash="dash", line_color="red",
                    annotation_text="Death")
    _fig.update_layout(
        title=f"Hades — HP Over 40 Rooms (Hard Labor {hades_hl.value}, "
              f"Lasting Consequences {hades_lc.value})",
        xaxis_title="Room",
        yaxis_title="HP",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Hades — Player-Controlled Tension"),
        mo.md(f"Hard Labor: +{hades_hl.value * 20}% damage. "
              f"Lasting Consequences: -{hades_lc.value * 25}% healing. "
              f"The player **chose** this difficulty. Move sliders to see "
              f"how Heat shifts the HP trajectory."),
        _fig,
    ])
    return


@app.cell
def _(mk_positions, mk_catch_up, go, mo, np):
    _laps = np.arange(1, mk_positions.shape[0] + 1)
    _n = mk_positions.shape[1]
    _colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA",
               "#FFA15A", "#19D3F3", "#FF6692", "#B6E880"]
    _fig = go.Figure()
    for _p in range(_n):
        _fig.add_trace(go.Scatter(
            x=_laps, y=mk_positions[:, _p],
            name=f"P{_p+1} (spd {0.8 + 0.4*_p/(_n-1):.2f})",
            line=dict(color=_colors[_p % len(_colors)], width=1.5),
        ))
    _fig.update_layout(
        title=f"Mario Kart — Positions Over Time "
              f"(catch-up={mk_catch_up.value:.2f})",
        xaxis_title="Lap",
        yaxis_title="Position (1 = first)",
        yaxis_autorange="reversed",
        hovermode="x unified",
    )
    _label = ("cluster (rubber band works)" if mk_catch_up.value > 0.1
              else "spread apart (no rubber band)")
    mo.vstack([
        mo.md("### Mario Kart — Catch-Up in Action"),
        mo.md(f"With catch-up at **{mk_catch_up.value:.2f}**, positions "
              f"{_label}. Set catch-up to 0 to see the fastest player dominate."),
        _fig,
    ])
    return


@app.cell
def _(ats_tension, ats_imp, ats_rep, hades_tension, hades_hp,
      mk_tension, mk_positions, mo, np):
    # Against the Storm outcome
    _win = np.any(ats_rep >= 15)
    _lose = np.any(ats_imp >= 14)
    _win_t = int(np.argmax(ats_rep >= 15)) if _win else None
    _lose_t = int(np.argmax(ats_imp >= 14)) if _lose else None
    if _win and (_lose_t is None or _win_t <= _lose_t):
        _ats_out = f"Win at tick {_win_t}"
    elif _lose:
        _ats_out = f"Lose at tick {_lose_t}"
    else:
        _ats_out = "Ongoing"

    # Hades outcome
    _dead = np.any(hades_hp <= 0)
    if _dead:
        _hades_out = f"Died room {int(np.argmax(hades_hp <= 0)) + 1}"
    else:
        _hades_out = f"Survived (min HP: {np.min(hades_hp):.0f})"

    # Tension trend
    def _trend(arr):
        _h = len(arr) // 2
        _d = np.mean(arr[_h:]) - np.mean(arr[:_h])
        if _d > 0.15:
            return "Rising (tightening)"
        elif _d < -0.15:
            return "Falling (easing)"
        elif np.std(arr[_h:]) > 0.15:
            return "Oscillating (rubber band)"
        return "Stable"

    mo.md(f"""### Summary

| Metric | Against the Storm | Hades | Mario Kart |
|---|---|---|---|
| Loop type | Coupled positive + negative | Player-controlled negative | Automatic catch-up |
| Tension shape | {_trend(ats_tension)} | {_trend(hades_tension)} | {_trend(mk_tension)} |
| Outcome | {_ats_out} | {_hades_out} | Weakest finished P{int(mk_positions[-1, 0])} |
| Peak tension | {np.max(ats_tension):.2f} | {np.max(hades_tension):.2f} | {np.max(mk_tension):.2f} |

**Design insight:**
- **Against the Storm:** The coupling (rep drains impatience) is the entire design. Real values: impatience +0.255/min, each rep gain drains 1.0 impatience. Strong drain → winning cascades. Weak drain → grinding race.
- **Hades:** Difficulty is opt-in. Max Heat = 63 across 15 pact conditions. Hard Labor (+20%/rank, 5 ranks) and Lasting Consequences (-25% healing/rank, 4 ranks) are highest-impact. The player chooses their own tension curve.
- **Mario Kart:** `item_quality = max_quality * (1 - position/total)`. Last place gets the best items with certainty. Simple, predictable, exploitable by design.
""")
    return


if __name__ == "__main__":
    app.run()
