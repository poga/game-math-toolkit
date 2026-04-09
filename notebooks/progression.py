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
    max_level = mo.ui.slider(start=20, stop=99, step=1, value=99,
                              show_value=True, label="Max level")
    income_exp = mo.ui.slider(start=0.0, stop=1.5, step=0.1, value=0.5,
                               show_value=True, label="Income growth exponent")
    mo.vstack([
        mo.md("## How Leveling Feels Across Real Games"),
        mo.md("Four proven XP formulas from shipped games. The **time-per-level** chart shows what the player actually experiences — not the raw math, but the grind."),
        mo.hstack([max_level, income_exp]),
    ])
    return (max_level, income_exp)


@app.cell
def _(max_level, income_exp, np):
    max_lvl = max_level.value
    levels = np.arange(2, max_lvl + 1, dtype=float)

    # OSRS: XP(L) = floor(sum_{x=1}^{L-1} floor(x + 300 * 2^(x/7)) / 4)
    _osrs_cum = np.zeros(max_lvl + 1)
    _running = 0.0
    for _x in range(1, max_lvl):
        _running += np.floor(_x + 300 * 2 ** (_x / 7))
        _osrs_cum[_x + 1] = np.floor(_running / 4)
    osrs_cost = np.diff(_osrs_cum)[1:]

    # Pokemon Medium Fast: cumulative = L^3
    _all = np.arange(0, max_lvl + 1, dtype=float)
    pokemon_cost = np.diff(_all ** 3)[1:]

    # D&D 5e: cumulative ≈ 500 * L * (L - 1)
    dnd_cost = np.diff(500 * _all * (_all - 1))[1:]

    # Civ 6 population: food(n) = 15 + 8*(n-1) + (n-1)^1.5
    civ6_cost = 15 + 8 * (levels - 1) + (levels - 1) ** 1.5

    # Shared income model for fair comparison
    _income = levels ** income_exp.value

    # Time per level = cost / income, normalized so first level = 1.0
    def _norm(cost):
        t = cost / _income
        return t / t[0] if t[0] > 0 else t

    osrs_time = _norm(osrs_cost)
    pokemon_time = _norm(pokemon_cost)
    dnd_time = _norm(dnd_cost)
    civ6_time = _norm(civ6_cost)

    return (levels, max_lvl, osrs_cost, pokemon_cost, dnd_cost, civ6_cost,
            osrs_time, pokemon_time, dnd_time, civ6_time)


@app.cell
def _(levels, osrs_time, pokemon_time, dnd_time, civ6_time, go, mo):
    _fig = go.Figure()
    _fig.add_trace(go.Scatter(x=levels, y=osrs_time, name="OSRS (quarter-exponential)",
                               line=dict(color="#EF553B", width=3)))
    _fig.add_trace(go.Scatter(x=levels, y=pokemon_time, name="Pokemon (cubic)",
                               line=dict(color="#636EFA", width=2)))
    _fig.add_trace(go.Scatter(x=levels, y=dnd_time, name="D&D 5e (quadratic)",
                               line=dict(color="#00CC96", width=2)))
    _fig.add_trace(go.Scatter(x=levels, y=civ6_time, name="Civ 6 pop (n^1.5)",
                               line=dict(color="#AB63FA", width=2)))
    _fig.update_layout(
        title="Time per Level (Normalized) — What the Player Feels",
        xaxis_title="Level",
        yaxis_title="Relative time (level 2 = 1.0)",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Time per Level — The Curve That Matters"),
        mo.md("All curves share the same income growth. Differences come entirely from the XP formula. Higher = more grind at that level. OSRS's exponential tail dwarfs everything else."),
        _fig,
    ])
    return


@app.cell
def _(levels, osrs_cost, pokemon_cost, dnd_cost, civ6_cost, go, mo):
    _fig = go.Figure()
    _fig.add_trace(go.Scatter(x=levels, y=osrs_cost, name="OSRS",
                               line=dict(color="#EF553B")))
    _fig.add_trace(go.Scatter(x=levels, y=pokemon_cost, name="Pokemon",
                               line=dict(color="#636EFA")))
    _fig.add_trace(go.Scatter(x=levels, y=dnd_cost, name="D&D 5e",
                               line=dict(color="#00CC96")))
    _fig.add_trace(go.Scatter(x=levels, y=civ6_cost, name="Civ 6",
                               line=dict(color="#AB63FA")))
    _fig.update_layout(
        title="Raw XP Cost per Level (Log Scale)",
        xaxis_title="Level",
        yaxis_title="XP cost per level",
        yaxis_type="log",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Raw Cost Curves"),
        mo.md("Log scale reveals the growth rate. Straight line on log scale = exponential growth. OSRS curves upward even on log scale — it's super-exponential."),
        _fig,
    ])
    return


@app.cell
def _(levels, max_lvl, osrs_cost, pokemon_cost, dnd_cost, civ6_cost,
      osrs_time, pokemon_time, dnd_time, civ6_time, mo, np):
    def _grind(time_arr):
        n = max(1, len(time_arr) // 10)
        return np.mean(time_arr[-n:]) / np.mean(time_arr[:n])

    def _inflection(time_arr):
        idx = np.argmax(time_arr > 2.0)
        return str(int(levels[idx])) if time_arr[idx] > 2.0 else "never"

    mo.md(f"""### Summary

| Metric | OSRS | Pokemon | D&D 5e | Civ 6 |
|---|---|---|---|---|
| Total XP to level {max_lvl} | {np.sum(osrs_cost):,.0f} | {np.sum(pokemon_cost):,.0f} | {np.sum(dnd_cost):,.0f} | {np.sum(civ6_cost):,.0f} |
| Grind ratio (last 10% / first 10%) | {_grind(osrs_time):.1f}x | {_grind(pokemon_time):.1f}x | {_grind(dnd_time):.1f}x | {_grind(civ6_time):.1f}x |
| Level where grind > 2x baseline | {_inflection(osrs_time)} | {_inflection(pokemon_time)} | {_inflection(dnd_time)} | {_inflection(civ6_time)} |

**Key insight:** OSRS level 92 is exactly 50% of the total XP to 99 — half the entire grind is in the last 7 levels. This is the quarter-exponential in action.

**Formulas:**
- **OSRS:** `XP(L) = floor(sum(floor(x + 300 * 2^(x/7)) / 4) for x=1..L-1)` — exponential sum, steepest endgame
- **Pokemon Medium Fast:** `XP(L) = L^3` — clean cubic, 1M XP to level 100
- **D&D 5e:** `XP(L) ≈ 500 * L * (L-1)` — quadratic, gentler because each level carries more weight
- **Civ 6 pop:** `food(n) = 15 + 8*(n-1) + (n-1)^1.5` — super-linear, keeps cities growing without stalling
""")
    return


if __name__ == "__main__":
    app.run()
