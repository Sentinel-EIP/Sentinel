// Formes des reponses de l'API (backend/app/api/routes).

export interface SymbolInfo {
  symbol: string;
  timeframe: string;
  first: string;
  last: string;
  count: number;
}

export interface Candle {
  ts: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export type AlertLevel = "warning" | "critical" | "stale";

export interface Alert {
  symbol: string;
  level: AlertLevel;
  code: string;
  message: string;
  value: number;
  threshold: number;
}

export interface RiskSummary {
  symbol: string;
  timeframe: string;
  as_of: string;
  last_price: number;
  volatility: number | null;
  max_drawdown: number;
  current_drawdown: number;
  sample_size: number;
  alerts: Alert[];
}

// Resultat IA generique : confiance, fiabilite mesuree et explication, sans
// direction de prix (docs/ECARTS.md, E10).
export interface AiResult {
  id: number;
  kind: string;
  symbol: string;
  model_version: string;
  confidence: number;
  reliability: number | null;
  explanation: string;
  value: {
    reference_price: number;
    lower: number;
    upper: number;
    horizon_hours: number;
    backtest_size: number;
    note: string;
  };
  created_at: string;
}
