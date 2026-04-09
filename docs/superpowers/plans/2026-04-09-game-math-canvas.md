# Game Math Toolkit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a documentation-driven game math toolkit: CLAUDE.md guide + 5 Marimo example notebooks + project setup. No custom Python library.

**Architecture:** Marimo reactive notebooks for interactive exploration. NumPy for math, Plotly for charts. CLAUDE.md teaches Claude Code how to generate game-specific notebooks from designer requests. Example notebooks serve as both templates and working tools.

**Tech Stack:** Python 3.10+, uv (package manager), Marimo (reactive notebooks), NumPy, Plotly

---

## File Structure

```
game-math-toolkit/
  .gitignore                  # Create: ignore .venv, __pycache__, .marimo
  pyproject.toml              # Create: project metadata + dependencies
  setup.sh                    # Create: one-command environment setup
  CLAUDE.md                   # Create: guide for Claude Code
  notebooks/
    progression.py            # Create: XP curve shaping notebook
    economy_flow.py           # Create: source/pool/drain simulation
    combat_balance.py         # Create: stat gap impact
    roguelike_variance.py     # Create: Monte Carlo run distribution
    market_pricing.py         # Create: bounded elastic pricing
  game-math-toolkit.md        # Existing: math reference (no changes)
  game-math-case-studies.md   # Existing: case studies (no changes)
```

---

### Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `setup.sh`
- Create: `.gitignore`

- [ ] **Step 1: Create `.gitignore`**

```gitignore
.venv/
__pycache__/
*.pyc
.marimo/
```

- [ ] **Step 2: Create `pyproject.toml`**

```toml
[project]
name = "game-math-toolkit"
version = "0.1.0"
description = "Interactive game systems math toolkit — Marimo notebooks for progression, economy, combat, and probability design"
requires-python = ">=3.10"
dependencies = [
    "marimo>=0.9.0",
    "numpy>=1.24.0",
    "plotly>=5.18.0",
]
```

- [ ] **Step 3: Create `setup.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    echo "Error: uv not found."
    echo "Install it with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

uv sync

echo ""
echo "Setup complete! Try an example notebook:"
echo "  uv run marimo edit notebooks/progression.py"
```

- [ ] **Step 4: Make `setup.sh` executable and run it**

Run: `chmod +x setup.sh && ./setup.sh`
Expected: uv creates `.venv/`, installs marimo, numpy, plotly. Prints success message.

- [ ] **Step 5: Verify marimo runs**

Run: `uv run marimo --version`
Expected: prints marimo version number.

- [ ] **Step 6: Commit**

```bash
git add .gitignore pyproject.toml setup.sh uv.lock
git commit -m "Add project setup: pyproject.toml, setup.sh, .gitignore"
```

---

### Task 2: CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Create `CLAUDE.md`**

```markdown
# Game Math Toolkit

You are a game systems design assistant. When the designer asks about progression, economy, combat balance, or randomness, create a Marimo notebook that lets them explore the answer interactively.

## Setup

- Package manager: `uv`
- Run notebooks: `uv run marimo edit notebooks/<name>.py`
- Add dependencies: `uv add <package>`

## Creating Notebooks

When a designer asks a game math question, create a Marimo `.py` notebook in `notebooks/`.

### Marimo Notebook Format

Marimo notebooks are `.py` files. Each cell is a function decorated with `@app.cell`. Cells declare dependencies via function arguments; Marimo infers the execution DAG automatically.

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
    my_slider = mo.ui.slider(start=1.0, stop=3.0, step=0.1, value=1.8,
                              show_value=True, label="My parameter")
    my_slider
    return (my_slider,)


@app.cell
def _(my_slider, np, go):
    x = np.arange(1, 101)
    y = x ** my_slider.value
    fig = go.Figure(data=[go.Scatter(x=x, y=y, mode="lines")])
    fig.update_layout(title=f"x^{my_slider.value}")
    fig
    return


if __name__ == "__main__":
    app.run()
```

Rules:
- Function names are always `_`
- Arguments declare which variables this cell reads (from other cells' returns)
- Return a tuple of variables this cell exports: `return (var1, var2)`
- Use bare `return` if the cell exports nothing (display-only cells)
- The last expression in a cell is displayed as output
- Use `mo.vstack([...])` or `mo.hstack([...])` to display multiple items
- Use `mo.md("...")` for markdown text
- Read slider values with `slider.value`

### Notebook Structure Convention

- Cell 1: imports (marimo, numpy, plotly)
- Cell 2: parameters (all `mo.ui.slider` definitions, displayed with `mo.vstack`)
- Cell 3: define the system (functions and computations that reference slider values)
- Cell 4+: visualizations, each answering one design question
- Last cell: summary table of key metrics using `mo.md` with a markdown table

### Workflow Rules

1. Put every tunable constant behind a `mo.ui.slider`
2. Show the ratio or inverse (what the player feels), not just the raw curve
3. Use Plotly for interactive charts (zoom, hover, pan)
4. One design question per visualization cell
5. Use `np.arange` or `np.linspace` for x-axis ranges -- all math should be vectorized with NumPy

## Pattern Recipes

### "How should XP scale?"

Create a progression notebook with:
- Sliders: growth exponent, base cost multiplier, income growth rate
- Compute: `cost(level) = base * level^exponent`, `income(level) = rate * level^income_exp`
- Key chart: `time_to_level = cost / income` -- this is what the player feels
- Also show: raw cost curve, raw income curve
- Reference: Pokemon uses cubic (level^3), Civ 6 uses n^1.5, D&D uses quadratic

### "Does my economy break?"

Create an economy simulation notebook with:
- Define stocks as a dict: `{"gold": 100.0, "reputation": 1.0}`
- Define flows as functions of current stock levels (this is how feedback loops emerge)
- Tick loop: update each stock by its net flow per tick
- Key chart: all stock levels over time on one plot -- look for unbounded growth or depletion
- Also show: net flow per stock (inflow - outflow). When this crosses zero, the stock is at equilibrium.
- Support events at specific ticks: `if t == event_tick: stocks["gold"] -= cost`

Economy simulation template:
```python
ticks = 500
history = {name: np.zeros(ticks) for name in stocks}

for t in range(ticks):
    # Compute flows based on current stocks
    customers = base_rate * np.log(stocks["reputation"] + 1)
    gold_income = customers * revenue_per_customer
    gold_drain = customers * cost_per_customer + overhead

    # Update stocks
    stocks["gold"] += gold_income - gold_drain
    stocks["reputation"] += growth_rate * customers

    # Record
    for name in stocks:
        history[name][t] = stocks[name]

    # Events
    if t == upgrade_tick:
        stocks["gold"] -= upgrade_cost
        stocks["reputation"] += reputation_boost
```

### "Is this power-up too strong?"

- Plot the relevant stat with and without the power-up against a difficulty curve
- Find the crossover point: where does the power-up make the content trivial?
- Use `np.argmax(power_curve > difficulty_curve)` to find the exact level/floor

### "How swingy are my drops?"

- Always use Monte Carlo simulation (never just show the average)
- Show histogram of outcomes + percentile bands (p10, p25, p50, p75, p90)
- Compare PRD (pseudo-random distribution) vs true random side by side
- PRD implementation: `P(nth attempt) = C * n`, reset on success. Solve for C with binary search so long-run rate equals nominal probability.

PRD implementation template:
```python
def prd_constant(p):
    """Binary search for PRD constant C given nominal probability p."""
    lo, hi = 0.0, p
    for _ in range(100):
        mid = (lo + hi) / 2
        expected_p = 0.0
        prob_not_yet = 1.0
        max_n = max(1, int(np.ceil(1.0 / mid))) if mid > 0 else 1
        for n in range(1, max_n + 1):
            p_n = min(1.0, mid * n)
            expected_p += p_n * prob_not_yet
            prob_not_yet *= (1 - p_n)
        if expected_p > p:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2
```

Vectorized Monte Carlo template (fast, use this over Python loops):
```python
def simulate_runs(n_runs, n_floors, C, power_fn, rng):
    power = np.full(n_runs, 10.0)  # starting power
    attempts = np.zeros(n_runs)
    for floor in range(1, n_floors + 1):
        attempts += 1
        rolls = rng.random(n_runs)
        procs = rolls < np.minimum(1.0, C * attempts)
        power[procs] += power_fn(floor)
        attempts[procs] = 0
    return power
```

### "Does this feedback loop converge?"

- Simulate iteratively: `x[t+1] = f(x[t])`
- Plot the trajectory over time
- Annotate whether it converges, oscillates, or diverges
- For coupled loops: plot both quantities and their phase portrait (x vs y)

### "How should I price items?"

- Bounded elastic model: `P = P_base * (1 + k * clamp(ratio, -1, +1))`
- Simulate buy/sell pressure with noise over time
- Show price within bounds, annotate equilibrium
- Reference: Victoria 3 uses k=0.75, bounds at 25%-175%

## Visualization Rules

- **Progression**: always show `time_to_level = cost / income`, not just the cost curve
- **Economy**: line chart for stock levels over time, net flow chart to find equilibrium
- **Randomness**: never show just the average -- always show the full distribution (histogram + percentiles)
- **Feedback**: simulate iteratively, show convergence/divergence trajectory
- **Sensitivity**: sweep a parameter with a for loop, collect a metric, plot as a line
- **Combat**: plot damage multiplier as a function of stat gap, annotate key thresholds (2x, 5x, 10x)

## Reference

- `game-math-toolkit.md` -- formulas for 20 primitives (growth curves, diminishing returns, production, market, feedback loops, probability, combat). Includes parameter descriptions and selection guides.
- `game-math-case-studies.md` -- how shipped games calibrated these primitives. Actual constants from Pokemon, Civ, Factorio, Hades, Slay the Spire, Victoria 3, LoL, Dota 2, etc.
- `notebooks/` -- working example notebooks. Reference these for Marimo patterns and visualization recipes.
```

- [ ] **Step 2: Verify CLAUDE.md is well-formed**

Run: `wc -l CLAUDE.md`
Expected: approximately 170-190 lines.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "Add CLAUDE.md: game systems design assistant guide"
```

---

### Task 3: Progression Notebook

**Files:**
- Create: `notebooks/progression.py`

- [ ] **Step 1: Create `notebooks/` directory**

Run: `mkdir -p notebooks`

- [ ] **Step 2: Create `notebooks/progression.py`**

```python
import marimo

app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    return go, make_subplots, mo, np


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
def _(cost, go, income, levels, mo, time_to_level):
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
def _(cost, income, levels, mo, np, time_to_level):
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
```

- [ ] **Step 3: Verify notebook runs headlessly**

Run: `uv run marimo run notebooks/progression.py`
Expected: exits cleanly with no errors.

- [ ] **Step 4: Commit**

```bash
git add notebooks/progression.py
git commit -m "Add progression curve notebook: XP cost, income, time-to-level"
```

---

### Task 4: Economy Flow Notebook

**Files:**
- Create: `notebooks/economy_flow.py`

- [ ] **Step 1: Create `notebooks/economy_flow.py`**

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

    for t in range(ticks):
        customers = customer_base.value * np.log(stocks["reputation"] + 1)
        gold_in = customers * revenue.value
        gold_out = customers * cost_per.value + overhead.value
        rep_in = growth_rate.value * customers

        stocks["gold"] += gold_in - gold_out
        stocks["reputation"] += rep_in

        if stocks["gold"] < 0:
            stocks["reputation"] *= 0.95
            stocks["gold"] = 0

        if t == int(upgrade_tick.value):
            stocks["gold"] = max(0, stocks["gold"] - 500)
            stocks["reputation"] += 10

        history["gold"][t] = stocks["gold"]
        history["reputation"][t] = stocks["reputation"]
        net_flow["gold"][t] = gold_in - gold_out
        net_flow["reputation"][t] = rep_in
    return history, net_flow, ticks


@app.cell
def _(go, history, mo, np, ticks):
    t = np.arange(ticks)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=history["gold"], name="Gold",
                              line=dict(color="#FFD700")))
    fig.add_trace(go.Scatter(x=t, y=history["reputation"], name="Reputation",
                              line=dict(color="#636EFA"), yaxis="y2"))
    fig.update_layout(
        title="Stock Levels Over Time",
        xaxis_title="Tick",
        yaxis=dict(title="Gold", titlefont=dict(color="#FFD700")),
        yaxis2=dict(title="Reputation", titlefont=dict(color="#636EFA"),
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
    t = np.arange(ticks)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=t, y=net_flow["gold"], name="Gold net flow",
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
```

- [ ] **Step 2: Verify notebook runs headlessly**

Run: `uv run marimo run notebooks/economy_flow.py`
Expected: exits cleanly with no errors.

- [ ] **Step 3: Commit**

```bash
git add notebooks/economy_flow.py
git commit -m "Add economy flow notebook: restaurant tycoon source/pool/drain simulation"
```

---

### Task 5: Combat Balance Notebook

**Files:**
- Create: `notebooks/combat_balance.py`

- [ ] **Step 1: Create `notebooks/combat_balance.py`**

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
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=delta, y=hits_to_kill, name="Hits to kill",
                               line=dict(color="#AB63FA", width=3)))
    trivial_idx = np.argmax(hits_to_kill <= 1)
    trivial_delta = delta[trivial_idx] if hits_to_kill[trivial_idx] <= 1 else None
    fig2.update_layout(
        title=f"Hits to Kill ({defender_hp.value} HP defender)",
        xaxis_title="Stat advantage",
        yaxis_title="Hits needed",
        hovermode="x unified",
    )
    if trivial_delta is not None:
        fig2.add_vline(x=trivial_delta, line_dash="dash", line_color="red",
                        annotation_text=f"One-shot at +{trivial_delta:.0f}")
    equal_hits = np.ceil(defender_hp.value / base_damage.value)
    mo.vstack([
        mo.md("### Hits to Kill — When Combat Becomes Trivial"),
        mo.md(f"At equal strength: **{equal_hits:.0f} hits** to kill. " +
              (f"One-shot threshold: **+{trivial_delta:.0f}** stat advantage." if trivial_delta is not None else "No one-shot possible in this range.")),
        fig2,
    ])
    return


@app.cell
def _(base_damage, doubling_point, k, mo, np):
    gaps = [0, 5, 10, 15, 20, 25, 30]
    rows = "\n".join(
        f"| +{g} | {np.exp(g/k.value):.2f}x | {base_damage.value * np.exp(g/k.value):.0f} | {base_damage.value * np.exp(-g/k.value):.0f} |"
        for g in gaps
    )
    mo.md(f"""### Reference Table

| Stat gap | Damage multiplier | Damage dealt | Damage taken |
|---|---|---|---|
{rows}

**Design levers:**
- Lower k → each stat point matters more (steep curve, snowbally)
- Higher k → stat points matter less (flat curve, forgiving)
- k={k.value} means doubling point is +{doubling_point:.1f} stats
- Civ 6 uses k=25, base=30. Modifiers: flanking +2, Great General +5, Corps +10, Army +17.
""")
    return


if __name__ == "__main__":
    app.run()
```

- [ ] **Step 2: Verify notebook runs headlessly**

Run: `uv run marimo run notebooks/combat_balance.py`
Expected: exits cleanly with no errors.

- [ ] **Step 3: Commit**

```bash
git add notebooks/combat_balance.py
git commit -m "Add combat balance notebook: exponential difference damage model"
```

---

### Task 6: Roguelike Variance Notebook

**Files:**
- Create: `notebooks/roguelike_variance.py`

- [ ] **Step 1: Create `notebooks/roguelike_variance.py`**

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
                                 show_value=True, label="Drop rate (nominal)")
    num_floors = mo.ui.slider(start=5, stop=50, step=5, value=20,
                               show_value=True, label="Number of floors")
    num_runs = mo.ui.slider(start=1000, stop=10000, step=1000, value=5000,
                             show_value=True, label="Simulation runs")
    base_power_gain = mo.ui.slider(start=1, stop=20, step=1, value=5,
                                    show_value=True, label="Base power per drop")
    mo.vstack([
        mo.md("## Roguelike Run Variance"),
        mo.md("Simulate thousands of runs with PRD (pseudo-random distribution) drops. See how swingy the outcomes are."),
        mo.hstack([nominal_rate, num_floors]),
        mo.hstack([num_runs, base_power_gain]),
    ])
    return base_power_gain, nominal_rate, num_floors, num_runs


@app.cell
def _(np):
    def prd_constant(p):
        """Binary search for PRD constant C given nominal probability p."""
        if p <= 0:
            return 0.0
        if p >= 1:
            return 1.0
        lo, hi = 0.0, p
        for _ in range(100):
            mid = (lo + hi) / 2
            expected_p = 0.0
            prob_not_yet = 1.0
            max_n = max(1, int(np.ceil(1.0 / mid))) if mid > 0 else 1
            for n in range(1, max_n + 1):
                p_n = min(1.0, mid * n)
                expected_p += p_n * prob_not_yet
                prob_not_yet *= (1 - p_n)
            if expected_p > p:
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2

    def simulate_prd(n_runs, n_floors, C, power_fn, rng):
        """Vectorized Monte Carlo: simulate n_runs in parallel."""
        power = np.full(n_runs, 10.0)
        attempts = np.zeros(n_runs)
        for floor in range(1, n_floors + 1):
            attempts += 1
            rolls = rng.random(n_runs)
            procs = rolls < np.minimum(1.0, C * attempts)
            power[procs] += power_fn(floor)
            attempts[procs] = 0
        return power

    def simulate_true_random(n_runs, n_floors, p, power_fn, rng):
        """Vectorized Monte Carlo with true random (no PRD)."""
        power = np.full(n_runs, 10.0)
        for floor in range(1, n_floors + 1):
            rolls = rng.random(n_runs)
            procs = rolls < p
            power[procs] += power_fn(floor)
        return power
    return prd_constant, simulate_prd, simulate_true_random


@app.cell
def _(base_power_gain, nominal_rate, np, num_floors, num_runs, prd_constant,
      simulate_prd, simulate_true_random):
    C = prd_constant(nominal_rate.value)
    rng = np.random.default_rng(42)
    power_fn = lambda floor: base_power_gain.value * floor ** 0.5

    prd_results = simulate_prd(num_runs.value, num_floors.value, C, power_fn, rng)
    rng2 = np.random.default_rng(42)
    random_results = simulate_true_random(num_runs.value, num_floors.value,
                                           nominal_rate.value, power_fn, rng2)
    return C, prd_results, random_results


@app.cell
def _(go, mo, np, num_floors, prd_results, random_results):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=prd_results, name="PRD", opacity=0.7,
                                marker_color="#636EFA", nbinsx=40))
    fig.add_trace(go.Histogram(x=random_results, name="True Random", opacity=0.7,
                                marker_color="#EF553B", nbinsx=40))
    fig.update_layout(
        title=f"Player Power Distribution at Floor {num_floors.value}",
        xaxis_title="Total Power",
        yaxis_title="Count",
        barmode="overlay",
        hovermode="x unified",
    )
    prd_std = np.std(prd_results)
    rand_std = np.std(random_results)
    mo.vstack([
        mo.md("### Power Distribution — PRD vs True Random"),
        mo.md(f"PRD standard deviation: **{prd_std:.1f}**. True random: **{rand_std:.1f}**. PRD is **{rand_std/prd_std:.1f}x tighter** — fewer extreme outliers."),
        fig,
    ])
    return


@app.cell
def _(C, mo, nominal_rate, np, prd_results, random_results):
    def percentiles(data):
        return {p: np.percentile(data, p) for p in [10, 25, 50, 75, 90]}

    prd_pct = percentiles(prd_results)
    rand_pct = percentiles(random_results)

    rows = "\n".join(
        f"| p{p} | {prd_pct[p]:.1f} | {rand_pct[p]:.1f} |"
        for p in [10, 25, 50, 75, 90]
    )
    mo.md(f"""### Percentile Table

| Percentile | PRD | True Random |
|---|---|---|
{rows}

**Interpretation:**
- p10 = unlucky run (bottom 10%). p90 = lucky run (top 10%).
- The gap between p10 and p90 is the "swinginess" of the system.
- PRD p10-p90 range: **{prd_pct[90]-prd_pct[10]:.1f}**. True random: **{rand_pct[90]-rand_pct[10]:.1f}**.

**PRD constant:** C = {C:.5f} for nominal rate {nominal_rate.value:.0%}. This means first attempt has {C:.1%} chance, second has {2*C:.1%}, etc. Guaranteed proc by attempt {int(np.ceil(1/C))}.

**Reference:** Dota 2 uses C=0.03980 for 17% bash. Three consecutive procs at 17% under PRD: ~1 in 10,000. Under true random: ~1 in 200.
""")
    return


if __name__ == "__main__":
    app.run()
```

- [ ] **Step 2: Verify notebook runs headlessly**

Run: `uv run marimo run notebooks/roguelike_variance.py`
Expected: exits cleanly with no errors.

- [ ] **Step 3: Commit**

```bash
git add notebooks/roguelike_variance.py
git commit -m "Add roguelike variance notebook: PRD Monte Carlo simulation"
```

---

### Task 7: Market Pricing Notebook

**Files:**
- Create: `notebooks/market_pricing.py`

- [ ] **Step 1: Create `notebooks/market_pricing.py`**

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
    rng = np.random.default_rng(42)

    prices = np.zeros(ticks)
    buys = np.zeros(ticks)
    sells = np.zeros(ticks)

    for t in range(ticks):
        demand_noise = rng.normal(0, volatility.value)
        buy = max(1, demand_base.value + demand_noise)
        sell = max(1, supply_base.value + rng.normal(0, 1))
        buys[t] = buy
        sells[t] = sell

        ratio = (buy - sell) / max(1, min(buy, sell))
        clamped = max(-1, min(1, ratio))
        prices[t] = p_base.value * (1 + elasticity.value * clamped)
    return buys, prices, sells, ticks


@app.cell
def _(elasticity, go, mo, np, p_base, prices, ticks):
    t = np.arange(ticks)
    upper_bound = p_base.value * (1 + elasticity.value)
    lower_bound = p_base.value * (1 - elasticity.value)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=prices, name="Price",
                              line=dict(color="#636EFA", width=2)))
    fig.add_hline(y=p_base.value, line_dash="dash", line_color="gray",
                   annotation_text="Base price")
    fig.add_hline(y=upper_bound, line_dash="dot", line_color="red",
                   annotation_text=f"Upper bound ({upper_bound:.0f})")
    fig.add_hline(y=lower_bound, line_dash="dot", line_color="green",
                   annotation_text=f"Lower bound ({lower_bound:.0f})")
    fig.update_layout(
        title="Price Over Time (Bounded)",
        xaxis_title="Tick",
        yaxis_title="Price",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Price Movement"),
        mo.md(f"Price is bounded between **{lower_bound:.0f}** and **{upper_bound:.0f}** ({(1-elasticity.value)*100:.0f}% to {(1+elasticity.value)*100:.0f}% of base). No matter how extreme the demand shock, the price never leaves this band."),
        fig,
    ])
    return


@app.cell
def _(buys, go, mo, np, sells, ticks):
    t = np.arange(ticks)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=t, y=buys, name="Buy orders (demand)",
                               line=dict(color="#EF553B")))
    fig2.add_trace(go.Scatter(x=t, y=sells, name="Sell orders (supply)",
                               line=dict(color="#00CC96")))
    fig2.update_layout(
        title="Supply vs Demand",
        xaxis_title="Tick",
        yaxis_title="Orders per tick",
        hovermode="x unified",
    )
    mo.vstack([
        mo.md("### Supply and Demand"),
        mo.md("When demand (red) exceeds supply (green), prices rise. When supply exceeds demand, prices fall. The clamping prevents extreme ratios from producing extreme prices."),
        fig2,
    ])
    return


@app.cell
def _(elasticity, mo, np, p_base, prices):
    avg_price = np.mean(prices)
    price_std = np.std(prices)
    pct_above_base = np.mean(prices > p_base.value) * 100
    upper = p_base.value * (1 + elasticity.value)
    lower = p_base.value * (1 - elasticity.value)
    mo.md(f"""### Summary

| Metric | Value |
|---|---|
| Base price | {p_base.value} |
| Price band | {lower:.0f} — {upper:.0f} |
| Average price | {avg_price:.1f} |
| Price std dev | {price_std:.1f} |
| Time above base | {pct_above_base:.0f}% |

**Design levers:**
- **Elasticity (k):** Controls how wide the price band is. Victoria 3 uses k=0.75 (25%-175% band). Lower k → stickier prices. Higher k → more responsive.
- **Volatility:** Controls demand noise. High volatility + high elasticity = wild price swings within bounds. Low volatility = prices hover near base.
- **Base price:** The anchor. All other prices are relative to this. Victoria 3 example: Grain=20, Tools=40.

**Key insight:** Bounds matter more than curves. Victoria 3's entire market is held inside a 25%-175% band on purpose. The simulation can be deep and still refuse to let the economy explode.
""")
    return


if __name__ == "__main__":
    app.run()
```

- [ ] **Step 2: Verify notebook runs headlessly**

Run: `uv run marimo run notebooks/market_pricing.py`
Expected: exits cleanly with no errors.

- [ ] **Step 3: Commit**

```bash
git add notebooks/market_pricing.py
git commit -m "Add market pricing notebook: bounded elastic model (Victoria 3-style)"
```

---

## Verification

After all tasks are complete, run the full verification:

```bash
# All notebooks should run without errors
uv run marimo run notebooks/progression.py
uv run marimo run notebooks/economy_flow.py
uv run marimo run notebooks/combat_balance.py
uv run marimo run notebooks/roguelike_variance.py
uv run marimo run notebooks/market_pricing.py
```

Then open one interactively to verify sliders and charts work:
```bash
uv run marimo edit notebooks/progression.py
```
