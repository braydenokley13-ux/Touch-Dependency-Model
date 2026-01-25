#!/usr/bin/env python3
"""
Touch Dependency Model - Command Line Interface

Usage:
    python tdm_cli.py evaluate --fg 373 --fga 1024 --ft 285 --fta 374 --pts 1031 --mp 2800
    python tdm_cli.py batch --input roster.csv --output reports.csv
    python tdm_cli.py interactive
    python tdm_cli.py info
"""

import argparse
import sys
import csv
from pathlib import Path
from typing import Optional


def get_tdm():
    """Get initialized TouchDependencyModel."""
    from tdm import TouchDependencyModel
    tdm = TouchDependencyModel()
    tdm.load_models()
    return tdm


def cmd_evaluate(args):
    """Evaluate a single player from command line arguments."""
    tdm = get_tdm()

    stats = {
        'FG': args.fg,
        'FGA': args.fga,
        'FT': args.ft,
        'FTA': args.fta,
        'PTS': args.pts,
        'MP': args.mp,
        '3P': args.three_p or 0,
        '3PA': args.three_pa or 0,
        'AST': args.ast or 0,
        'TOV': args.tov or 0,
        'Age': args.age,
        'Pos': args.pos,
        'Player': args.player or 'Player'
    }

    # Add optional advanced stats
    if args.usg:
        stats['USG%'] = args.usg
    if args.ast_pct:
        stats['AST%'] = args.ast_pct

    try:
        report = tdm.evaluate_player(stats)
        print_report(report, verbose=args.verbose)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_batch(args):
    """Process a batch of players from CSV."""
    tdm = get_tdm()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Read input CSV
    with open(input_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        players = list(reader)

    print(f"Processing {len(players)} players...")

    results = []
    for i, player in enumerate(players):
        # Convert string values to appropriate types
        stats = {}
        for key, value in player.items():
            if value == '' or value is None:
                continue
            try:
                # Try int first, then float
                if '.' in str(value):
                    stats[key] = float(value)
                else:
                    stats[key] = int(value)
            except ValueError:
                stats[key] = value

        try:
            report = tdm.evaluate_player(stats)
            result = {
                'Player': stats.get('Player', f'Player_{i}'),
                'TDS_Score': report['tds_score'],
                'TDS_Category': report['tds_category'],
                'Archetype': report['archetype'],
                'Predicted_TS': report['predicted_ts'],
                'Actual_TS': report['actual_ts'],
                'Residual': report['residual'],
                'Short_Summary': report['short_summary']
            }
            results.append(result)

            if args.verbose:
                print(f"  [{i+1}/{len(players)}] {result['Player']}: TDS={result['TDS_Score']}")

        except Exception as e:
            print(f"  Warning: Failed to process player {i}: {e}", file=sys.stderr)
            continue

    # Write output
    output_path = Path(args.output)
    if results:
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print(f"Results written to {output_path}")
        print(f"Successfully processed {len(results)}/{len(players)} players")
    else:
        print("No results to write", file=sys.stderr)
        sys.exit(1)


def cmd_interactive(args):
    """Interactive mode for entering player stats."""
    tdm = get_tdm()

    print("=" * 60)
    print("Touch Dependency Model - Interactive Mode")
    print("=" * 60)
    print("Enter player statistics or 'quit' to exit")
    print()

    while True:
        try:
            print("-" * 40)
            player_name = input("Player name (or 'quit'): ").strip()
            if player_name.lower() in ('quit', 'q', 'exit'):
                break

            # Get required stats
            fg = int(input("FG (field goals made): "))
            fga = int(input("FGA (field goal attempts): "))
            ft = int(input("FT (free throws made): "))
            fta = int(input("FTA (free throw attempts): "))
            pts = int(input("PTS (points): "))
            mp = int(input("MP (minutes played): "))

            # Get optional stats
            print("\nOptional stats (press Enter to skip):")

            three_p_str = input("3P (three-pointers made): ").strip()
            three_p = int(three_p_str) if three_p_str else 0

            three_pa_str = input("3PA (three-point attempts): ").strip()
            three_pa = int(three_pa_str) if three_pa_str else 0

            ast_str = input("AST (assists): ").strip()
            ast = int(ast_str) if ast_str else 0

            tov_str = input("TOV (turnovers): ").strip()
            tov = int(tov_str) if tov_str else 0

            age_str = input("Age: ").strip()
            age = int(age_str) if age_str else None

            pos = input("Position (G/F/C/etc): ").strip() or None

            stats = {
                'Player': player_name,
                'FG': fg, 'FGA': fga,
                'FT': ft, 'FTA': fta,
                'PTS': pts, 'MP': mp,
                '3P': three_p, '3PA': three_pa,
                'AST': ast, 'TOV': tov,
                'Age': age, 'Pos': pos
            }

            print("\nAnalyzing...")
            report = tdm.evaluate_player(stats)
            print()
            print_report(report, verbose=True)

        except ValueError as e:
            print(f"\nInvalid input: {e}. Please enter numeric values.\n")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

    print("\nGoodbye!")


def cmd_info(args):
    """Display model information."""
    tdm = get_tdm()
    info = tdm.get_model_info()

    print("=" * 60)
    print("Touch Dependency Model - Model Information")
    print("=" * 60)
    print(f"\nStatus: {info['status']}")
    print(f"Model Directory: {info['model_dir']}")

    print(f"\nFeatures ({len(info['feature_names'])}):")
    for name in info['feature_names']:
        print(f"  - {name}")

    if info['archetypes']:
        print(f"\nArchetypes ({len(info['archetypes'])}):")
        for archetype in info['archetypes']:
            print(f"  - {archetype}")

    if info['ensemble_weights']:
        w_linear, w_xgb = info['ensemble_weights']
        print(f"\nEnsemble Weights:")
        print(f"  Linear: {w_linear:.2f}")
        print(f"  XGBoost: {w_xgb:.2f}")

    if info['tds_distribution']:
        dist = info['tds_distribution']
        print(f"\nTDS Calibration Distribution:")
        print(f"  Samples: {dist['n_samples']}")
        print(f"  Mean Residual: {dist['mean']:.4f}")
        print(f"  Std Dev: {dist['std']:.4f}")


def print_report(report: dict, verbose: bool = False):
    """Print a formatted report."""
    print("=" * 60)
    print("PLAYER EVALUATION REPORT")
    print("=" * 60)

    print(f"\nTDS Score: {report['tds_score']}")
    print(f"Category: {report['tds_category']}")
    print(f"Archetype: {report['archetype']}")

    print(f"\nPredicted TS%: {report['predicted_ts']:.3f}")
    print(f"Actual TS%:    {report['actual_ts']:.3f}")
    print(f"Residual:      {report['residual']:+.3f}")

    print(f"\n--- Scouting Summary ---")
    # Word wrap the summary
    summary = report['scouting_summary']
    words = summary.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 <= 70:
            line = f"{line} {word}".strip()
        else:
            print(line)
            line = word
    if line:
        print(line)

    if verbose:
        print(f"\n--- GM Recommendations ---")
        recs = report['gm_recommendations']
        print(f"DEPLOYMENT: {recs['deployment']}")
        print(f"ACQUISITION: {recs['acquisition']}")
        print(f"MARKET VALUE: {recs['market_value']}")
        print(f"DEVELOPMENT: {recs['development']}")

        print(f"\n--- Feature Values ---")
        for key, value in report['feature_values'].items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")

    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Touch Dependency Model - Player Evaluation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Evaluate single player:
    python tdm_cli.py evaluate --fg 373 --fga 1024 --ft 285 --fta 374 --pts 1031 --mp 2800

  Batch process CSV:
    python tdm_cli.py batch --input roster.csv --output reports.csv

  Interactive mode:
    python tdm_cli.py interactive

  Show model info:
    python tdm_cli.py info
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Evaluate command
    eval_parser = subparsers.add_parser('evaluate', help='Evaluate a single player')
    eval_parser.add_argument('--fg', type=int, required=True, help='Field goals made')
    eval_parser.add_argument('--fga', type=int, required=True, help='Field goal attempts')
    eval_parser.add_argument('--ft', type=int, required=True, help='Free throws made')
    eval_parser.add_argument('--fta', type=int, required=True, help='Free throw attempts')
    eval_parser.add_argument('--pts', type=int, required=True, help='Points')
    eval_parser.add_argument('--mp', type=int, required=True, help='Minutes played')
    eval_parser.add_argument('--3p', dest='three_p', type=int, help='Three-pointers made')
    eval_parser.add_argument('--3pa', dest='three_pa', type=int, help='Three-point attempts')
    eval_parser.add_argument('--ast', type=int, help='Assists')
    eval_parser.add_argument('--tov', type=int, help='Turnovers')
    eval_parser.add_argument('--age', type=int, help='Player age')
    eval_parser.add_argument('--pos', type=str, help='Position')
    eval_parser.add_argument('--player', type=str, help='Player name')
    eval_parser.add_argument('--usg', type=float, help='Usage percentage')
    eval_parser.add_argument('--ast-pct', type=float, help='Assist percentage')
    eval_parser.add_argument('-v', '--verbose', action='store_true', help='Show full report')

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Process multiple players from CSV')
    batch_parser.add_argument('--input', '-i', required=True, help='Input CSV file')
    batch_parser.add_argument('--output', '-o', required=True, help='Output CSV file')
    batch_parser.add_argument('-v', '--verbose', action='store_true', help='Show progress')

    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Interactive evaluation mode')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show model information')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == 'evaluate':
        cmd_evaluate(args)
    elif args.command == 'batch':
        cmd_batch(args)
    elif args.command == 'interactive':
        cmd_interactive(args)
    elif args.command == 'info':
        cmd_info(args)


if __name__ == '__main__':
    main()
