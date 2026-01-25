"""
Player archetype clustering for Touch Dependency Model.
"""

import numpy as np
from typing import Optional, Dict, List, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
import joblib


class ArchetypeClusterer:
    """
    Clusters players into offensive archetypes based on their profiles.

    Uses K-Means or Gaussian Mixture Models to identify player types
    based on usage, playmaking, efficiency, and shot selection patterns.

    12 Archetypes (simplified naming):
    1. Star Playmaker - High usage + high assists + efficient
    2. Volume Scorer - High usage + scores a lot + okay efficiency
    3. Floor General - Primary ball handler + pass-first
    4. Sharpshooter - Catch-and-shoot three specialist
    5. Reliable Starter - Solid all-around contributor
    6. Energy Scorer - Gets buckets in limited minutes
    7. Rim Runner - Finishes at rim + limited shot creation
    8. Stretch Big - Spacing center/forward
    9. Role Player - Does a bit of everything
    10. Defensive Specialist - Offense not primary value
    11. Developing Player - Young/raw with potential
    12. Bench Scorer - Instant offense off bench
    """

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

    ARCHETYPE_DESCRIPTIONS = {
        "Star Playmaker": "Creates offense for self and others at high volume with strong efficiency",
        "Volume Scorer": "Takes lots of shots and carries scoring load",
        "Floor General": "Primary ball handler who makes teammates better",
        "Sharpshooter": "Elite three-point shooter who spaces the floor",
        "Reliable Starter": "Dependable two-way player with no major weaknesses",
        "Energy Scorer": "Brings instant offense and energy",
        "Rim Runner": "Scores at the basket off cuts and rolls",
        "Stretch Big": "Big man who can shoot from outside",
        "Role Player": "Does multiple things well without starring",
        "Defensive Specialist": "Primary value is on defense",
        "Developing Player": "Still growing into their role",
        "Bench Scorer": "Provides scoring punch off the bench"
    }

    CLUSTERING_FEATURES = ['USG%', 'AST%', 'TS%', 'TDS', '3PA_rate', 'FTA_rate']

    def __init__(self, n_clusters: int = 12, method: str = 'kmeans'):
        """
        Initialize ArchetypeClusterer.

        Args:
            n_clusters: Number of archetypes (default 12)
            method: Clustering method ('kmeans' or 'gmm')
        """
        self.n_clusters = n_clusters
        self.method = method

        if method == 'kmeans':
            self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        else:
            self.model = GaussianMixture(n_components=n_clusters, random_state=42)

        self.scaler = StandardScaler()
        self.cluster_centers_: Optional[np.ndarray] = None
        self.cluster_labels_: Optional[Dict[int, str]] = None
        self._is_fitted = False

    def fit(self, features: np.ndarray,
            feature_names: Optional[List[str]] = None) -> 'ArchetypeClusterer':
        """
        Fit the clustering model.

        Args:
            features: Feature matrix for clustering
            feature_names: Names of features used

        Returns:
            self
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(features)

        # Fit clustering model
        self.model.fit(X_scaled)

        # Store cluster centers (unscaled for interpretability)
        if self.method == 'kmeans':
            self.cluster_centers_ = self.scaler.inverse_transform(
                self.model.cluster_centers_
            )
        else:
            self.cluster_centers_ = self.scaler.inverse_transform(
                self.model.means_
            )

        # Auto-label clusters based on profiles
        self.cluster_labels_ = self._auto_label_clusters(
            self.cluster_centers_, feature_names
        )

        self._is_fitted = True
        return self

    def _auto_label_clusters(self, centers: np.ndarray,
                             feature_names: Optional[List[str]] = None) -> Dict[int, str]:
        """
        Automatically assign archetype labels based on cluster profiles.

        Uses rule-based logic to match cluster characteristics to archetypes.
        """
        if feature_names is None:
            feature_names = self.CLUSTERING_FEATURES

        # Create feature index lookup
        feat_idx = {name: i for i, name in enumerate(feature_names)}

        labels = {}
        used_archetypes = set()

        # Sort clusters by usage to assign in order of prominence
        usg_idx = feat_idx.get('USG%', 0)
        cluster_order = np.argsort(centers[:, usg_idx])[::-1]

        for cluster_id in cluster_order:
            center = centers[cluster_id]

            # Extract feature values with safe defaults
            usg = center[feat_idx.get('USG%', 0)] if 'USG%' in feat_idx else 20
            ast = center[feat_idx.get('AST%', 0)] if 'AST%' in feat_idx else 15
            ts = center[feat_idx.get('TS%', 0)] if 'TS%' in feat_idx else 0.54
            tds = center[feat_idx.get('TDS', 0)] if 'TDS' in feat_idx else 50
            three_rate = center[feat_idx.get('3PA_rate', 0)] if '3PA_rate' in feat_idx else 0.3
            fta_rate = center[feat_idx.get('FTA_rate', 0)] if 'FTA_rate' in feat_idx else 0.25

            archetype = self._classify_profile(
                usg, ast, ts, tds, three_rate, fta_rate, used_archetypes
            )
            labels[cluster_id] = archetype
            used_archetypes.add(archetype)

        return labels

    def _classify_profile(self, usg: float, ast: float, ts: float,
                          tds: float, three_rate: float, fta_rate: float,
                          used: set) -> str:
        """Classify a profile into an archetype based on features."""

        # Star Playmaker: high usage, high assists, efficient
        if "Star Playmaker" not in used and usg > 25 and ast > 20 and ts > 0.55:
            return "Star Playmaker"

        # Floor General: pass-first, high assists
        if "Floor General" not in used and ast > 25 and usg < 22:
            return "Floor General"

        # Volume Scorer: high usage, lower assists
        if "Volume Scorer" not in used and usg > 26 and ast < 18:
            return "Volume Scorer"

        # Sharpshooter: high three rate, efficient, low usage
        if "Sharpshooter" not in used and three_rate > 0.45 and usg < 20 and ts > 0.54:
            return "Sharpshooter"

        # Stretch Big: moderate three rate, lower usage (typically big)
        if "Stretch Big" not in used and three_rate > 0.30 and usg < 18 and fta_rate > 0.30:
            return "Stretch Big"

        # Rim Runner: low three rate, high FTA rate, low assists
        if "Rim Runner" not in used and three_rate < 0.15 and fta_rate > 0.35 and ast < 12:
            return "Rim Runner"

        # Energy Scorer: moderate usage, efficient, high TDS
        if "Energy Scorer" not in used and tds > 60 and usg > 18 and usg < 25:
            return "Energy Scorer"

        # Reliable Starter: balanced profile, good efficiency
        if "Reliable Starter" not in used and ts > 0.53 and 18 < usg < 24:
            return "Reliable Starter"

        # Bench Scorer: moderate usage, variable efficiency
        if "Bench Scorer" not in used and 16 < usg < 22:
            return "Bench Scorer"

        # Defensive Specialist: low usage, low scoring impact
        if "Defensive Specialist" not in used and usg < 16 and ts < 0.54:
            return "Defensive Specialist"

        # Developing Player: low TDS, variable profile
        if "Developing Player" not in used and tds < 45:
            return "Developing Player"

        # Role Player: catch-all for balanced low-usage players
        if "Role Player" not in used:
            return "Role Player"

        # Fallback - find first unused archetype
        for archetype in self.ARCHETYPE_NAMES.values():
            if archetype not in used:
                return archetype

        return "Role Player"

    def predict_archetype(self, features: np.ndarray) -> Tuple[str, int]:
        """
        Predict archetype for a player.

        Args:
            features: Player feature vector

        Returns:
            Tuple of (archetype_name, cluster_id)
        """
        if not self._is_fitted:
            raise ValueError("Clusterer not fitted. Call fit() first.")

        X = features.reshape(1, -1) if features.ndim == 1 else features
        X_scaled = self.scaler.transform(X)

        cluster_id = self.model.predict(X_scaled)[0]
        archetype = self.cluster_labels_.get(cluster_id, "Unknown")

        return archetype, cluster_id

    def predict_archetype_proba(self, features: np.ndarray) -> Dict[str, float]:
        """
        Get probability distribution over archetypes (GMM only).

        Args:
            features: Player feature vector

        Returns:
            Dictionary mapping archetype names to probabilities
        """
        if self.method != 'gmm':
            raise ValueError("Probability prediction only available for GMM")

        X = features.reshape(1, -1) if features.ndim == 1 else features
        X_scaled = self.scaler.transform(X)

        probas = self.model.predict_proba(X_scaled)[0]

        return {
            self.cluster_labels_[i]: float(p)
            for i, p in enumerate(probas)
        }

    def get_archetype_profiles(self) -> Dict[str, Dict[str, float]]:
        """
        Get the average profile for each archetype.

        Returns:
            Dictionary mapping archetype names to feature profiles
        """
        if not self._is_fitted:
            raise ValueError("Clusterer not fitted.")

        profiles = {}
        for cluster_id, archetype in self.cluster_labels_.items():
            center = self.cluster_centers_[cluster_id]
            profiles[archetype] = {
                feat: float(center[i])
                for i, feat in enumerate(self.CLUSTERING_FEATURES)
                if i < len(center)
            }

        return profiles

    def get_archetype_description(self, archetype: str) -> str:
        """Get description for an archetype."""
        return self.ARCHETYPE_DESCRIPTIONS.get(archetype, "Unknown archetype")

    def get_similar_archetypes(self, features: np.ndarray, top_n: int = 3) -> List[Tuple[str, float]]:
        """
        Get most similar archetypes to a player profile.

        Args:
            features: Player feature vector
            top_n: Number of similar archetypes to return

        Returns:
            List of (archetype_name, similarity_score) tuples
        """
        if not self._is_fitted:
            raise ValueError("Clusterer not fitted.")

        X = features.reshape(1, -1) if features.ndim == 1 else features
        X_scaled = self.scaler.transform(X)

        # Calculate distances to all cluster centers
        centers_scaled = self.scaler.transform(self.cluster_centers_)
        distances = np.linalg.norm(centers_scaled - X_scaled, axis=1)

        # Convert to similarity (inverse distance)
        similarities = 1 / (1 + distances)

        # Sort by similarity
        sorted_idx = np.argsort(similarities)[::-1][:top_n]

        return [
            (self.cluster_labels_[idx], float(similarities[idx]))
            for idx in sorted_idx
        ]

    def save(self, filepath: str) -> None:
        """Save clusterer state."""
        state = {
            'model': self.model,
            'scaler': self.scaler,
            'n_clusters': self.n_clusters,
            'method': self.method,
            'cluster_centers': self.cluster_centers_,
            'cluster_labels': self.cluster_labels_,
            'is_fitted': self._is_fitted
        }
        joblib.dump(state, filepath)

    def load(self, filepath: str) -> None:
        """Load clusterer state."""
        state = joblib.load(filepath)
        self.model = state['model']
        self.scaler = state['scaler']
        self.n_clusters = state['n_clusters']
        self.method = state['method']
        self.cluster_centers_ = state['cluster_centers']
        self.cluster_labels_ = state['cluster_labels']
        self._is_fitted = state['is_fitted']

    @property
    def is_fitted(self) -> bool:
        """Check if clusterer is fitted."""
        return self._is_fitted
