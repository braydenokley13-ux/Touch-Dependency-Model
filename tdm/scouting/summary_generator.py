"""
Scouting summary generator for Touch Dependency Model.
"""

from typing import Dict, Optional


class ScoutingSummaryGenerator:
    """
    Generates natural language scouting summaries from player profiles.

    Creates 3-6 sentence assessments covering:
    1. Touch load profile (usage, playmaking)
    2. Efficiency context (TS%, performance)
    3. Scalability assessment (TDS interpretation)
    4. Archetype and role fit
    5. Risk factors and limitations
    """

    def __init__(self):
        """Initialize ScoutingSummaryGenerator."""
        pass

    def generate_summary(self, profile: Dict) -> str:
        """
        Generate a scouting summary from a player profile.

        Args:
            profile: Dictionary containing:
                - player_name (optional)
                - usg_pct: Usage percentage
                - ast_pct: Assist percentage
                - ts_pct: True shooting percentage
                - predicted_ts: Model predicted TS%
                - tds_score: Touch Dependency Score
                - archetype: Player archetype
                - three_pa_rate: Three-point attempt rate
                - fta_rate: Free throw attempt rate
                - age (optional)

        Returns:
            Multi-sentence scouting summary
        """
        sentences = []

        # 1. Touch load profile
        sentences.append(self._describe_touch_load(profile))

        # 2. Efficiency context
        sentences.append(self._describe_efficiency(profile))

        # 3. Scalability assessment
        sentences.append(self._describe_scalability(profile))

        # 4. Archetype and role fit
        sentences.append(self._describe_archetype_fit(profile))

        # 5. Risk factors (if applicable)
        risk = self._describe_risks(profile)
        if risk:
            sentences.append(risk)

        return " ".join(sentences)

    def _describe_touch_load(self, profile: Dict) -> str:
        """Describe the player's touch load and playmaking role."""
        usg = profile.get('usg_pct', 20)
        ast = profile.get('ast_pct', 15)

        # Usage description
        if usg >= 30:
            usg_desc = "very high"
            usg_context = "as a primary offensive option"
        elif usg >= 25:
            usg_desc = "high"
            usg_context = "as a go-to scorer"
        elif usg >= 20:
            usg_desc = "moderate"
            usg_context = "in a secondary role"
        elif usg >= 15:
            usg_desc = "low"
            usg_context = "as a complementary piece"
        else:
            usg_desc = "very low"
            usg_context = "in a limited offensive role"

        # Assist description
        if ast >= 30:
            ast_desc = "elite playmaking duties"
        elif ast >= 22:
            ast_desc = "significant playmaking responsibility"
        elif ast >= 15:
            ast_desc = "moderate ball-handling duties"
        elif ast >= 10:
            ast_desc = "occasional playmaking"
        else:
            ast_desc = "minimal creation responsibility"

        return f"Player operates at {usg_desc} usage ({usg:.1f}%) {usg_context}, with {ast_desc} ({ast:.1f}% AST)."

    def _describe_efficiency(self, profile: Dict) -> str:
        """Describe the player's efficiency relative to expectations."""
        ts = profile.get('ts_pct', 0.54)
        predicted = profile.get('predicted_ts', 0.54)
        usg = profile.get('usg_pct', 20)

        # Actual TS% interpretation
        if ts >= 0.60:
            ts_desc = "elite"
        elif ts >= 0.57:
            ts_desc = "excellent"
        elif ts >= 0.54:
            ts_desc = "solid"
        elif ts >= 0.50:
            ts_desc = "below average"
        else:
            ts_desc = "poor"

        # Comparison to prediction
        diff = ts - predicted
        if diff >= 0.03:
            comparison = "significantly exceeding model expectations"
        elif diff >= 0.015:
            comparison = "outperforming expected efficiency"
        elif diff >= -0.015:
            comparison = "performing near expected levels"
        elif diff >= -0.03:
            comparison = "slightly underperforming expectations"
        else:
            comparison = "well below expected efficiency"

        # Context based on usage
        if usg >= 25:
            context = "despite heavy offensive load"
        elif usg >= 20:
            context = "at moderate volume"
        else:
            context = "in limited opportunities"

        return f"Maintains {ts_desc} efficiency ({ts:.1%} TS), {comparison} {context}."

    def _describe_scalability(self, profile: Dict) -> str:
        """Describe the player's scalability based on TDS."""
        tds = profile.get('tds_score', 50)

        if tds >= 75:
            return f"TDS of {tds:.0f} indicates exceptional scalability - this player can thrive in any role from featured scorer to complementary piece without efficiency loss."
        elif tds >= 65:
            return f"TDS of {tds:.0f} suggests strong role flexibility - efficiency should hold or improve in varied offensive systems."
        elif tds >= 55:
            return f"TDS of {tds:.0f} indicates positive scalability potential - can adapt to different roles without major efficiency drops."
        elif tds >= 45:
            return f"TDS of {tds:.0f} represents neutral scalability - performance relatively stable but may require consistent role."
        elif tds >= 35:
            return f"TDS of {tds:.0f} suggests some touch dependency - player may need consistent offensive involvement to maintain efficiency."
        else:
            return f"TDS of {tds:.0f} indicates significant touch dependency - efficiency could drop meaningfully in reduced roles or different systems."

    def _describe_archetype_fit(self, profile: Dict) -> str:
        """Describe the player's archetype and ecosystem fit."""
        archetype = profile.get('archetype', 'Role Player')
        tds = profile.get('tds_score', 50)
        three_rate = profile.get('three_pa_rate', 0.30)
        usg = profile.get('usg_pct', 20)

        # Base archetype description
        archetype_fits = {
            "Star Playmaker": "primary creator who elevates teammates while maintaining personal efficiency",
            "Volume Scorer": "high-volume scorer who requires significant shot attempts to be effective",
            "Floor General": "pass-first point guard who orchestrates offense and creates for others",
            "Sharpshooter": "catch-and-shoot specialist who provides spacing and gravity",
            "Reliable Starter": "two-way contributor who can fill multiple roles effectively",
            "Energy Scorer": "instant offense option who provides scoring punch",
            "Rim Runner": "roll man and cutter who finishes at the rim",
            "Stretch Big": "floor-spacing big who opens driving lanes for teammates",
            "Role Player": "versatile complementary player who fits multiple systems",
            "Defensive Specialist": "defense-first player whose offensive value is secondary",
            "Developing Player": "prospect with room to grow into expanded role",
            "Bench Scorer": "second-unit scorer who provides instant offense"
        }

        fit_desc = archetype_fits.get(archetype, "versatile contributor")

        # Add ecosystem context
        if tds >= 60 and three_rate >= 0.35:
            ecosystem = "Projects as ideal fit alongside ball-dominant stars needing floor spacing."
        elif tds >= 60 and usg < 20:
            ecosystem = "High-value addition to championship-caliber rosters as plug-and-play piece."
        elif tds < 40 and usg >= 25:
            ecosystem = "May require specific system with consistent offensive touches to maximize value."
        elif archetype == "Floor General":
            ecosystem = "Best paired with off-ball scorers and shooters who can capitalize on creation."
        else:
            ecosystem = "Fits as complementary piece in balanced offensive systems."

        return f"Profiles as {archetype} - a {fit_desc}. {ecosystem}"

    def _describe_risks(self, profile: Dict) -> Optional[str]:
        """Identify and describe risk factors."""
        risks = []

        tds = profile.get('tds_score', 50)
        ts = profile.get('ts_pct', 0.54)
        usg = profile.get('usg_pct', 20)
        age = profile.get('age')
        three_rate = profile.get('three_pa_rate', 0.30)

        # Low TDS with high usage = risky
        if tds < 40 and usg >= 25:
            risks.append("role reduction risk")

        # Poor efficiency
        if ts < 0.50:
            risks.append("efficiency concerns")

        # Low three-point rate in modern era
        if three_rate < 0.15:
            risks.append("spacing limitations")

        # Age concerns
        if age and age >= 32:
            risks.append("age-related decline potential")
        elif age and age <= 22:
            risks.append("developmental variance")

        # High usage + low assists + mediocre efficiency
        if usg >= 25 and profile.get('ast_pct', 15) < 12 and ts < 0.55:
            risks.append("ball-stopping tendencies")

        if not risks:
            return None

        risk_str = ", ".join(risks)
        return f"Key considerations: {risk_str}."

    def generate_short_summary(self, profile: Dict) -> str:
        """Generate a 1-2 sentence summary."""
        archetype = profile.get('archetype', 'Role Player')
        tds = profile.get('tds_score', 50)
        ts = profile.get('ts_pct', 0.54)

        if tds >= 65:
            scalability = "highly scalable"
        elif tds >= 50:
            scalability = "solid role flexibility"
        else:
            scalability = "role-dependent"

        if ts >= 0.57:
            eff = "elite efficiency"
        elif ts >= 0.54:
            eff = "solid efficiency"
        else:
            eff = "efficiency work needed"

        return f"{archetype} with {scalability} (TDS: {tds:.0f}) and {eff} ({ts:.1%} TS)."
