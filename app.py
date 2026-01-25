#!/usr/bin/env python3
"""
Touch Dependency Model - Streamlit Web Application

A beautiful, interactive web interface for evaluating player touch dependency.

Usage:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Touch Dependency Model",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .archetype-badge {
        background-color: #1f77b4;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        font-weight: bold;
    }
    .summary-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    """Load the TDM model (cached)."""
    try:
        from tdm import TouchDependencyModel
        tdm = TouchDependencyModel()
        tdm.load_models()
        return tdm, None
    except FileNotFoundError:
        return None, "Models not found. Please run train_model.py first."
    except Exception as e:
        return None, str(e)


def get_tds_color(tds: float) -> str:
    """Get color based on TDS score."""
    if tds >= 70:
        return "#28a745"  # Green
    elif tds >= 55:
        return "#17a2b8"  # Blue
    elif tds >= 45:
        return "#ffc107"  # Yellow
    elif tds >= 35:
        return "#fd7e14"  # Orange
    else:
        return "#dc3545"  # Red


def main():
    """Main application."""
    # Header
    st.markdown('<p class="main-header">🏀 Touch Dependency Model</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: gray;">Player Evaluation & Scouting Tool</p>',
                unsafe_allow_html=True)

    # Load model
    tdm, error = load_model()

    if error:
        st.error(f"Failed to load model: {error}")
        st.info("Please run `python train_model.py` to train the model first.")
        return

    # Sidebar
    with st.sidebar:
        st.header("Model Information")
        info = tdm.get_model_info()

        st.metric("Status", "✅ Loaded" if info['status'] == 'loaded' else "❌ Not Loaded")

        if info['ensemble_weights']:
            w_linear, w_xgb = info['ensemble_weights']
            st.metric("Linear Weight", f"{w_linear:.2f}")
            st.metric("XGBoost Weight", f"{w_xgb:.2f}")

        if info['archetypes']:
            st.subheader("Archetypes")
            for archetype in info['archetypes']:
                st.write(f"• {archetype}")

        st.markdown("---")
        st.subheader("TDS Scale")
        st.write("""
        - 80-100: Highly Scalable
        - 70-80: Touch Independent
        - 60-70: Slightly Scalable
        - 50-60: Neutral
        - 40-50: Slightly Dependent
        - 30-40: Touch Dependent
        - 0-30: Highly Touch Dependent
        """)

    # Main content - tabs
    tab1, tab2, tab3 = st.tabs(["📝 Single Player", "📊 Batch Upload", "ℹ️ About"])

    # Tab 1: Single Player Evaluation
    with tab1:
        st.header("Evaluate Player")

        with st.form("player_stats", clear_on_submit=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("Shooting Stats")
                fg = st.number_input("FG (Field Goals Made)", min_value=0, value=100)
                fga = st.number_input("FGA (Field Goal Attempts)", min_value=1, value=250)
                ft = st.number_input("FT (Free Throws Made)", min_value=0, value=50)
                fta = st.number_input("FTA (Free Throw Attempts)", min_value=0, value=60)
                pts = st.number_input("PTS (Points)", min_value=0, value=280)

            with col2:
                st.subheader("Three-Point Stats")
                three_p = st.number_input("3P (Three-Pointers Made)", min_value=0, value=30)
                three_pa = st.number_input("3PA (Three-Point Attempts)", min_value=0, value=80)

                st.subheader("Playmaking")
                ast = st.number_input("AST (Assists)", min_value=0, value=50)
                tov = st.number_input("TOV (Turnovers)", min_value=0, value=30)

            with col3:
                st.subheader("Game Info")
                mp = st.number_input("MP (Minutes Played)", min_value=1, value=1000)
                age = st.number_input("Age", min_value=18, max_value=45, value=25)
                pos = st.selectbox("Position", ["G", "F", "C", "G-F", "F-C", "PG", "SG", "SF", "PF"])

                st.subheader("Optional")
                player_name = st.text_input("Player Name", value="Player")
                usg_pct = st.number_input("USG% (if known)", min_value=0.0, max_value=50.0,
                                          value=0.0, help="Leave at 0 to auto-calculate")
                ast_pct = st.number_input("AST% (if known)", min_value=0.0, max_value=60.0,
                                          value=0.0, help="Leave at 0 to auto-calculate")

            submitted = st.form_submit_button("🔍 Evaluate Player", use_container_width=True)

        if submitted:
            # Build stats dict
            stats = {
                'Player': player_name,
                'FG': fg, 'FGA': fga,
                'FT': ft, 'FTA': fta,
                'PTS': pts, 'MP': mp,
                '3P': three_p, '3PA': three_pa,
                'AST': ast, 'TOV': tov,
                'Age': age, 'Pos': pos
            }

            if usg_pct > 0:
                stats['USG%'] = usg_pct
            if ast_pct > 0:
                stats['AST%'] = ast_pct

            try:
                with st.spinner("Analyzing player..."):
                    report = tdm.evaluate_player(stats)

                # Display results
                st.markdown("---")
                st.header("📊 Evaluation Results")

                # Key metrics row
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    tds_color = get_tds_color(report['tds_score'])
                    st.markdown(f"""
                    <div style="background-color: {tds_color}; color: white; padding: 1rem;
                                border-radius: 0.5rem; text-align: center;">
                        <h3 style="margin: 0;">TDS Score</h3>
                        <h1 style="margin: 0; font-size: 3rem;">{report['tds_score']}</h1>
                        <p style="margin: 0;">{report['tds_category']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.metric("Archetype", report['archetype'])
                    st.caption(report['archetype_description'])

                with col3:
                    st.metric("Actual TS%", f"{report['actual_ts']:.1%}")
                    st.metric("Predicted TS%", f"{report['predicted_ts']:.1%}")

                with col4:
                    residual_pct = report['residual'] * 100
                    st.metric("Residual", f"{residual_pct:+.1f}%",
                             delta=f"{'Overperforming' if residual_pct > 0 else 'Underperforming'}")

                # Scouting Summary
                st.markdown("---")
                st.subheader("🔍 Scouting Summary")
                st.markdown(f"""
                <div class="summary-box">
                    {report['scouting_summary']}
                </div>
                """, unsafe_allow_html=True)

                # GM Recommendations
                st.markdown("---")
                st.subheader("💼 GM Recommendations")

                rec_col1, rec_col2 = st.columns(2)

                with rec_col1:
                    st.markdown("**📋 Deployment**")
                    st.write(report['gm_recommendations']['deployment'])

                    st.markdown("**💰 Market Value**")
                    st.write(report['gm_recommendations']['market_value'])

                with rec_col2:
                    st.markdown("**🎯 Acquisition**")
                    st.write(report['gm_recommendations']['acquisition'])

                    st.markdown("**📈 Development**")
                    st.write(report['gm_recommendations']['development'])

                # Feature breakdown
                with st.expander("📊 Feature Breakdown"):
                    feature_df = pd.DataFrame([report['feature_values']])
                    st.dataframe(feature_df.T.rename(columns={0: 'Value'}))

            except Exception as e:
                st.error(f"Error evaluating player: {e}")

    # Tab 2: Batch Upload
    with tab2:
        st.header("Batch Player Evaluation")
        st.write("Upload a CSV file with player statistics to evaluate multiple players at once.")

        # Show expected format
        with st.expander("📋 Expected CSV Format"):
            st.write("Your CSV should have the following columns:")
            st.code("""
Required columns:
- FG: Field goals made
- FGA: Field goal attempts
- FT: Free throws made
- FTA: Free throw attempts
- PTS: Points
- MP: Minutes played

Optional columns:
- Player: Player name
- 3P, 3PA: Three-point makes/attempts
- AST: Assists
- TOV: Turnovers
- Age: Player age
- Pos: Position
            """)

        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.write(f"Loaded {len(df)} players")

                # Preview
                st.subheader("Preview")
                st.dataframe(df.head())

                if st.button("🚀 Evaluate All Players"):
                    progress_bar = st.progress(0)
                    results = []

                    for i, row in df.iterrows():
                        stats = row.to_dict()
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
                        except Exception as e:
                            st.warning(f"Failed to process row {i}: {e}")

                        progress_bar.progress((i + 1) / len(df))

                    if results:
                        results_df = pd.DataFrame(results)

                        st.subheader("Results")
                        st.dataframe(results_df)

                        # Download button
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            "📥 Download Results CSV",
                            csv,
                            "tdm_results.csv",
                            "text/csv"
                        )

                        # Summary stats
                        st.subheader("Summary Statistics")
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Average TDS", f"{results_df['TDS_Score'].mean():.1f}")

                        with col2:
                            st.metric("Highest TDS",
                                     f"{results_df['TDS_Score'].max():.1f}",
                                     delta=results_df.loc[results_df['TDS_Score'].idxmax(), 'Player'])

                        with col3:
                            st.metric("Lowest TDS",
                                     f"{results_df['TDS_Score'].min():.1f}",
                                     delta=results_df.loc[results_df['TDS_Score'].idxmin(), 'Player'])

                        # Archetype distribution
                        st.subheader("Archetype Distribution")
                        arch_counts = results_df['Archetype'].value_counts()
                        st.bar_chart(arch_counts)

            except Exception as e:
                st.error(f"Error reading CSV: {e}")

    # Tab 3: About
    with tab3:
        st.header("About the Touch Dependency Model")

        st.markdown("""
        ### What is Touch Dependency?

        Touch Dependency measures how much a player's offensive efficiency depends on
        having consistent offensive involvement (touches). A player with **high touch dependency**
        needs regular shots and ball handling to be effective, while a **low touch dependency**
        (high scalability) player can maintain efficiency in varied roles.

        ### How TDS Works

        The Touch Dependency Score (TDS) is calculated by:

        1. **Feature Engineering**: Computing usage rate, assist rate, shot diet, and other metrics
        2. **Efficiency Prediction**: Using an ensemble model (Linear + XGBoost) to predict expected TS%
        3. **Residual Analysis**: Comparing actual vs predicted efficiency
        4. **Percentile Scoring**: Converting residuals to 0-100 scale based on historical distribution

        ### Interpreting TDS

        | Score Range | Category | Meaning |
        |-------------|----------|---------|
        | 80-100 | Highly Scalable | Can thrive in any role |
        | 70-80 | Touch Independent | Efficient regardless of role |
        | 60-70 | Slightly Scalable | Adapts well to varied roles |
        | 50-60 | Neutral | Stable but may need consistency |
        | 40-50 | Slightly Dependent | Minor efficiency drops in reduced roles |
        | 30-40 | Touch Dependent | Performs best with consistent role |
        | 0-30 | Highly Touch Dependent | Needs specific role to be effective |

        ### The 12 Archetypes

        1. **Star Playmaker** - Creates for self and others at high volume
        2. **Volume Scorer** - High usage scorer who carries offensive load
        3. **Floor General** - Pass-first point guard who orchestrates
        4. **Sharpshooter** - Elite catch-and-shoot specialist
        5. **Reliable Starter** - Solid two-way contributor
        6. **Energy Scorer** - Instant offense and energy
        7. **Rim Runner** - Finishes at the basket off cuts/rolls
        8. **Stretch Big** - Floor-spacing big man
        9. **Role Player** - Versatile complementary player
        10. **Defensive Specialist** - Defense-first player
        11. **Developing Player** - Young prospect still growing
        12. **Bench Scorer** - Second-unit scoring punch

        ### Model Details

        - **Training Data**: Historical NBA player seasons
        - **Target Variable**: True Shooting Percentage (TS%)
        - **Model Type**: Ensemble (Ridge Regression + XGBoost)
        - **Clustering**: K-Means with 12 clusters

        ---
        *Built with ❤️ for basketball analytics*
        """)


if __name__ == "__main__":
    main()
