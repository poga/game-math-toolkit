# Proven Formulas Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite all 5 Marimo notebooks from generic explorations into feel-comparison tools anchored on proven, shipped game formulas.

**Architecture:** Each notebook shows 3-5 real formulas side by side. The primary chart is always the "feel" metric (what the player experiences), not the raw math. Sliders control shared parameters for fair comparison. All formulas come from `game-math-case-studies.md`.

**Tech Stack:** Python, Marimo, NumPy, Plotly

**All 5 tasks are independent and can be executed in parallel.**

---

### Task 1: Rewrite progression.py — "How Leveling Feels Across Real Games"

**Files:**
- Modify: `notebooks/progression.py`

**Formulas:** OSRS (quarter-exponential sum), Pokemon Medium Fast (cubic), D&D 5e (quadratic), Civ 6 population (n^1.5 polynomial)

- [ ] **Step 1: Write the notebook**

Write the complete notebook to `notebooks/progression.py`:

```python
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
```

- [ ] **Step 2: Verify notebook compiles**

Run: `uv run python -c "import py_compile; py_compile.compile('notebooks/progression.py', doraise=True)"`

Expected: no output (success)

- [ ] **Step 3: Commit**

```bash
git add notebooks/progression.py
git commit -m "Rewrite progression notebook: OSRS, Pokemon, D&D, Civ 6 XP feel comparison"
```

---

### Task 2: Rewrite combat_balance.py — "How Stat Gaps Decide Fights"

**Files:**
- Modify: `notebooks/combat_balance.py`

**Formulas:** Civ 6 (exponential difference), LoL armor (hyperbolic), Civ 5 (ratio model)

- [ ] **Step 1: Write the notebook**

Write the complete notebook to `notebooks/combat_balance.py`:

```python
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
```

- [ ] **Step 2: Verify notebook compiles**

Run: `uv run python -c "import py_compile; py_compile.compile('notebooks/combat_balance.py', doraise=True)"`

Expected: no output (success)

- [ ] **Step 3: Commit**

```bash
git add notebooks/combat_balance.py
git commit -m "Rewrite combat notebook: Civ 6, Civ 5, LoL damage model feel comparison"
```

---

### Task 3: Rewrite market_pricing.py — "How Markets Stay Stable (or Don't)"

**Files:**
- Modify: `notebooks/market_pricing.py`

**Formulas:** Victoria 3 bounded elastic, unbounded linear, logarithmic dampening

- [ ] **Step 1: Write the notebook**

Write the complete notebook to `notebooks/market_pricing.py`:

```python
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
```

- [ ] **Step 2: Verify notebook compiles**

Run: `uv run python -c "import py_compile; py_compile.compile('notebooks/market_pricing.py', doraise=True)"`

Expected: no output (success)

- [ ] **Step 3: Commit**

```bash
git add notebooks/market_pricing.py
git commit -m "Rewrite market notebook: Victoria 3 bounded vs unbounded vs logarithmic pricing"
```

---

### Task 4: Rewrite roguelike_variance.py — "How Drop Systems Shape Run Outcomes"

**Files:**
- Modify: `notebooks/roguelike_variance.py`

**Formulas:** Dota 2 PRD (real C constants), true random (control), Slay the Spire-style aggressive pity

- [ ] **Step 1: Write the notebook**

Write the complete notebook to `notebooks/roguelike_variance.py`:

```python
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
```

- [ ] **Step 2: Verify notebook compiles**

Run: `uv run python -c "import py_compile; py_compile.compile('notebooks/roguelike_variance.py', doraise=True)"`

Expected: no output (success)

- [ ] **Step 3: Commit**

```bash
git add notebooks/roguelike_variance.py
git commit -m "Rewrite variance notebook: Dota 2 PRD, true random, StS pity feel comparison"
```

---

### Task 5: Create feedback_loops.py, delete economy_flow.py

**Files:**
- Create: `notebooks/feedback_loops.py`
- Delete: `notebooks/economy_flow.py`

**Systems:** Against the Storm (coupled dual-bar), Hades Heat (player-controlled negative), Mario Kart (automatic catch-up)

- [ ] **Step 1: Write the notebook**

Write the complete notebook to `notebooks/feedback_loops.py`:

```python
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
```

- [ ] **Step 2: Delete economy_flow.py**

```bash
git rm notebooks/economy_flow.py
```

- [ ] **Step 3: Verify notebook compiles**

Run: `uv run python -c "import py_compile; py_compile.compile('notebooks/feedback_loops.py', doraise=True)"`

Expected: no output (success)

- [ ] **Step 4: Commit**

```bash
git add notebooks/feedback_loops.py
git commit -m "Replace economy notebook with feedback loops: AtS, Hades, Mario Kart feel comparison"
```
