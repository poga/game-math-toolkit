# Proven Formulas Redesign

Rewrite all 5 notebooks from generic explorations into "feel comparison" tools anchored on proven, shipped game formulas. Each notebook shows 3-5 real formulas side by side, with the key output being the derived "feel" metric — what the player actually experiences.

## Design Principle

The notebooks are teaching tools. The lesson is: **different math produces different feel, and here's proof from games you know.** Every notebook leads with the feel chart, not the raw formula.

---

## 1. `progression.py` — "How Leveling Feels Across Real Games"

### Proven formulas

| Game | Formula | Source |
|---|---|---|
| OSRS | `XP(L) = floor(sum(floor(L' + 300 * 2^(L'/7)) / 4) for L'=1..L)` | Quarter-exponential sum |
| Pokemon Medium Fast | `XP(L) = L^3` | Clean cubic |
| D&D 5e | `XP(L) = 500 * L * (L-1)` | Quadratic approximation |
| Civ 6 population | `food(n) = 15 + 8*(n-1) + (n-1)^1.5` | Super-linear polynomial |

### Charts

1. **Time-per-level (feel chart):** All games normalized so level 1 = 1.0. This is the player experience. OSRS's exponential tail is visible against D&D's gentle quadratic.
2. **Raw XP cost curves (log scale):** Shows the underlying math.
3. **Grind ratio:** Last 10% of levels vs first 10% — quantifies how much harder endgame is.

### Sliders

- Max level range (to zoom into early/mid/late game)
- Assumed income growth rate (shared across all curves for fair comparison)

### Summary table

For each game: total XP to max, time ratio (last level / first level), grind inflection point.

---

## 2. `combat_balance.py` — "How Stat Gaps Decide Fights"

### Proven formulas

| Game | Formula | Type |
|---|---|---|
| Civ 6 | `damage = 30 * e^(delta/25)` | Exponential difference |
| LoL armor | `reduction = armor / (armor + 100)` | Hyperbolic |
| Civ 5 | `damage = 30 * ((((R+3)/4)^4 + 1) / 2)`, R = attacker/defender | Ratio |

### Charts

1. **Damage multiplier vs stat gap (feel chart):** All three on one plot. Shows how Civ 6 becomes a stomp faster than LoL, and how Civ 5 diverges at extremes.
2. **Hits to kill:** At what stat gap does a fight become trivial (1-shot)?
3. **Comeback zone:** Range where weaker side still has a chance (multiplier < 2x). Wider = more forgiving.

### Sliders

- Stat gap range
- Defender HP
- Base damage (shared baseline)

### Summary table

For each model: doubling point, 1-shot threshold, comeback zone width.

---

## 3. `market_pricing.py` — "How Markets Stay Stable (or Don't)"

### Proven formula

Victoria 3 bounded elastic: `P = P_base * (1 + 0.75 * clamp(ratio, -1, +1))`. Prices bounded to 25%-175% of base.

### Feel comparison — same demand shock, three market designs

| Model | Formula | Behavior |
|---|---|---|
| Unbounded linear | `P = P_base * (1 + k * ratio)` | Runaway prices on demand spike |
| Victoria 3 bounded | `P = P_base * (1 + k * clamp(ratio, -1, +1))` | Prices hit ceiling and stop |
| Logarithmic dampening | `P = P_base * (1 + k * sign(r) * log(1 + abs(r)))` | Soft ceiling, approaches but never hits bound |

### Charts

1. **Price response to same demand simulation (feel chart):** All three models, shared RNG. The moment unbounded explodes while Victoria 3 holds is the lesson.
2. **Price recovery time:** After a demand shock, ticks until price returns within 10% of base.
3. **Merchant profit window:** Buy/sell spread over time. Wider = more arbitrage.

### Sliders

- Base price, elasticity k, demand/supply volatility
- Shock magnitude (one-time demand spike at configurable tick)

### Summary table

For each model: max price reached, time above 150% of base, recovery time after shock.

---

## 4. `roguelike_variance.py` — "How Drop Systems Shape Run Outcomes"

### Proven formulas

| System | Formula | Source |
|---|---|---|
| Dota 2 PRD | `P(n) = C * n`, reset on success. C=0.01475 (10%), C=0.03980 (17%), C=0.08474 (25%) | Published constants |
| True random | `P(n) = p` constant | Control group |
| Bad-luck protection (StS-style) | Base chances (62% common, 35% uncommon, 3% rare). On each non-rare draw, rare probability increases additively by base chance until triggered, then resets. | Slay the Spire |

### Charts

1. **Drop count histogram (feel chart):** PRD vs true random at Dota 2's 17% rate. Tighter PRD distribution = fewer droughts and fewer lucky streaks.
2. **Longest drought distribution:** PRD has hard ceiling (attempt 26 at 17%). True random has fat tail.
3. **Consecutive proc probability:** 3 in a row is 1-in-10,000 under PRD vs 1-in-200 under true random.

### Sliders

- Nominal drop rate (Dota 2 presets highlighted)
- Number of floors/attempts
- Number of simulation runs

### Summary table

For each system: median drops, p10/p90 range, max drought length, consecutive proc probability.

---

## 5. `feedback_loops.py` — "How Feedback Loops Shape the Arc of a Run"

Replaces `economy_flow.py`.

### Proven systems

| Game | Mechanism | Loop type |
|---|---|---|
| Against the Storm | Reputation vs Impatience dual-bar race. Impatience +0.255/min, rep gain drains 1.0 impatience. | Coupled positive + negative |
| Hades Heat | Player-selected difficulty. Base * (1 + sum heat). Hard Labor +20%/rank, Lasting Consequences -25% healing/rank. Max 63 Heat. | Player-controlled negative |
| Mario Kart | `item_quality = max_quality * (1 - position/total)`. Last place = best items. | Automatic catch-up |

### Charts

1. **Tension curve (feel chart):** How close is the player to winning/losing at each moment? Against the Storm: tightening vice. Hades: player-controlled steady-state. Mario Kart: rubber-banding oscillation.
2. **Comeback probability:** If behind at midpoint, chance of recovery. Against the Storm: low. Mario Kart: high. Hades: depends on skill.
3. **Variance over time:** Converge (stable), oscillate (rubber band), or diverge (snowball)?

### Sliders

- Against the Storm: impatience rate, reputation-per-gain, drain coupling
- Hades: number of Heat ranks active
- Mario Kart: number of players, catch-up strength

### Summary table

For each system: convergence type, comeback rate from midpoint deficit, tension peak location.

---

## Implementation notes

- All formulas come from `game-math-case-studies.md` — no invented constants.
- Each notebook follows the existing Marimo conventions from CLAUDE.md.
- Feel charts are always the first visualization cell (most important = most prominent).
- Use Plotly for all charts. Distinct colors per game, consistent across charts within a notebook.
- Normalize curves where needed so comparisons are fair (e.g. time-per-level normalized to level 1 = 1.0).
