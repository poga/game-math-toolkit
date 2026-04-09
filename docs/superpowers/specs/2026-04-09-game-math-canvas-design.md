# Game Math Toolkit -- Design Spec

## Overview

A documentation-driven toolkit that turns Claude Code into a game systems design assistant. Designers describe what they want to explore (progression curves, economy balance, combat tuning, run variance), and Claude Code generates interactive Marimo notebooks with tweakable parameters.

No custom library. NumPy/SciPy covers all the math. The existing reference docs (`game-math-toolkit.md`, `game-math-case-studies.md`) are the knowledge base. CLAUDE.md teaches Claude Code how to apply them.

## Target Users

Game designers who are comfortable with code and math, working on management, simulation, tycoon, and roguelike games.

## Deliverables

### 1. Project Setup

**`pyproject.toml`** -- declares dependencies, uses uv as the project manager.

Dependencies:
- `marimo` -- reactive notebook runtime
- `numpy` -- array math
- `plotly` -- interactive charts

**`setup.sh`** -- one-command environment setup:
1. Check if `uv` is available; if not, print install instructions (`curl -LsSf https://astral.sh/uv/install.sh | sh`) and exit
2. `uv sync` (creates venv + installs deps from `pyproject.toml`)
3. Print instructions: `uv run marimo edit notebooks/progression.py`

Designer's first experience:
```bash
./setup.sh
uv run marimo edit notebooks/progression.py
```

### 2. CLAUDE.md

The guide that teaches Claude Code how to be a game systems design assistant. Sections:

**A) Role** -- "You are a game systems design assistant. When the designer asks about progression, economy, combat balance, or randomness, create a Marimo notebook that lets them explore the answer interactively."

**B) Workflow** -- When creating a notebook, always:
1. Create a Marimo `.py` notebook in `notebooks/`
2. Put every tunable constant behind a `mo.ui.slider`
3. Show the ratio/inverse (what the player feels), not just the raw curve
4. Use Plotly for interactive charts
5. Answer one design question per visualization cell

**C) Pattern recipes** -- How to handle common design requests:

| Designer says | Claude Code does |
|---|---|
| "How should XP scale?" | Cost curve + income curve + time-to-level ratio, sliders for exponent and base |
| "Does my economy break?" | Tick simulation of stocks, plot levels over time, highlight where net flow crosses zero |
| "Is this power-up too strong?" | Plot power with/without upgrade vs difficulty curve, find crossover point |
| "How swingy are my drops?" | Monte Carlo, histogram + percentile bands (p10/p25/p50/p75/p90) |
| "Does this feedback loop converge?" | Iterative simulation, plot trajectory, warn if unbounded growth |
| "How should I price items?" | Bounded elastic pricing sim, show price oscillation and convergence |

**D) Visualization rules:**
- Progression: always show `time_to_level = cost / income`, not just cost
- Economy: stacked area for sources vs sinks, line chart for stock levels
- Randomness: never show just the average -- always show the distribution
- Feedback: simulate iteratively, show convergence/divergence over time
- Sensitivity: sweep a parameter, collect a metric, plot as a line

**E) Economy simulation pattern:**
- Define stocks as a dict: `{"gold": 100, "wood": 50}`
- Define flows as functions of current stock levels
- Tick loop: `stocks[resource] += net_flow(resource) * dt`
- Track history as arrays, plot all stocks on one chart
- Support events at specific ticks (perturbations, upgrades, roguelike power-ups)

**F) Notebook structure convention:**
- Cell 1: imports (`marimo`, `numpy`, `plotly`)
- Cell 2: parameters (all `mo.ui.slider` definitions)
- Cell 3: define the system (functions that reference parameters)
- Cell 4+: visualizations, each answering one design question
- Last cell: summary table of key metrics

**G) Marimo notebook format:**
- Marimo notebooks are `.py` files where each cell is a function decorated with `@app.cell`
- Cells declare dependencies via function arguments (Marimo infers the DAG)
- Always generate valid Marimo format, not plain Python scripts
- Use `marimo edit --sandbox notebook.py` to create new notebooks interactively

**H) Reference pointers:**
- `game-math-toolkit.md` -- formulas for all 20 primitives and when to use each
- `game-math-case-studies.md` -- calibration examples from shipped games (Pokemon, Civ 6, Factorio, Hades, Slay the Spire, etc.)
- `notebooks/` -- working examples to reference and adapt

### 3. Example Notebooks

Five Marimo notebooks (`.py` files). Each is a working example AND a template that Claude Code learns from when generating new notebooks.

**`notebooks/progression.py`** -- XP curve shaping
- Sliders: exponent (1-3), base cost, income growth rate
- Three charts: cost curve, income curve, time-to-level ratio
- Designer sees immediately how changing the exponent affects grind feel
- References: Pokemon cubic, Civ 6 n^1.5, D&D quadratic from case studies

**`notebooks/economy_flow.py`** -- Restaurant tycoon economy
- Stocks: gold, ingredients, reputation
- Flows: customer income (function of reputation), supply cost (constant), upgrade drain (player-triggered)
- Tick simulation over 500 ticks, stock level chart, net balance chart
- Slider for customer growth rate -- find the tipping point from stable to snowball
- Events: simulate an upgrade at tick 100, show the ripple effect

**`notebooks/combat_balance.py`** -- Stat gap impact
- Exponential difference damage model: `base * e^(delta/k)`
- Sliders: base damage, k (scaling factor)
- Shows: at +10 strength you deal 1.5x, at +30 you deal 3.3x
- Crossover annotation: where does the fight become trivial?
- Reference: Civ 6's k=25 calibration

**`notebooks/roguelike_variance.py`** -- Run outcome distribution
- PRD drop system for power-ups (configurable nominal rate)
- Power scaling function per floor
- 10,000 run Monte Carlo simulation
- Histogram of player power at floor 20 + percentile table
- Slider for drop rate -- shows how variance and expected power shift
- Compares PRD vs true random side by side

**`notebooks/market_pricing.py`** -- Supply/demand pricing
- Bounded elastic model: `P = P_base * (1 + k * clamp(ratio, -1, +1))`
- Simulated buy/sell pressure over 200 ticks with some noise
- Price chart showing oscillation within bounds
- Sliders: elasticity (k), bound width, demand volatility
- Reference: Victoria 3's 25%-175% band

### 4. Existing Documentation (no changes)

- **`game-math-toolkit.md`** -- reference of 20 mathematical primitives across 10 categories (growth curves, contest resolution, production, market, spatial fields, flow/queueing, diminishing returns, feedback loops, probability, decision value). Includes formulas, parameter descriptions, and selection guides.

- **`game-math-case-studies.md`** -- how shipped games (Pokemon, Civ 5/6, Factorio, Anno 1800, Victoria 3, LoL, Dota 2, Hades, Slay the Spire, etc.) calibrated these primitives. Includes actual constants and the reasoning behind them.

## Project Structure

```
game-math-toolkit/
  CLAUDE.md                   # Guide for Claude Code
  setup.sh                    # One-command setup (uv)
  pyproject.toml              # Dependencies
  game-math-toolkit.md        # (existing) Math reference
  game-math-case-studies.md   # (existing) Case studies
  notebooks/
    progression.py            # XP curve shaping
    economy_flow.py           # Source/pool/drain simulation
    combat_balance.py         # Stat gap impact
    roguelike_variance.py     # Monte Carlo run distribution
    market_pricing.py         # Bounded elastic pricing
  docs/
    superpowers/
      specs/
        2026-04-09-game-math-canvas-design.md  # This file
```

## What This Is NOT

- Not a Python library with wrapper functions -- NumPy/SciPy already covers all the math
- Not a custom notebook UI -- Marimo provides the reactive notebook
- Not a node-graph or visual editor -- designers write code, Claude Code assists
- Not a drag-and-drop tool -- the target user is comfortable with code and math

## Tech Stack

- **Runtime:** Marimo (reactive Python notebook, `.py` file format)
- **Package manager:** uv
- **Math:** NumPy, SciPy (standard library-level math)
- **Charting:** Plotly (interactive, zoom, hover)
- **AI assistant:** Claude Code (reads CLAUDE.md, generates notebooks)
