# Touch Dependency Model - API Reference

Complete API documentation for the Touch Dependency Model Python package.

## Table of Contents

1. [TouchDependencyModel](#touchdependencymodel)
2. [FeatureEngineer](#featureengineer)
3. [TDSCalculator](#tdscalculator)
4. [ArchetypeClusterer](#archetypeclusterer)
5. [Models](#models)
6. [Scouting Generators](#scouting-generators)
7. [DataLoader](#dataloader)

---

## TouchDependencyModel

The main interface for player evaluation.

### Import

```python
from tdm import TouchDependencyModel
```

### Constructor

```python
TouchDependencyModel(model_dir: str = "models")
```

**Parameters:**
- `model_dir`: Directory containing saved model files

### Methods

#### load_models

```python
load_models(model_dir: Optional[str] = None) -> TouchDependencyModel
```

Load all trained models from disk.

**Parameters:**
- `model_dir`: Optional override for model directory

**Returns:** self (for method chaining)

**Raises:** `FileNotFoundError` if models not found

#### evaluate_player

```python
evaluate_player(stats: Dict) -> Dict
```

Evaluate a single player and generate full report.

**Parameters:**
- `stats`: Dictionary of player statistics

**Required keys:**
- `FG`: Field goals made (int)
- `FGA`: Field goal attempts (int)
- `FT`: Free throws made (int)
- `FTA`: Free throw attempts (int)
- `PTS`: Points (int)
- `MP`: Minutes played (int)

**Optional keys:**
- `3P`, `3PA`: Three-point makes/attempts
- `2P`, `2PA`: Two-point makes/attempts
- `AST`: Assists
- `TOV`: Turnovers
- `Age`: Player age
- `Pos`: Position
- `Player`: Player name
- `USG%`, `AST%`, `TOV%`: Pre-computed advanced stats

**Returns:** Dictionary containing:

```python
{
    'tds_score': float,           # 0-100 score
    'tds_category': str,          # e.g., "Touch Independent"
    'tds_description': str,       # Category explanation
    'archetype': str,             # e.g., "Sharpshooter"
    'archetype_description': str, # Archetype explanation
    'predicted_ts': float,        # Model predicted TS%
    'actual_ts': float,           # Actual TS%
    'residual': float,            # actual - predicted
    'scouting_summary': str,      # Multi-sentence assessment
    'short_summary': str,         # 1-2 sentence summary
    'gm_recommendations': {
        'deployment': str,
        'acquisition': str,
        'market_value': str,
        'development': str
    },
    'feature_values': Dict[str, float]
}
```

#### evaluate_batch

```python
evaluate_batch(players: List[Dict]) -> List[Dict]
```

Evaluate multiple players.

**Parameters:**
- `players`: List of player stat dictionaries

**Returns:** List of evaluation reports

#### quick_score

```python
quick_score(stats: Dict) -> float
```

Get just the TDS score without full report.

**Parameters:**
- `stats`: Player statistics

**Returns:** TDS score (0-100)

#### get_model_info

```python
get_model_info() -> Dict
```

Get information about loaded models.

**Returns:** Dictionary with model details

### Properties

- `is_loaded`: Boolean indicating if models are loaded

### Example

```python
from tdm import TouchDependencyModel

tdm = TouchDependencyModel()
tdm.load_models()

report = tdm.evaluate_player({
    'FG': 200, 'FGA': 450,
    'FT': 100, 'FTA': 120,
    'PTS': 550, 'MP': 2000,
    '3P': 50, '3PA': 150,
    'AST': 100, 'TOV': 60
})

print(f"TDS: {report['tds_score']}")
print(f"Archetype: {report['archetype']}")
```

---

## FeatureEngineer

Handles feature computation and transformation.

### Import

```python
from tdm.features import FeatureEngineer
```

### Methods

#### compute_ts_percent

```python
compute_ts_percent(fg: float, fga: float, ft: float,
                   fta: float, pts: float) -> float
```

Compute True Shooting Percentage.

**Formula:** `TS% = PTS / (2 * (FGA + 0.44 * FTA))`

#### compute_usg_percent

```python
compute_usg_percent(fga: float, fta: float, tov: float,
                    mp: float, team_fga: float, team_fta: float,
                    team_tov: float, team_mp: float) -> float
```

Compute Usage Percentage.

#### compute_ast_percent

```python
compute_ast_percent(ast: float, mp: float, team_fg: float,
                    fg: float, team_mp: float) -> float
```

Compute Assist Percentage.

#### compute_shot_diet_rates

```python
compute_shot_diet_rates(fga: float, three_pa: float,
                        two_pa: float, fta: float) -> Tuple[float, float, float]
```

Compute shot distribution rates.

**Returns:** Tuple of (3PA_rate, 2PA_rate, FTA_rate)

#### create_feature_matrix

```python
create_feature_matrix(df: pd.DataFrame,
                      use_precomputed: bool = True,
                      fit_scaler: bool = True) -> Tuple[np.ndarray, np.ndarray, List[str]]
```

Create feature matrix from raw data.

**Returns:** Tuple of (X features, y target, feature_names)

#### transform_single_player

```python
transform_single_player(stats: dict) -> np.ndarray
```

Transform single player stats to feature vector.

---

## TDSCalculator

Calculates Touch Dependency Score from model residuals.

### Import

```python
from tdm.scoring import TDSCalculator
```

### Methods

#### calibrate

```python
calibrate(training_residuals: np.ndarray) -> TDSCalculator
```

Calibrate using training data residuals.

#### compute_tds

```python
compute_tds(residual: float) -> float
```

Compute TDS from a single residual.

**Returns:** TDS score (0-100)

#### interpret_tds

```python
interpret_tds(score: float) -> Tuple[str, str]
```

Get interpretation of TDS score.

**Returns:** Tuple of (category_name, description)

#### get_percentile_thresholds

```python
get_percentile_thresholds() -> dict
```

Get residual values at key percentile thresholds.

---

## ArchetypeClusterer

Clusters players into offensive archetypes.

### Import

```python
from tdm.archetypes import ArchetypeClusterer
```

### Constructor

```python
ArchetypeClusterer(n_clusters: int = 12, method: str = 'kmeans')
```

### Methods

#### fit

```python
fit(features: np.ndarray, feature_names: Optional[List[str]] = None) -> ArchetypeClusterer
```

Fit the clustering model.

#### predict_archetype

```python
predict_archetype(features: np.ndarray) -> Tuple[str, int]
```

Predict archetype for a player.

**Returns:** Tuple of (archetype_name, cluster_id)

#### get_archetype_profiles

```python
get_archetype_profiles() -> Dict[str, Dict[str, float]]
```

Get the average profile for each archetype.

### Archetype Names

```python
ARCHETYPE_NAMES = {
    0: "Star Playmaker",
    1: "Volume Scorer",
    2: "Floor General",
    3: "Sharpshooter",
    4: "Reliable Starter",
    5: "Energy Scorer",
    6: "Rim Runner",
    7: "Stretch Big",
    8: "Role Player",
    9: "Defensive Specialist",
    10: "Developing Player",
    11: "Bench Scorer"
}
```

---

## Models

### LinearTSModel

Linear regression for TS% prediction.

```python
from tdm.models import LinearTSModel

model = LinearTSModel()
model.fit(X, y, feature_names)
predictions = model.predict(X)
coefficients = model.get_coefficients()
```

### XGBoostTSModel

XGBoost for TS% prediction.

```python
from tdm.models import XGBoostTSModel

model = XGBoostTSModel()
model.fit(X, y, feature_names, tune_hyperparams=True)
predictions = model.predict(X)
importance = model.get_feature_importance()
```

### EnsembleTSModel

Ensemble combining linear and XGBoost.

```python
from tdm.models import EnsembleTSModel

ensemble = EnsembleTSModel()
ensemble.fit(X, y, use_stacking=True)
predictions = ensemble.predict(X)
residuals = ensemble.compute_final_residuals(X, y)
```

---

## Scouting Generators

### ScoutingSummaryGenerator

```python
from tdm.scouting import ScoutingSummaryGenerator

generator = ScoutingSummaryGenerator()

profile = {
    'usg_pct': 25, 'ast_pct': 18,
    'ts_pct': 0.58, 'tds_score': 65,
    'archetype': 'Star Playmaker'
}

summary = generator.generate_summary(profile)
short = generator.generate_short_summary(profile)
```

### GMRecommendationEngine

```python
from tdm.scouting import GMRecommendationEngine

engine = GMRecommendationEngine()
recommendations = engine.generate_recommendations(profile)
# Returns: {'deployment', 'acquisition', 'market_value', 'development'}
```

---

## DataLoader

### Import

```python
from tdm.data_loader import DataLoader
```

### Methods

#### load_training_data

```python
load_training_data(filepath: Optional[str] = None) -> pd.DataFrame
```

Load and preprocess training data.

#### filter_valid_seasons

```python
filter_valid_seasons(df: pd.DataFrame) -> pd.DataFrame
```

Filter to valid seasons (min minutes, FGA).

**Default thresholds:**
- `MIN_MINUTES_THRESHOLD = 500`
- `MIN_FGA_THRESHOLD = 100`

#### compute_team_aggregates

```python
compute_team_aggregates(df: pd.DataFrame) -> pd.DataFrame
```

Add team-level statistics for advanced stat computation.

---

## CLI Reference

### Evaluate Command

```bash
python tdm_cli.py evaluate \
    --fg 200 --fga 450 \
    --ft 100 --fta 120 \
    --pts 550 --mp 2000 \
    [--3p 50] [--3pa 150] \
    [--ast 100] [--tov 60] \
    [--age 26] [--pos G] \
    [--player "Name"] \
    [--verbose]
```

### Batch Command

```bash
python tdm_cli.py batch \
    --input roster.csv \
    --output reports.csv \
    [--verbose]
```

### Interactive Command

```bash
python tdm_cli.py interactive
```

### Info Command

```bash
python tdm_cli.py info
```

---

## Error Handling

### Common Exceptions

```python
# Models not loaded
ValueError: "Models not loaded. Call load_models() first."

# Models not found
FileNotFoundError: "Model files not found in models/. Run train_model.py first."

# Missing required stats
ValueError: "Missing required stats: ['FT', 'FTA']"

# Invalid values
ValueError: "FGA cannot be zero"
ValueError: "MP cannot be zero"
```

### Best Practices

```python
try:
    report = tdm.evaluate_player(stats)
except ValueError as e:
    print(f"Invalid input: {e}")
except FileNotFoundError:
    print("Please train the model first: python train_model.py")
```
