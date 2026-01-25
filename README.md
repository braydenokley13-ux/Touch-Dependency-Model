# Touch Dependency Model (TDM)

A production-ready ML system for evaluating player touch dependency in basketball.

## Overview

The Touch Dependency Model (TDM) helps scouts and GMs understand how a player's offensive efficiency scales with different roles. Players with **high touch dependency** need consistent offensive involvement to be effective, while **scalable** players maintain efficiency regardless of role.

## Features

- **Python Package**: Programmatic access for integration into analytics pipelines
- **Command-Line Tool**: Quick evaluations from the terminal
- **Web Application**: Beautiful browser-based GUI with Streamlit
- **12 Player Archetypes**: Automatic classification into meaningful categories
- **Scouting Reports**: Natural language summaries for non-technical users
- **GM Recommendations**: Actionable insights for deployment, acquisition, and development

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Touch-Dependency-Model.git
cd Touch-Dependency-Model

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Train the Model (First Time Only)

```bash
python train_model.py
```

This trains all models on the historical data and saves them to the `models/` directory.

### 2. Evaluate Players

#### Python API

```python
from tdm import TouchDependencyModel

# Initialize and load models
tdm = TouchDependencyModel()
tdm.load_models()

# Evaluate a player
report = tdm.evaluate_player({
    'Player': 'Sample Player',
    'FG': 373,
    'FGA': 1024,
    'FT': 285,
    'FTA': 374,
    '3P': 0,
    '3PA': 0,
    'AST': 247,
    'MP': 2800,
    'PTS': 1031,
    'TOV': 150,
    'Age': 25,
    'Pos': 'G'
})

print(f"TDS Score: {report['tds_score']}")
print(f"Archetype: {report['archetype']}")
print(f"\nScouting Summary:\n{report['scouting_summary']}")
```

#### Command Line

```bash
# Single player evaluation
python tdm_cli.py evaluate \
    --fg 373 --fga 1024 \
    --ft 285 --fta 374 \
    --pts 1031 --mp 2800 \
    --ast 247 --tov 150 \
    --verbose

# Batch processing
python tdm_cli.py batch --input roster.csv --output reports.csv

# Interactive mode
python tdm_cli.py interactive
```

#### Web Application

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Understanding the Output

### TDS Score (0-100)

| Score | Category | Meaning |
|-------|----------|---------|
| 80-100 | Highly Scalable | Can thrive in any role |
| 70-80 | Touch Independent | Efficient regardless of role |
| 60-70 | Slightly Scalable | Adapts well to varied roles |
| 50-60 | Neutral | Stable but may need consistency |
| 40-50 | Slightly Dependent | Minor drops in reduced roles |
| 30-40 | Touch Dependent | Performs best with consistent role |
| 0-30 | Highly Touch Dependent | Needs specific role to be effective |

### The 12 Archetypes

1. **Star Playmaker** - Creates offense for self and others at high volume
2. **Volume Scorer** - Takes lots of shots and carries scoring load
3. **Floor General** - Primary ball handler who makes teammates better
4. **Sharpshooter** - Elite three-point shooter who spaces the floor
5. **Reliable Starter** - Dependable two-way player with no major weaknesses
6. **Energy Scorer** - Brings instant offense and energy
7. **Rim Runner** - Scores at the basket off cuts and rolls
8. **Stretch Big** - Big man who can shoot from outside
9. **Role Player** - Does multiple things well without starring
10. **Defensive Specialist** - Primary value is on defense
11. **Developing Player** - Still growing into their role
12. **Bench Scorer** - Provides scoring punch off the bench

## Project Structure

```
Touch-Dependency-Model/
├── data/
│   └── Seasons_Stats.csv       # Training data
├── models/                      # Saved models (generated)
├── tdm/                         # Main package
│   ├── __init__.py
│   ├── predictor.py            # Main TDM class
│   ├── features.py             # Feature engineering
│   ├── scoring.py              # TDS calculation
│   ├── archetypes.py           # Player clustering
│   ├── data_loader.py          # Data utilities
│   ├── models/                 # ML models
│   └── scouting/               # Language generation
├── tests/                       # Test suite
├── train_model.py              # Training script
├── tdm_cli.py                  # CLI interface
├── app.py                      # Streamlit web app
├── requirements.txt
├── README.md
├── METHODOLOGY.md
└── API_REFERENCE.md
```

## Required Statistics

**Required:**
- FG: Field goals made
- FGA: Field goal attempts
- FT: Free throws made
- FTA: Free throw attempts
- PTS: Points
- MP: Minutes played

**Optional (improve accuracy):**
- 3P, 3PA: Three-point makes/attempts
- AST: Assists
- TOV: Turnovers
- Age: Player age
- Pos: Position (G/F/C)
- USG%, AST%, TOV%: Pre-computed advanced stats

## Model Performance

- **Ensemble RMSE**: ~0.025 (2.5 percentage points TS%)
- **R-squared**: ~0.45 (explains 45% of efficiency variance)
- **Training samples**: 15,000+ player-seasons

## Testing

```bash
pytest tests/ -v
```

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Basketball-Reference for historical statistics data
- Scikit-learn, XGBoost, and Streamlit communities
