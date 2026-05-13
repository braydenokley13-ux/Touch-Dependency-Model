export interface PlayerStats {
  Player?: string;
  FG: number;
  FGA: number;
  FT: number;
  FTA: number;
  PTS: number;
  MP: number;
  "3P"?: number;
  "3PA"?: number;
  AST?: number;
  TOV?: number;
  Age?: number;
  Pos?: string;
  "USG%"?: number;
  "AST%"?: number;
}

export interface GMRecommendations {
  deployment: string;
  acquisition: string;
  market_value: string;
  development: string;
}

export interface EvaluationReport {
  tds_score: number;
  tds_category: string;
  tds_description: string;
  archetype: string;
  archetype_description: string;
  predicted_ts: number;
  actual_ts: number;
  residual: number;
  scouting_summary: string;
  short_summary: string;
  gm_recommendations: GMRecommendations;
  feature_values: Record<string, number | string>;
}
