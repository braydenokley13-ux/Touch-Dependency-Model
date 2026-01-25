#!/usr/bin/env python3
"""
Touch Dependency Model - Training Script

One-time script to train all models and save to disk.
Run once, then use saved models forever (or retrain when new data available).

Usage:
    python train_model.py
    python train_model.py --data-path data/Seasons_Stats.csv
    python train_model.py --tune-xgb  # Enable XGBoost hyperparameter tuning
"""

import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


def train_all_models(data_path: str = "data/Seasons_Stats.csv",
                     model_dir: str = "models",
                     tune_xgb: bool = False,
                     verbose: bool = True):
    """
    Train all models and save to disk.

    Args:
        data_path: Path to training data CSV
        model_dir: Directory to save models
        tune_xgb: Whether to tune XGBoost hyperparameters
        verbose: Print progress messages
    """
    from tdm.data_loader import DataLoader
    from tdm.features import FeatureEngineer
    from tdm.models import LinearTSModel, XGBoostTSModel, EnsembleTSModel
    from tdm.archetypes import ArchetypeClusterer
    from tdm.scoring import TDSCalculator

    model_path = Path(model_dir)
    model_path.mkdir(parents=True, exist_ok=True)

    if verbose:
        print("=" * 60)
        print("TOUCH DEPENDENCY MODEL - TRAINING")
        print("=" * 60)
        print(f"\nData path: {data_path}")
        print(f"Model directory: {model_dir}")
        print(f"XGBoost tuning: {'enabled' if tune_xgb else 'disabled'}")
        print()

    # Step 1: Load and preprocess data
    if verbose:
        print("[1/7] Loading data...")

    loader = DataLoader()
    df = loader.load_training_data(data_path)

    if verbose:
        print(f"  Loaded {len(df)} player-seasons")
        print(f"  Years: {df['Year'].min()} - {df['Year'].max()}")
        print(f"  Unique players: {df['Player'].nunique()}")

    # Step 2: Engineer features
    if verbose:
        print("\n[2/7] Engineering features...")

    engineer = FeatureEngineer()
    X, y, feature_names = engineer.create_feature_matrix(df, use_precomputed=True)

    if verbose:
        print(f"  Features: {len(feature_names)}")
        print(f"  Feature names: {feature_names}")
        print(f"  Training samples: {len(y)}")
        print(f"  Target (TS%) range: {y.min():.3f} - {y.max():.3f}")

    # Step 3: Train linear model
    if verbose:
        print("\n[3/7] Training linear model...")

    linear_model = LinearTSModel()
    linear_model.fit(X, y, feature_names)
    linear_cv = linear_model.cross_validate(X, y)

    if verbose:
        print(f"  Cross-validation RMSE: {linear_cv['rmse_mean']:.4f} (+/- {linear_cv['rmse_std']:.4f})")
        print(f"  Cross-validation R2: {linear_cv['r2_mean']:.4f} (+/- {linear_cv['r2_std']:.4f})")
        print(f"  Best alpha: {linear_cv['best_alpha']:.4f}")

        # Show top coefficients
        coefs = linear_model.get_coefficients()
        print("  Top coefficients:")
        for i, (name, coef) in enumerate(coefs.items()):
            if i >= 5 or name == 'intercept':
                continue
            print(f"    {name}: {coef:.4f}")

    # Step 4: Train XGBoost model
    if verbose:
        print("\n[4/7] Training XGBoost model...")
        if tune_xgb:
            print("  (Hyperparameter tuning enabled - this may take a few minutes)")

    xgb_model = XGBoostTSModel()
    xgb_model.fit(X, y, feature_names, tune_hyperparams=tune_xgb)
    xgb_cv = xgb_model.cross_validate(X, y)

    if verbose:
        print(f"  Cross-validation RMSE: {xgb_cv['rmse_mean']:.4f} (+/- {xgb_cv['rmse_std']:.4f})")
        print(f"  Cross-validation R2: {xgb_cv['r2_mean']:.4f} (+/- {xgb_cv['r2_std']:.4f})")

        # Show feature importance
        importance = xgb_model.get_feature_importance()
        print("  Top feature importance:")
        for i, (name, imp) in enumerate(importance.items()):
            if i >= 5:
                break
            print(f"    {name}: {imp:.4f}")

    # Step 5: Create ensemble and compute residuals
    if verbose:
        print("\n[5/7] Creating ensemble model...")

    ensemble = EnsembleTSModel(linear_model, xgb_model)
    ensemble.fit(X, y, feature_names, use_stacking=True, tune_xgb=False)

    # Evaluate all models
    metrics = ensemble.evaluate(X, y)
    residuals = ensemble.compute_final_residuals(X, y)

    if verbose:
        print(f"  Ensemble weights: Linear={ensemble.weights[0]:.2f}, XGBoost={ensemble.weights[1]:.2f}")
        print("\n  Model Performance Comparison:")
        print("  Model      | RMSE   | R2     | MAE")
        print("  -----------|--------|--------|-------")
        for name, m in metrics.items():
            print(f"  {name:10} | {m['rmse']:.4f} | {m['r2']:.4f} | {m['mae']:.4f}")

    # Step 6: Calibrate TDS calculator
    if verbose:
        print("\n[6/7] Calibrating TDS calculator...")

    tds_calc = TDSCalculator()
    tds_calc.calibrate(residuals)
    tds_stats = tds_calc.get_distribution_stats()

    if verbose:
        print(f"  Calibration samples: {tds_stats['n_samples']}")
        print(f"  Residual mean: {tds_stats['mean']:.4f}")
        print(f"  Residual std: {tds_stats['std']:.4f}")
        print(f"  Residual range: [{tds_stats['min']:.4f}, {tds_stats['max']:.4f}]")

        # Show percentile thresholds
        thresholds = tds_calc.get_percentile_thresholds()
        print("  Percentile thresholds (residual):")
        for p, val in thresholds.items():
            print(f"    {p}th: {val:.4f}")

    # Step 7: Cluster archetypes
    if verbose:
        print("\n[7/7] Clustering player archetypes...")

    # Prepare clustering features
    # We need to compute TDS for each player first
    tds_scores = tds_calc.compute_tds_batch(residuals)

    # Build clustering feature matrix
    clustering_df = pd.DataFrame()

    # Get original feature values (unscaled)
    if 'USG%' in df.columns:
        clustering_df['USG%'] = df.loc[df.index[:len(tds_scores)], 'USG%'].values
    else:
        # Estimate from scaled features
        clustering_df['USG%'] = 20  # Default

    if 'AST%' in df.columns:
        clustering_df['AST%'] = df.loc[df.index[:len(tds_scores)], 'AST%'].values
    else:
        clustering_df['AST%'] = 15

    if 'TS%' in df.columns:
        clustering_df['TS%'] = df.loc[df.index[:len(tds_scores)], 'TS%'].values
    else:
        clustering_df['TS%'] = y

    clustering_df['TDS'] = tds_scores

    # Shot diet rates
    df_subset = df.iloc[:len(tds_scores)]
    clustering_df['3PA_rate'] = (df_subset['3PA'] / df_subset['FGA'].replace(0, 1)).values
    clustering_df['FTA_rate'] = (df_subset['FTA'] / df_subset['FGA'].replace(0, 1)).values

    # Handle missing values
    clustering_df = clustering_df.fillna(clustering_df.median())

    clustering_features = clustering_df.values

    # Fit clusterer
    clusterer = ArchetypeClusterer(n_clusters=12, method='kmeans')
    clusterer.fit(clustering_features, feature_names=clustering_df.columns.tolist())

    if verbose:
        print(f"  Identified {len(clusterer.cluster_labels_)} archetypes:")
        for cluster_id, archetype in sorted(clusterer.cluster_labels_.items()):
            count = np.sum(clusterer.model.labels_ == cluster_id)
            print(f"    [{cluster_id}] {archetype}: {count} players")

    # Save all models
    if verbose:
        print("\n" + "=" * 60)
        print("SAVING MODELS")
        print("=" * 60)

    # Save individual components
    engineer.save(model_path / 'feature_engineer.pkl')
    linear_model.save(model_path / 'linear_model.pkl')
    xgb_model.save(model_path / 'xgboost_model.pkl')
    ensemble.save(model_path / 'ensemble_weights.pkl')
    tds_calc.save(model_path / 'tds_calculator.pkl')
    clusterer.save(model_path / 'clusterer.pkl')

    if verbose:
        print(f"\nSaved models to {model_path}/:")
        for f in model_path.glob('*.pkl'):
            size_kb = f.stat().st_size / 1024
            print(f"  {f.name}: {size_kb:.1f} KB")

    # Save training residuals for reference
    residuals_df = pd.DataFrame({
        'Player': df.iloc[:len(residuals)]['Player'].values,
        'Year': df.iloc[:len(residuals)]['Year'].values,
        'Actual_TS': y,
        'Predicted_TS': ensemble.predict(X),
        'Residual': residuals,
        'TDS': tds_scores
    })
    residuals_df.to_csv(model_path / 'training_residuals.csv', index=False)

    if verbose:
        print(f"  training_residuals.csv: {len(residuals_df)} rows")

    # Generate summary report
    if verbose:
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE")
        print("=" * 60)

        print(f"\nFinal Model Performance:")
        print(f"  Ensemble RMSE: {metrics['ensemble']['rmse']:.4f}")
        print(f"  Ensemble R2: {metrics['ensemble']['r2']:.4f}")

        print(f"\nTDS Distribution:")
        print(f"  Mean: {np.mean(tds_scores):.1f}")
        print(f"  Std: {np.std(tds_scores):.1f}")
        print(f"  Min: {np.min(tds_scores):.1f}")
        print(f"  Max: {np.max(tds_scores):.1f}")

        print(f"\nTraining completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nTo use the model:")
        print("  from tdm import TouchDependencyModel")
        print("  tdm = TouchDependencyModel()")
        print("  tdm.load_models()")
        print("  report = tdm.evaluate_player({'FG': 100, 'FGA': 250, ...})")

    return {
        'metrics': metrics,
        'tds_stats': tds_stats,
        'n_samples': len(y),
        'n_features': len(feature_names),
        'model_dir': str(model_path)
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Train Touch Dependency Model',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--data-path', '-d',
        default='data/Seasons_Stats.csv',
        help='Path to training data CSV'
    )

    parser.add_argument(
        '--model-dir', '-m',
        default='models',
        help='Directory to save trained models'
    )

    parser.add_argument(
        '--tune-xgb',
        action='store_true',
        help='Enable XGBoost hyperparameter tuning (slower but potentially better)'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress messages'
    )

    args = parser.parse_args()

    try:
        results = train_all_models(
            data_path=args.data_path,
            model_dir=args.model_dir,
            tune_xgb=args.tune_xgb,
            verbose=not args.quiet
        )

        if not args.quiet:
            print("\nTraining successful!")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nMake sure the data file exists at the specified path.")
        return 1

    except Exception as e:
        print(f"Error during training: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
