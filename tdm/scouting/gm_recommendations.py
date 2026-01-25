"""
GM recommendation engine for Touch Dependency Model.
"""

from typing import Dict, List, Optional


class GMRecommendationEngine:
    """
    Generates actionable GM recommendations from player profiles.

    Provides guidance on:
    - Deployment: How to use the player
    - Acquisition: Trade/FA implications
    - Market Value: Over/undervalued assessment
    - Development: Growth opportunities
    """

    def __init__(self):
        """Initialize GMRecommendationEngine."""
        pass

    def generate_recommendations(self, profile: Dict) -> Dict[str, str]:
        """
        Generate comprehensive GM recommendations.

        Args:
            profile: Dictionary containing player metrics and archetype

        Returns:
            Dictionary with deployment, acquisition, market_value, development keys
        """
        return {
            'deployment': self._generate_deployment(profile),
            'acquisition': self._generate_acquisition(profile),
            'market_value': self._generate_market_value(profile),
            'development': self._generate_development(profile)
        }

    def _generate_deployment(self, profile: Dict) -> str:
        """Generate deployment recommendations."""
        archetype = profile.get('archetype', 'Role Player')
        tds = profile.get('tds_score', 50)
        usg = profile.get('usg_pct', 20)
        ast = profile.get('ast_pct', 15)
        three_rate = profile.get('three_pa_rate', 0.30)
        ts = profile.get('ts_pct', 0.54)

        recommendations = []

        # Lineup pairing recommendations
        if archetype == "Star Playmaker":
            recommendations.append("Feature as primary ball handler in crunch time")
            recommendations.append("Pair with shooters to maximize drive-and-kick opportunities")
        elif archetype == "Volume Scorer":
            recommendations.append("Use as primary scoring option when playmakers rest")
            recommendations.append("Stagger minutes with other high-usage players")
        elif archetype == "Floor General":
            recommendations.append("Run offense through in half-court sets")
            recommendations.append("Pair with off-ball scorers who can finish")
        elif archetype == "Sharpshooter":
            recommendations.append("Position in corners and wings for catch-and-shoot looks")
            recommendations.append("Use as decoy to create space for drivers")
        elif archetype == "Rim Runner":
            recommendations.append("Feature in pick-and-roll as roller to basket")
            recommendations.append("Pair with skilled passers who can find lobs")
        elif archetype == "Stretch Big":
            recommendations.append("Use as pick-and-pop option to open driving lanes")
            recommendations.append("Deploy in closing lineups for spacing")
        elif archetype == "Energy Scorer":
            recommendations.append("Insert for scoring bursts when offense stalls")
            recommendations.append("Effective in fast-break opportunities")
        elif archetype == "Bench Scorer":
            recommendations.append("Lead second unit offense")
            recommendations.append("Stagger with starters for consistent scoring presence")

        # TDS-based recommendations
        if tds >= 65:
            recommendations.append("Flexible deployment - can play with any lineup configuration")
        elif tds < 40:
            recommendations.append("Ensure consistent role and touches to maintain efficiency")

        # Three-point recommendations
        if three_rate >= 0.40:
            recommendations.append("Maximize three-point attempts; hunt open looks")
        elif three_rate < 0.15 and archetype not in ["Rim Runner", "Floor General"]:
            recommendations.append("Develop or avoid situations requiring perimeter shooting")

        return "; ".join(recommendations[:3])

    def _generate_acquisition(self, profile: Dict) -> str:
        """Generate acquisition recommendations."""
        tds = profile.get('tds_score', 50)
        ts = profile.get('ts_pct', 0.54)
        archetype = profile.get('archetype', 'Role Player')
        age = profile.get('age', 27)

        recommendations = []

        # TDS-based value
        if tds >= 70:
            recommendations.append("High-priority target for contenders needing plug-and-play pieces")
        elif tds >= 55:
            recommendations.append("Solid addition for teams with established systems")
        elif tds < 40:
            recommendations.append("Requires specific fit - not a universal upgrade")

        # Archetype-specific recommendations
        if archetype == "Sharpshooter" and ts >= 0.58:
            recommendations.append("Premium value in playoff settings where spacing is critical")
        elif archetype == "Star Playmaker":
            recommendations.append("Centerpiece acquisition - build around this player")
        elif archetype == "Developing Player":
            recommendations.append("Buy low if organization has development resources")

        # Age considerations
        if age and age <= 25:
            recommendations.append("Long-term asset with upside")
        elif age and age >= 30:
            recommendations.append("Win-now acquisition; limited long-term value")

        # Efficiency-based
        if ts >= 0.60:
            recommendations.append("Elite efficiency makes overpaying less risky")
        elif ts < 0.50:
            recommendations.append("Efficiency concerns suggest caution on cost")

        return "; ".join(recommendations[:3])

    def _generate_market_value(self, profile: Dict) -> str:
        """Generate market value assessment."""
        tds = profile.get('tds_score', 50)
        ts = profile.get('ts_pct', 0.54)
        usg = profile.get('usg_pct', 20)
        archetype = profile.get('archetype', 'Role Player')

        # Determine value direction
        undervalued_signals = 0
        overvalued_signals = 0

        # High TDS with low usage = often undervalued
        if tds >= 60 and usg < 22:
            undervalued_signals += 1

        # Scalable shooters undervalued
        if archetype in ["Sharpshooter", "Stretch Big"] and tds >= 55:
            undervalued_signals += 1

        # High efficiency in limited role
        if ts >= 0.58 and usg < 20:
            undervalued_signals += 1

        # Volume scorers with poor TDS often overvalued
        if archetype == "Volume Scorer" and tds < 45:
            overvalued_signals += 1

        # High usage with mediocre efficiency
        if usg >= 25 and ts < 0.53:
            overvalued_signals += 1

        # Low TDS stars
        if usg >= 28 and tds < 40:
            overvalued_signals += 1

        # Generate assessment
        if undervalued_signals >= 2:
            value_assessment = "Likely undervalued in current market"
            reasoning = "TDS suggests efficiency will hold or improve in varied roles"
        elif overvalued_signals >= 2:
            value_assessment = "Potentially overvalued based on counting stats"
            reasoning = "Touch dependency suggests efficiency may decline in different context"
        else:
            value_assessment = "Fair market value"
            reasoning = "Profile matches expected production at current cost"

        # Add comparable context
        if archetype == "Sharpshooter" and tds >= 60:
            comp = "Comps: Joe Harris, Luke Kennard tier"
        elif archetype == "Star Playmaker":
            comp = "Comps: Elite playmaker tier"
        elif archetype == "Rim Runner" and ts >= 0.60:
            comp = "Comps: Efficient vertical spacer tier"
        else:
            comp = ""

        result = f"{value_assessment}. {reasoning}."
        if comp:
            result += f" {comp}."

        return result

    def _generate_development(self, profile: Dict) -> str:
        """Generate development recommendations."""
        three_rate = profile.get('three_pa_rate', 0.30)
        tds = profile.get('tds_score', 50)
        ast = profile.get('ast_pct', 15)
        fta_rate = profile.get('fta_rate', 0.25)
        age = profile.get('age', 27)
        archetype = profile.get('archetype', 'Role Player')

        recommendations = []

        # Three-point development
        if three_rate < 0.25:
            recommendations.append(f"Increase 3PA rate from {three_rate:.0%} to 35%+ to unlock spacing value")
        elif three_rate < 0.35 and archetype in ["Sharpshooter", "Stretch Big"]:
            recommendations.append("Push three-point volume to maximize archetype value")

        # Playmaking development
        if ast < 12 and profile.get('usg_pct', 20) >= 22:
            recommendations.append("Develop passing out of double teams to counter defensive attention")

        # Free throw improvement for paint players
        if fta_rate > 0.35 and profile.get('ft_pct', 0.75) and profile.get('ft_pct', 0.75) < 0.70:
            recommendations.append("Free throw improvement critical for closing lineup viability")

        # TDS improvement paths
        if tds < 45:
            recommendations.append("Work on catch-and-shoot scenarios to improve off-ball value")
            recommendations.append("Reduce reliance on iso/creation touches")

        # Age-specific recommendations
        if age and age <= 23:
            recommendations.append("Focus on skill development - physical tools still developing")
        elif age and age >= 30:
            recommendations.append("Optimize current skillset rather than adding new dimensions")

        # Role-specific
        if archetype == "Developing Player":
            recommendations.append("Needs consistent playing time to translate practice to games")
        elif archetype == "Defensive Specialist":
            recommendations.append("Add one offensive skill (corner 3, cutting) to increase value")

        if not recommendations:
            recommendations.append("Maintain current approach - no major development needs identified")

        return "; ".join(recommendations[:3])

    def generate_one_liner(self, profile: Dict) -> str:
        """Generate a quick one-line recommendation."""
        tds = profile.get('tds_score', 50)
        archetype = profile.get('archetype', 'Role Player')
        ts = profile.get('ts_pct', 0.54)

        if tds >= 70 and ts >= 0.57:
            return "High-priority acquisition: Elite efficiency with proven scalability."
        elif tds >= 60:
            return f"Quality {archetype}: Good fit for contenders needing role flexibility."
        elif tds >= 45:
            return f"Neutral {archetype}: Serviceable in right system."
        else:
            return f"Caution on {archetype}: May require specific role to maintain value."

    def generate_trade_value(self, profile: Dict) -> Dict[str, str]:
        """Generate trade value assessment."""
        tds = profile.get('tds_score', 50)
        ts = profile.get('ts_pct', 0.54)
        age = profile.get('age', 27)
        archetype = profile.get('archetype', 'Role Player')

        # Determine draft pick equivalent
        if tds >= 70 and ts >= 0.58:
            if archetype == "Star Playmaker":
                pick_value = "Multiple first-round picks"
            else:
                pick_value = "Late first-round pick"
        elif tds >= 55 and ts >= 0.55:
            pick_value = "Early second-round pick"
        elif tds >= 45:
            pick_value = "Second-round pick"
        else:
            pick_value = "Cash considerations / minimum trade value"

        # Contract considerations
        if age and age <= 25:
            contract = "Worth paying for long-term value"
        elif age and age >= 32:
            contract = "Short-term deal preferred"
        else:
            contract = "Standard market rate appropriate"

        return {
            'pick_equivalent': pick_value,
            'contract_guidance': contract,
            'trade_direction': 'buy' if tds >= 55 else 'hold/sell'
        }
