# Game Systems Math Toolkit

A reference of the fundamental mathematical primitives behind progression, economy, combat, and feel. Each section states a design problem, gives the formulas that solve it, and describes the parameters you actually tune. The source material spans dozens of shipped games; the primitives number around twenty.

---

## 1. Growth and Scaling Curves

**Design problem:** how should effort and reward change as the player progresses?

What the player feels is not the cost curve itself but the ratio `time_to_next(x) = cost(x) / income(x)`. Pick curves so this ratio stays in the band you want across all levels. Flat ratio means constant pace. Rising ratio means increasing grind.

### Linear
```
y = a·x + b
```
Constant rate. Predictable. Best for tutorials and short ranges where simplicity matters more than shape.

### Polynomial (power law)
```
y = a·x^k + c
```
Smooth super-linear growth. The exponent controls steepness: 1.5 for gentle, 2 for moderate, 3 for aggressive but bounded. Use when income scales slowly and you want costs to stay ahead of it without exploding.

### Exponential
```
y = a·b^x
```
Each step multiplies the previous by a constant. Extremely aggressive. Only use this when the opposing quantity (income, damage, power) also grows exponentially, otherwise the system becomes unplayable within a few levels.

### Logistic (S-curve)
```
y = K / (1 + e^(-r·(x - x₀)))
```
Slow start, rapid middle, plateau at carrying capacity `K`. This naturally models anything with a ceiling: population under housing, skill under practice, market adoption under saturation. The parameter `r` controls how sharp the S is, and `x₀` controls when the inflection hits.

### Logarithmic
```
y = k·ln(x + 1)
```
Rapid early gains, slow late gains. Use for stats you want to matter forever but never dominate. A +1 at level 1 feels very different from a +1 at level 100, by design.

### Choosing between them
| Shape | Use when |
|---|---|
| Linear | You want perfect predictability |
| Polynomial n^1.5–2 | Standard strategy and RPG progression |
| Cubic n^3 | Level-capped RPG XP |
| Exponential | Income also grows exponentially |
| Logistic | There is a natural cap |
| Logarithmic | Infinite-scaling or prestige systems |

---

## 2. Contest Resolution

**Design problem:** translate opposed power into outcomes.

### Linear contest (Lanchester's linear law)
```
dA/dt = -β·B·(A/A₀)
dB/dt = -α·A·(B/B₀)
```
Combat is one-on-one. Doubling force doubles effective power. Side A wins if `α·A₀ > β·B₀`. Use for duels, lane combat, and any situation where only a subset of each force can engage at once.

### Square contest (Lanchester's square law)
```
dA/dt = -β·B
dB/dt = -α·A
```
Every unit can target any enemy. Fighting power scales with the *square* of force size, which is why concentration is devastating in ranged combat. Side A wins if `α·A₀² > β·B₀²`. Survivors: `A_final = √(A₀² - (β/α)·B₀²)`.

### Two ways to map a strength gap to damage
Ratio form:
```
damage ∝ f(A_strength / B_strength)
```
Clean when bonuses are naturally multiplicative. Overflows when ratios get extreme.

Difference form:
```
damage = base · e^(Δ/k),  where Δ = A_strength - B_strength
```
Damage doubles every `k·ln(2)` strength points. Bonuses stack additively on strength, which is easier to reason about and balance. Use this when you want linear-feeling modifiers but nonlinear outcomes.

### Stacking rule
Pick additive-within-category, multiplicative-between-category as the default. Terrain, weather, and morale multipliers compound; individual unit bonuses add up inside each category. This gives you a readable design surface where no single modifier is decisive but combinations are.

---

## 3. Production and Transformation

**Design problem:** turn inputs into outputs in a way that forces interesting choices.

### Multi-input production (Cobb-Douglas)
```
Y = A · X₁^α₁ · X₂^α₂ · ... · Xₙ^αₙ,   with Σαᵢ ≤ 1
```
Doubling all inputs doubles output. Doubling only one input yields diminishing returns. The exponents are the weight each input carries. Use this when you want players to balance multiple resources rather than stockpile the cheapest.

### Fixed-ratio chain
```
output_rate = (speed · qty_per_cycle) / cycle_time
buildings_needed = demand / output_rate
```
Deterministic. Each production step needs a specific integer ratio of feeders to consumers. Readable, puzzle-like, and easy to visualize. Use it when planning is part of the fun.

### Recipe graph
Model transformations as a directed acyclic graph. Raw cost of any item is a recursive traversal down to leaves. Throughput is limited by the minimum cut of the flow network. Use this structure for complex crafting trees where players need to find the real bottleneck.

---

## 4. Market and Exchange

**Design problem:** let prices emerge from supply and demand without breaking.

### Linear equilibrium
```
Q_d = a - b·P       (demand)
Q_s = c + d·P       (supply)
P*  = (a - c) / (b + d)
```
The slopes `b` and `d` control elasticity. Flat curves mean quantity swings hard with small price changes. Use this for single-good markets where you need an analytic answer.

### Dynamic adjustment
```
P(t+1) = P(t) · (1 + λ · (Q_d - Q_s) / Q_s)
```
Price chases equilibrium at rate `λ`. Values around 0.01 give sticky prices and slow cycles. Values around 0.1 give whiplash. This is the right model for live player-driven markets.

### Bounded elastic pricing
```
P = P_base · (1 + k · clamp((buys - sells) / min(buys, sells), -1, +1))
```
Prices stay within a fixed band around a base value. Prevents hyperinflation and deflation entirely. Use this when you want a soft market signal without risking a broken economy, which is the right call for most single-player simulations.

---

## 5. Spatial Fields

**Design problem:** make position matter.

### Diffusion
```
C(t+1, x, y) = (1 - decay)·C(t, x, y) + D·(avg_neighbors - C(t, x, y)) + source(x, y)
```
Spreads any quantity across a grid: pollution, culture, heat, influence, fire. The diffusion coefficient `D` controls spread speed, and `decay` controls falloff. Stability requires `D·Δt/Δx² ≤ 0.25` on a 4-neighbor grid.

For directional spread, add an advection term proportional to wind or current velocity.

### Distance decay
```
value(x, y) = Σ wᵢ · factorᵢ · max(0, 1 - dᵢ/radius)
```
Each source contributes a weight that falls with distance. Linear falloff is cheapest and readable. Inverse square feels more "physical" but creates extreme near-field values. Use this for land desirability, zone of control, and placement bonuses.

### Competing fields
Run one diffusion per owner, then assign each cell to the owner with the highest local value. This gives you culture borders, influence wars, and territorial contention with a single uniform mechanism.

---

## 6. Flow and Queueing

**Design problem:** model throughput, bottlenecks, and waiting.

### Little's Law
```
L = λ · W
```
Average items in any stable system equals arrival rate times average time in system. Universal. Apply it to queues, production lines, inventory, crowds, anything.

### M/M/1 queue (single server)
```
ρ  = λ/μ                  (utilization; must be < 1)
L  = ρ/(1 - ρ)            (avg in system)
Wq = λ / (μ·(μ - λ))      (avg wait in queue)
```
Wait time rises hyperbolically as utilization approaches 1. At 80% utilization the wait is four times longer than at 50%. This is why service buildings feel fine until suddenly they do not. Size capacity against peak load, not average.

### Max-flow and min-cut
The maximum throughput of a network equals the capacity of its smallest cut. Find the bottleneck edge to find the balance lever. Directly applicable to production chains, logistics, and road networks.

### Pathfinding cost surfaces
A* finds the cheapest path given a heuristic and edge costs. The design surface is the cost function: slope penalty, turn penalty, signal penalty, terrain multiplier. Tuning these costs is the same thing as tuning how units behave. Use octile distance for 8-way grids and Euclidean for any-angle movement.

---

## 7. Diminishing Returns

**Design problem:** bound stacking so stats never trivialize the game.

### Hyperbolic
```
effective = stat / (stat + k)
```
At `stat = k` you get exactly 50%. Never reaches 100%. Each point adds a constant amount of "effective HP" while the percentage reduction diminishes. The cleanest formula for damage reduction, resistance, and armor.

### Multiplicative stacking
```
effective = 1 - (1 - p)^n
```
Three 25% stacks give 57.8%, not 75%. Prevents reaching 100% with finite stacks. Use for evasion, crit chance, and chance-to-avoid.

### Exponential approach
```
effective = max · (1 - e^(-k·stat))
```
Smooth glide to a hard cap. The parameter `k` controls how quickly you approach it. Good when you want a visible ceiling and a smooth feel all the way up.

### Piecewise soft cap
Full value up to a threshold, then reduced rate beyond, possibly in multiple tiers. Sends a strong design message: "this is the target, but more is tolerated."

### Logarithmic
```
effective = k · ln(stat + 1)
```
Unbounded but very slow. Correct choice for infinite-scaling systems and prestige loops where you want every 10× of input to feel like the same step.

### Picking between them
Use hyperbolic for defensive stats, multiplicative for chance-to-avoid, exponential for hard caps with smooth feel, piecewise when you need a sharp message, logarithmic when the stat has no upper bound.

---

## 8. Feedback Loops

**Design problem:** decide whether a system stabilizes, spirals, or oscillates. Every system in a game is a feedback loop or a composition of them. This section is the most important one.

### Positive feedback (reinforcing)
```
dx/dt = k·x     ⇒     x(t) = x₀·e^(kt)
```
More of X produces more of X. Creates runaway leaders and winner-takes-all dynamics. Use it deliberately for snowball mechanics, then bound it with a cap, a rising cost, or a coupled negative loop.

### Negative feedback (balancing)
```
dx/dt = -k·(x - target)
```
System converges to target with time constant `τ = 1/k`. Use for rubber-banding, market equilibrium, dynamic difficulty, anything that should self-correct.

### Coupled loops
Two quantities feed each other. Two positives give explosive growth or collapse. One positive and one negative give convergence or oscillation depending on the gains. Race mechanics built from coupled loops (one bar fills, another bar drains it) produce the most legible tension systems in game design.

### PID controller
```
u = Kp·e + Ki·∫e·dt + Kd·(de/dt),   where e = target - actual
```
The proportional term responds to current error, the integral term eliminates steady-state bias, and the derivative term prevents overshoot. Use for dynamic difficulty adjustment. Tune with the Ziegler-Nichols method: find the critical gain where the system oscillates, then set `Kp = 0.6·Ku`, `Ki = 2·Kp/Tu`, `Kd = Kp·Tu/8`.

### Catch-up term
```
bonus = k · (leader_score - player_score) / leader_score
```
Assistance scales with the gap, reaching zero at parity. Use when the system should help losing players visibly without feeling coercive.

---

## 9. Probability and Variance Shaping

**Design problem:** make randomness feel fair.

### Weighted selection
Standard cumulative sampling. Keep rarity ratios consistent across tiers; a 3× to 5× step between adjacent tiers gives a readable hierarchy that players learn quickly.

### Hypergeometric (sampling without replacement)
```
P(X = k) = C(K, k) · C(N - K, n - k) / C(N, n)
```
Probability of drawing `k` copies of a target from a deck of `N` cards containing `K` targets, drawing `n`. The essential primitive for card games. Key insight: thinning a deck improves target frequency more than adding copies does.

### Pseudo-random distribution (PRD)
```
P(nth attempt) = C·n,   reset on success
```
The constant `C` is solved so the long-run proc rate equals the nominal probability `p`. Eliminates streaks in both directions. A 17% proc with PRD has roughly 1-in-10,000 odds of three in a row, compared to 1-in-200 with true random. Use wherever streaks feel unfair.

### Pity timers
Guarantee a reward after `N` failures. Implemented by redistributing probability mass on each miss. Use when a rare drop should be a guarantee on some horizon rather than a pure lottery.

### Markov chain
```
x(k) = x(0)·P^k,   steady state satisfies π·P = π
```
Transition matrix where each entry `p_ij` is the probability of moving from state `i` to state `j`. Rows sum to 1. Use for weather, economy cycles, NPC mood, any system with memory of exactly one state.

---

## 10. Decision Value

**Design problem:** make choices feel meaningful.

### Expected value
```
EV = Σ pᵢ · vᵢ
```
The baseline. Necessary but not sufficient for an interesting choice.

### The interesting-decision test
A choice becomes interesting when `EV_safe ≈ EV_risky` but `Var(safe) ≪ Var(risky)`. Equal expected value, different variance, different consequences. Every branching decision in the game should pass this test or be removed.

### Logarithmic utility
```
U(wealth) = ln(wealth)
```
Models risk aversion. A 50/50 gamble of ±50 HP at 100 HP has EV of zero but negative expected utility, because `0.5·ln(150) + 0.5·ln(50) < ln(100)`. This explains mathematically why permadeath games should punish fair gambles, and it gives you a tool to check whether your risks actually feel risky.

### Cost curve
```
power  = Σ wᵢ · statᵢ
cost   = f(power),  fit via regression
```
List every item, assign each a power score, regress cost against power. Items above the fitted line are overcosted, items below are undercosted. The single most useful balance diagnostic you can build.

### Pareto dominance
Item A dominates item B if A is at least as good in every dimension and strictly better in at least one. Dominated items are dead choices. Find them, then either buff or remove.

---

## Composing the primitives

Real systems chain these together. A deckbuilder is hypergeometric sampling plus cost curves plus multiplicative scoring bounded by a rising ante requirement. A city builder is diffusion plus queueing plus supply-demand equilibrium plus diminishing returns on proximity. A 4X game is Lanchester combat plus polynomial growth plus positive feedback bounded by logistic caps on population.

A few rules for composing them well:

1. **Every system should trace to a feedback-loop diagram.** Classify each loop as positive, negative, or coupled. Mark the gain constants. Most balance problems become obvious once you draw this.

2. **Every parameter should be exposed as a tunable.** The math is universal; the balance lives entirely in the constants. Hardcoding a 1.5 inside a formula is a design decision you will regret.

3. **Every curve should be viewable with its inverse.** For a cost curve, plot `time_to_level(n) = cost(n)/income(n)`. For a drop rate, plot `attempts_for_95%_confidence`. Players feel inverses more than they feel forward curves.

4. **Every choice in the game should pass the interesting-decision test.** Same EV, different variance. Otherwise it is not a choice, it is a checklist.

5. **Source, pool, drain.** Every economy reduces to faucets and sinks. A healthy economy keeps them roughly balanced over time. Persistent imbalance means exponential accumulation or collapse.

The toolkit is small. Twenty primitives cover essentially every shipped simulation, strategy, and roguelite. The work of design is choosing which to use, composing them into loops, and tuning their constants against each other.
