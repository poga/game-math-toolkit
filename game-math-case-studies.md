# Game Systems Math: Case Studies

Companion to the toolkit. Each section matches one of the ten primitives and shows how shipped games calibrated them. The point is not to copy the constants but to see the range of reasonable values and understand what each choice does to the feel.

---

## 1. Growth and Scaling Curves

### Pokémon XP groups (cubic polynomial)
```
Medium Fast:  XP(level) = level^3
Slow:         XP(level) = (5/4)·level^3
Fast:         XP(level) = (4/5)·level^3
```
At level 100 the Medium Fast group needs exactly 1,000,000 XP. The Slow group needs 25% more. The clean cubic makes the first ten levels almost free and the last ten painful, which matches the designed pace of a story game with a hard cap.

### Civilization 6 city population (mixed polynomial)
```
food_needed(n) = 15 + 8·(n - 1) + (n - 1)^1.5
```
At pop 1→2: 15 food. At pop 10→11: 114 food. At pop 20→21: 249 food. The `n^1.5` term is the key design choice. It creates a super-linear curve that is harsher than linear but far softer than quadratic, which keeps late-game cities growing rather than stalling.

### Dungeons & Dragons 5e (quadratic)
```
XP_total ≈ 500 · level · (level - 1)
```
Roughly quadratic. Gentler than Pokémon's cubic because D&D levels carry much more weight per level (new class features, proficiency bonus jumps) and the designers wanted leveling to stay achievable throughout a long campaign.

### Factorio infinite research (exponential)
```
cost(level) = base · 1.5^level
```
Used for post-endgame infinite sciences. The 1.5 base is chosen to match the roughly exponential way player production scales at that stage. If income grows at `1.5^t` and cost grows at `1.5^t`, the ratio stays flat and each research level always feels the same distance away.

### Civilization 6 housing (piecewise logistic)
```
housing - population ≥ 2:   growth_modifier = 1.0
housing - population = 1:   growth_modifier = 0.5
population - housing ≤ 4:   growth_modifier = 0.25
else:                       growth_modifier = 0.0
```
Not a smooth logistic curve, but the same shape built from four pieces. Players can read the thresholds directly off the UI, which matters more here than analytical smoothness.

**What to take away:** a curve family is a starting point, not an answer. Civ 6's food curve is polynomial with an exponent of 1.5 chosen by playtesting. Pokémon's cube is clean because the cap is hard. Factorio's exponential base matches the slope of player income. Always tune the exponent or base against the opposing curve, not in isolation.

---

## 2. Contest Resolution

### Civilization 6 combat (exponential difference)
```
damage = 30 · e^(Δ/25) · random(0.75, 1.25),   Δ = attacker_CS - defender_CS
```
Equal strength deals 30 HP per round against a 100 HP unit. Damage doubles every 17.3 strength points (from `25 · ln(2)`). A +30 advantage deals 99 damage while taking only 10, which is why flanking and terrain matter so much.

Modifiers stack additively into `Δ`:
```
flanking         +2
Great General    +5
Corps formation  +10
Army formation   +17
```
Additive stacking keeps the design surface readable. Every +5 you can name is worth roughly 1.5× more damage, and players learn this quickly.

### Civilization 5 combat (ratio)
```
damage = 30 · ((((R + 3)/4)^4 + 1) / 2),   R = attacker_CS / defender_CS
```
Same base value of 30, but fed through a ratio rather than a difference. This is why percentage bonuses in Civ 5 had to stack additively onto a base strength before the ratio was computed. The two systems produce similar curves in the middle range but diverge at extremes; Civ 6's difference model is smoother when strength gaps grow large.

### Hearts of Iron 4 (hardness-weighted)
```
attacks = soft_attack · (1 - target_hardness) + hard_attack · target_hardness
hit_chance = 0.40 if attacks > remaining_defense, else 0.10
```
Stats scale with current strength: `effective_attack = base_attack · (current_HP / max_HP)`. Terrain penalties are multiplicative between categories: forest 0.80×, mountain 0.40×, each fort level 0.85×. Stacking these gives brutal compounds: attacking mountains across a river into level-3 forts is near suicide, as intended.

### EU4 (dice plus pip difference)
```
base_damage = 15 + 5 · max(0, dice + attack_pips - defend_pips + leader_diff - terrain)
damage_modifier = attacker_max_morale / defender_max_morale
```
Dice rolls from 0 to 9 give high variance, which is why players dislike small battles. The morale ratio is the real lever: France's +20% national morale produces roughly a 44% effective combat edge, because morale damage scales by the ratio.

**What to take away:** the same "30 base damage" constant appears in both Civ 5 and Civ 6, but one runs it through a ratio and one through an exponential difference. The shape of the mapping matters more than the base constant. Pick difference models when you want additive bonus stacking and smooth behavior at extremes; pick ratio models when bonuses are naturally multiplicative.

---

## 3. Production and Transformation

### Anno 1800 (fixed-ratio chains)
```
Bread:   1 Grain Farm : 1 Flour Mill : 1 Bakery
Bricks:  1 Clay Pit   : 2 Brick Factories
```
Consumption is per-residence, not per-population, which makes ratios stay clean as cities grow. The designers picked cycle times so that every chain has a small integer ratio. That decision is what makes Anno's planning feel like a puzzle rather than a spreadsheet.

### Factorio (throughput and beacon stacking)
```
belt throughput:   yellow 15/s,  red 30/s,  blue 45/s
beacon_bonus = module_effect · distribution_efficiency / √n
productivity:  effective_output = base_output · (1 + Σ bonuses)
```
Belt tiers double neatly, which is a deliberate design choice so players can reason about throughput without a calculator. The `1/√n` beacon falloff in Factorio 2.0 was added precisely to prevent stacked beacon setups from dominating; the square root ensures each additional beacon helps less, which bounds the maximum practical stack.

### Cobb-Douglas in practice
Most games that use multi-input production use exponents chosen empirically rather than economically. A 60/40 split between labor and materials forces players to balance both without making either feel dominant. A 50/50 split makes the two inputs perfectly interchangeable at the margin, which is often too symmetric to be interesting.

**What to take away:** Anno optimized for integer ratios so players can plan in their heads. Factorio optimized for clean doubling on belts and square-root falloff on beacons to bound extreme stacking. The constants are not arbitrary; each one was chosen to support a specific kind of player cognition.

---

## 4. Market and Exchange

### Victoria 3 (bounded elastic pricing)
```
P = P_base · (1 + 0.75 · clamp((buy_orders - sell_orders) / min(buy_orders, sell_orders), -1, +1))
```
Prices range from 25% to 175% of base. The 0.75 multiplier is the maximum swing. The clamp on the ratio is critical: without it, a small seller facing huge demand would produce arbitrarily large prices and the economy would break. Victoria 3 bounds the market signal instead.

Local prices blend market and state:
```
local_price = MAPI · market_price + (1 - MAPI) · state_price
MAPI = market_access · 0.75
market_access = min(1.0, infrastructure / infrastructure_usage)
```
The 0.75 cap on MAPI ensures that even perfect infrastructure only blends 75% toward the market price, which preserves meaningful regional variation. Pop substitution between competing goods shifts at 1–10% per week, capped at 80% market share per good. Those caps prevent market whiplash.

### Base price constants
```
Grain = 20,  Tools = 40
```
These are not arbitrary. They are the anchor points against which all ratios and swings are measured. Choose base prices so that common transactions produce readable numbers and ratios between staple goods tell a recognizable story about scarcity.

**What to take away:** Victoria 3's entire market is held inside a fixed band (25% to 175%) on purpose. A simulation can be deep and still refuse to let the economy explode. Pick your bounds before you pick your curves.

---

## 5. Spatial Fields

### Standard diffusion parameter ranges
```
diffusion coefficient D:   0.1 to 0.3
decay per tick:            0.01 to 0.05
influence spread α:        0.01 to 0.1
```
These are the ranges that produce "readable" spread at typical grid sizes (50–200 cells per side) and tick rates (a few updates per second). Values much higher produce jittery flooding; much lower produce spread that players cannot see.

### Nagel-Schreckenberg traffic
```
randomization probability p ≈ 0.3
maximum flow at critical density ρ_c ≈ 1/(v_max + 1)
```
The 0.3 randomization is the magic ingredient. Without it, traffic is deterministic and jams never form. With it, phantom jams emerge above critical density, which matches real-world traffic and gives city builder players a readable symptom of overcrowded roads.

### SimCity land value
Residential wealth tiers use different sensitivity weights to the same inputs. Luxury housing is highly sensitive to pollution and crime. Low-income housing tolerates more negatives. The sensitivity weights are the design lever, not the raw factors.

**What to take away:** diffusion's magic constants (D around 0.2, decay around 0.02) are not physics, they are tuned for visual readability at game timescales. The Nagel-Schreckenberg randomization of 0.3 is the exact parameter that turns deterministic traffic into the jam behavior players recognize.

---

## 6. Flow and Queueing

### RollerCoaster Tycoon guest patience
```
> 5 min queue:   complaints begin
> 15 min queue:  queue abandonment
guests/hour = cars · trains · capacity · 60 / ride_duration
```
The 5-minute and 15-minute thresholds are the entire design of ride management in RCT. Players are not really solving throughput; they are solving "keep average wait under five minutes." Both numbers were chosen to feel fair to guests without making rides trivial to operate.

### OpenTTD YAPF rail costs
```
slope penalty:          +100
curve penalty:          +1
red signal:             +1,000
red exit signal:        +10,000
depot reverse:          +5,000
signal look-ahead[i] = 500 - 100·i + 5·i^2
```
These are not guesses. Each number reflects how much that penalty should discourage the AI pathfinder from the corresponding behavior. The signal look-ahead formula is quadratic in distance so that distant signals matter less than near ones but never drop to zero, which is why OpenTTD trains plan routes that feel rational instead of myopic.

### Factorio belt tiers as a queueing problem
```
yellow belt: 15/s,  red: 30/s,  blue: 45/s
```
These match Little's Law cleanly with the crafting times of the three assembler tiers, so players can saturate a belt with small integer counts of machines. The design goal was integer answers to "how many machines per belt," not realistic physics.

**What to take away:** RCT's 5/15 patience thresholds and OpenTTD's weirdly-specific penalty numbers do not come from theory. They come from playtesting until the emergent behavior felt right. Treat queueing and pathfinding constants as feel parameters, not physical ones.

---

## 7. Diminishing Returns

### League of Legends armor (hyperbolic)
```
effective = stat / (stat + 100)
```
The constant `k = 100` is the half-effectiveness point. 100 armor gives 50% damage reduction. 200 gives 66.7%. The curve never reaches 100%, and each point of armor adds the same amount of effective HP. That last property is why LoL itemization stays balanced across a huge stat range.

### World of Warcraft soft caps (piecewise)
```
0 – 30%:      100% efficiency
30 – 39%:     90%
39 – 47%:     80%
...
above 66%:    50% efficiency
```
The tiers send a design message: 30% is the target, 66% is the practical ceiling, and the zone in between is available but discouraged. Pure mathematical curves cannot communicate this shape as clearly as a piecewise system.

### Factorio beacon stacking (square-root)
```
effective_bonus_per_beacon = nominal / √n
```
With one beacon, you get 100%. With four, each gives 50%. With sixteen, each gives 25%. The square root was chosen over linear falloff because it lets moderate stacks still be worthwhile (4 beacons is better than 1) while making extreme stacks (16+) hit a wall.

**What to take away:** LoL picked `k = 100` so that the "50% reduction" breakpoint lined up with common itemization. WoW picked exact percentage tiers because players needed to see the breakpoints in the UI. Factorio picked square root for a specific engineering reason. Each formula was chosen against a communication goal.

---

## 8. Feedback Loops

### Against the Storm (coupled dual-bar race)
```
impatience_rate = 0.255 points/min
target:  fill Reputation bar (12 to 18) before Impatience reaches 14
```
Modifiers compound negatively:
```
Human Firekeeper:       -25%
Obsidian Archive up to: -40%
Combined maximum:       -65%
```
Each Reputation gain also reduces Impatience by 1.0 (0.5 at Prestige 14+), which couples the two bars. The feedback structure is: Reputation is positive, Impatience is positive, and Reputation actively drains Impatience. The result is a system where losing feels like a slow grind and winning feels like a cascade, both of which are emotionally correct for the game.

### Hades (positive meta-progression plus negative Heat)
```
effective_difficulty = base · (1 + Σ heat_modifiers)
Hard Labor:            +20% enemy damage per rank (5 ranks)
Lasting Consequences:  -25% healing per rank (4 ranks)
maximum Heat:          63 across 15 pact conditions
```
Mirror upgrades scale linearly (`cost = base · rank`). The Heat system is a negative feedback loop the player controls directly, which is an unusual and clever design choice. Instead of the game rubber-banding against the player, the player selects their own rubber band.

### Mario Kart (catch-up term)
```
item_quality(position) = max_quality · (1 - position/total_players)
```
Direct inverse linear scaling. Last place gets the strongest items with certainty, first place gets the weakest. The formula is simple because it needs to be predictable: players learn that trailing means power items, and that prediction is part of the strategy.

### PID tuning in practice
Most shipped dynamic difficulty systems use only the proportional and integral terms. The derivative term is usually skipped because it amplifies noise in player performance data. Ziegler-Nichols tuning is the starting point; final values are almost always found by playtesting.

**What to take away:** Against the Storm built its entire game around a three-variable coupled feedback triangle. Hades made the negative loop player-selected instead of automatic. Mario Kart kept its catch-up term simple so players could predict and exploit it. Feedback loops are design decisions first, math second.

---

## 9. Probability and Variance Shaping

### Dota 2 PRD constants
```
nominal p       C              max attempts (guaranteed)
10%             0.01475        68
17%             0.03980        26
25%             0.08474        12
```
The 17% value is the famous "bash chance" and the C constant was solved so that the long-run rate is exactly 17%. Three consecutive procs at nominal 17% happen at roughly 1-in-10,000 under PRD, compared to 1-in-200 under true random. Players noticed the difference and the system has not changed in over a decade.

### Slay the Spire (seeded RNG streams)
```
13 independent RNG streams initialized from one 64-bit seed
card rarity: 62% common, 35% uncommon, 3% rare
removal cost: 75 + 25·previous_removals
```
The 13 separate streams are the reason StS runs are deterministic when seeded. Card rarity uses bad-luck protection: the 3% rare rate is pulled forward after unlucky streaks. Card removal escalates economically to prevent infinite deck thinning, which would otherwise break the hypergeometric math.

### Mystery room distribution (cumulative probability)
```
initial: 10% monster, 3% shop, 2% treasure, 85% event
```
Each non-selection adds the base chance cumulatively until triggered, then resets. This guarantees variety without allowing long droughts of any type. It is a pity system applied to content distribution rather than drops.

### Blizzard-style pity
On each miss, the weights of non-guaranteed items decrease by `100 / max_rolls_%`, progressively shifting probability mass toward the guaranteed tier. Players know the pity exists and plan around it; the system is transparent by design.

**What to take away:** Dota 2's PRD constant for 17% is 0.0398, which you can use directly. Slay the Spire's 62/35/3 rarity split and 75+25 removal cost are reference points for any deckbuilder. Mystery room cumulative distribution is a clean technique that generalizes to any place you want variety without droughts.

---

## 10. Decision Value

### Balatro (multiplicative scoring order)
```
Score = Total_Chips · Total_Mult
Order of jokers matters: +Chips, then +Mult, then ×Mult, evaluated left to right
```
Example with chips = 100, base mult = 10:
```
+10 Mult then ×2 Mult:  (10 + 10)·2 = 40  → score 4,000
×2 Mult then +10 Mult:  (10·2) + 10 = 30  → score 3,000
```
The difference is 33%. This is not a bug, it is the core of the decision space. Scaling is quadratic with planet card leveling but becomes exponential when multiplicative jokers stack, which is the only way to hit late-ante scores. Every joker placement is an interesting-decision test.

### Hades Heat (variance vs reward)
```
+20% damage per Hard Labor rank (5 ranks)
-25% healing per Lasting Consequences rank (4 ranks)
maximum total Heat: 63 across 15 pact conditions
```
Each Heat condition shifts the variance profile of the run. Lasting Consequences lowers your expected HP at any given room, which raises run variance. Hard Labor raises damage taken, which amplifies the tail risk of unlucky rooms. Players choose their own risk curve, and the reward scales with it.

### Against the Storm blueprint drafting
Pick 1 of 3 randomized buildings at Reputation thresholds. This is the same hypergeometric logic as deckbuilder card drafting, applied to buildings. Each pick narrows the Pareto front of viable strategies for the current run, which is why the draft is the most memorable decision in each game.

### Sid Meier's principle, quantified
A choice is interesting when `EV_safe ≈ EV_risky` but `Var(safe) ≪ Var(risky)`. Shipped examples:
```
Civ:        attack with odds, or wait a turn
StS:        take the relic with a downside, or skip
Balatro:    re-roll the shop, or buy what is there
Hades:      pick the upgraded boon, or keep the rare one
```
Each of these passes the test. The safe option has similar expected value to the risky one, but the variances differ by a factor of 2 to 10. That factor is the feel of the decision.

**What to take away:** Balatro's +Mult versus ×Mult ordering is the cleanest example in modern design of a decision whose math is visible but whose mastery takes hours. Hades lets the player set their own variance with Heat. Sid Meier's interesting-decision principle becomes a measurable test once you compute variance explicitly.

---

## Cross-cutting observations

A few patterns show up across the case studies that are worth naming.

**Round numbers are chosen, not discovered.** Civ 6's base damage of 30, LoL's armor constant of 100, RCT's patience thresholds of 5 and 15 minutes, Factorio's belt speeds of 15/30/45. None of these are physical constants. Each was chosen so that common computations produce readable results in the player's head.

**Bounds matter more than curves.** Victoria 3 bounds prices to 25–175%. Hades caps Heat at 63. Slay the Spire caps deck thinning via rising removal cost. Factorio caps beacon effectiveness via the square root. The difference between a good system and a broken one is almost always whether the designer put explicit bounds on the tails, not whether the curve is polynomial or exponential in the middle.

**Readable constants beat optimal constants.** Anno 1800's 1:1:1 bread chain is not the most realistic ratio. It is the ratio that lets players plan without a calculator. Dota 2 publishes its PRD constants. Slay the Spire's 62/35/3 split is round enough to memorize. Designers repeatedly choose legibility over precision.

**Feedback loop topology is the real design.** Against the Storm's dual-bar race, Hades' Heat system, Victoria 3's market, Civilization's city growth: each one is defined more by which loops are positive, which are negative, and how they couple, than by the specific curves inside any one loop. When tuning a system, draw the loop diagram first.

Use these as reference points. The toolkit gives you the primitives; these case studies show what reasonable constants look like when a shipped game has tuned them against real players. Your numbers will be different, but the orders of magnitude and the bounding strategies should feel familiar.
