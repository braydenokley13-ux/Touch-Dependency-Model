# Touch Dependency Model - Methodology Guide

A comprehensive guide for GMs, scouts, and analysts on understanding and using the Touch Dependency Model.

## Table of Contents

1. [What is Touch Dependency?](#what-is-touch-dependency)
2. [How TDS Works](#how-tds-works)
3. [Interpreting the Score](#interpreting-the-score)
4. [Understanding Archetypes](#understanding-archetypes)
5. [Using TDM for Roster Decisions](#using-tdm-for-roster-decisions)
6. [Case Studies](#case-studies)
7. [Limitations](#limitations)

---

## What is Touch Dependency?

Touch Dependency measures how much a player's offensive efficiency depends on having consistent offensive involvement (touches, shots, ball handling time).

### High Touch Dependency (Low TDS)

Players who need:
- Consistent shot volume to find rhythm
- Regular ball handling to stay engaged
- Specific plays designed for them
- A defined role that doesn't change

**Risk**: Efficiency drops significantly when usage decreases

### Low Touch Dependency (High TDS)

Players who can:
- Maintain efficiency across varied roles
- Perform well with fewer touches
- Add value without needing plays called for them
- Seamlessly fit into different offensive systems

**Value**: "Plug and play" - valuable to any roster construction

---

## How TDS Works

### Step 1: Feature Engineering

We compute key metrics from raw statistics:

| Metric | What It Measures |
|--------|-----------------|
| USG% | Share of team possessions used |
| AST% | Percentage of teammate field goals assisted |
| TS% | Overall scoring efficiency |
| 3PA Rate | Percentage of shots from three |
| FTA Rate | Free throw attempts relative to field goal attempts |
| TOV% | Turnover rate |

### Step 2: Efficiency Prediction

An ensemble model (combining Linear Regression and XGBoost) predicts what a player's True Shooting % **should be** based on their:
- Usage rate (higher usage typically means lower efficiency)
- Playmaking burden (passing duties can reduce personal scoring efficiency)
- Shot selection (three-point heavy vs. paint-focused)
- Age and position

### Step 3: Residual Analysis

We compare **actual efficiency** to **predicted efficiency**:

```
Residual = Actual TS% - Predicted TS%
```

- **Positive residual**: Player is more efficient than expected
- **Negative residual**: Player is less efficient than expected

### Step 4: TDS Calculation

The residual is converted to a 0-100 percentile score:

- TDS 50 = Average (efficiency matches expectation)
- TDS 75 = Better than 75% of players
- TDS 25 = Worse than 75% of players

---

## Interpreting the Score

### TDS Score Breakdown

| Score | Category | Profile | GM Implication |
|-------|----------|---------|----------------|
| 80-100 | Highly Scalable | Exceeds efficiency expectations consistently | Premium acquisition target |
| 70-80 | Touch Independent | Efficient in any role | Safe addition to any roster |
| 60-70 | Slightly Scalable | Adapts well to changes | Good fit for contenders |
| 50-60 | Neutral | Performs as expected | Standard value |
| 40-50 | Slightly Dependent | Minor efficiency drops possible | Needs role consistency |
| 30-40 | Touch Dependent | Needs regular involvement | Specific fit required |
| 0-30 | Highly Touch Dependent | Efficiency suffers in reduced roles | High risk for role change |

### What TDS Does NOT Measure

- Overall talent level (a 50 TDS player isn't necessarily average)
- Defense or non-offensive contributions
- Intangibles (leadership, clutch performance)
- Future potential

---

## Understanding Archetypes

### The 12 Archetypes

#### Primary Creators

**1. Star Playmaker**
- High USG%, high AST%, high TS%
- Creates for self and others at volume
- Examples: Elite point guards who can also score

**2. Volume Scorer**
- High USG%, lower AST%
- Primary scoring option
- Value tied to shot-making ability

**3. Floor General**
- Lower USG%, very high AST%
- Pass-first playmaker
- Orchestrates offense for others

#### Shooting Specialists

**4. Sharpshooter**
- High 3PA rate, high TS%, low USG%
- Catch-and-shoot specialist
- Provides spacing and gravity

**5. Stretch Big**
- Big man with three-point shooting
- Opens driving lanes for teammates
- Modern NBA value archetype

#### Role Players

**6. Reliable Starter**
- Balanced profile, solid efficiency
- No major weaknesses
- Dependable two-way contributor

**7. Role Player**
- Does multiple things well
- Complements stars
- System-flexible

**8. Bench Scorer**
- Scoring punch off the bench
- Leads second unit offense
- Spark plug value

#### Specialists

**9. Energy Scorer**
- Instant offense in limited minutes
- Fast-break value
- Momentum-changing ability

**10. Rim Runner**
- Low 3PA rate, high FTA rate
- Finishes at basket off rolls/cuts
- Pairs well with playmakers

**11. Defensive Specialist**
- Low offensive usage
- Primary value is defensive
- Role player archetype

**12. Developing Player**
- Inconsistent efficiency
- High variance in performance
- Potential upside

---

## Using TDM for Roster Decisions

### Acquisition Strategy

**When to Target High TDS Players:**
- Building around a ball-dominant star
- Adding "finishing touches" to a contender
- Limited cap space (maximize value per dollar)

**When TDS Matters Less:**
- Acquiring a franchise cornerstone
- Developing young talent
- Defense-first acquisitions

### Roster Construction

**Optimal Mix:**
- 1-2 Star Playmakers or Volume Scorers (carries offense)
- 2-3 High TDS role players (scalable depth)
- Specialists based on team needs

**Red Flags:**
- Too many low-TDS players competing for touches
- High-TDS player forced into high-usage role
- Low-TDS player expected to reduce role

### Trade Evaluation

Use TDS to identify:
1. **Undervalued**: High TDS player on team with ball-dominant star
2. **Overvalued**: Low TDS player with inflated stats from high usage
3. **Risk**: Low TDS player being traded to reduced-role situation

---

## Case Studies

### Case Study 1: The Undervalued Sharpshooter

**Profile:**
- TDS: 72 (Touch Independent)
- Archetype: Sharpshooter
- Current Role: 12 PPG on 18% USG

**Analysis:**
Despite modest counting stats, the high TDS indicates this player would maintain (or improve) efficiency as a third option on a contender. The market likely undervalues this player based on raw points.

**Recommendation:** Acquire below market value for playoff rotation.

### Case Study 2: The Risky Star Trade

**Profile:**
- TDS: 38 (Touch Dependent)
- Archetype: Volume Scorer
- Current Role: 25 PPG on 32% USG

**Analysis:**
Impressive counting stats mask touch dependency. If traded to join another star, efficiency likely drops. The 32% usage inflates his scoring; at 22% USG, efficiency could fall significantly.

**Recommendation:** Proceed with caution. This player needs to be "the guy."

### Case Study 3: The Development Decision

**Profile:**
- TDS: 58 (Neutral)
- Archetype: Developing Player
- Current Role: 8 PPG on 15% USG, age 22

**Analysis:**
Neutral TDS at low usage is promising - efficiency isn't artificially inflated. As role expands, efficiency should remain stable. Worth investing development resources.

**Recommendation:** Increase role gradually; monitor TDS changes.

---

## Limitations

### What TDM Cannot Do

1. **Predict the future**: TDS reflects historical performance, not trajectory
2. **Account for injuries**: Pre/post-injury players may have different TDS
3. **Measure defense**: A low-TDS defensive specialist has value not captured
4. **Evaluate in isolation**: Context (team, system, era) matters

### When to Use Caution

- **Small sample sizes**: Less than 1000 minutes may be noisy
- **Role changes mid-season**: TDS may lag reality
- **System-dependent players**: Some coaches unlock efficiency differently
- **Injury recovery**: Players may perform differently post-injury

### Best Practices

1. Use TDS as one input among many
2. Combine with film study and traditional scouting
3. Consider the specific role being projected
4. Update evaluations as new data becomes available

---

## Appendix: Technical Details

### Model Architecture

- **Linear Model**: Ridge regression with cross-validated regularization
- **Nonlinear Model**: XGBoost gradient boosting
- **Ensemble**: Weighted average (30% linear, 70% XGBoost typical)

### Feature Importance (Typical)

1. USG% (most important)
2. Age
3. 3PA Rate
4. AST%
5. FTA Rate

### Validation Metrics

- Cross-validation RMSE: ~0.025 TS%
- R-squared: ~0.45
- TDS distribution: Mean 50, StdDev 15-18
