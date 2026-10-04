import { create } from "zustand";

import { ApiError, apiFetch } from "../api/client";
import type { AiResult, Alert, Candle, RiskSummary, SymbolInfo } from "../api/types";
import { useAuth } from "./useAuth";

const TIMEFRAME = "1h";

interface DashboardState {
  symbols: SymbolInfo[];
  symbol: string | null;
  candles: Candle[];
  risk: RiskSummary | null;
  alerts: Alert[];
  cone: AiResult | null;
  loading: boolean;
  analysing: boolean;
  error: string | null;
  load: () => Promise<void>;
  select: (symbol: string) => Promise<void>;
  runCone: (horizonHours: number) => Promise<void>;
}

// Appel authentifie ; un 401 (jeton expire) ramene a l'ecran de connexion.
async function call<T>(path: string, body?: unknown): Promise<T> {
  try {
    return await apiFetch<T>(path, {
      method: body === undefined ? "GET" : "POST",
      body,
      token: useAuth.getState().token,
    });
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) useAuth.getState().logout();
    throw err;
  }
}

function message(err: unknown): string {
  return err instanceof ApiError ? err.message : "Erreur inattendue";
}

export const useDashboard = create<DashboardState>((set, get) => ({
  symbols: [],
  symbol: null,
  candles: [],
  risk: null,
  alerts: [],
  cone: null,
  loading: false,
  analysing: false,
  error: null,

  load: async () => {
    set({ loading: true, error: null });
    try {
      const [symbols, alerts] = await Promise.all([
        call<SymbolInfo[]>("/market/symbols"),
        call<Alert[]>(`/alerts?timeframe=${TIMEFRAME}`),
      ]);
      const available = symbols.filter((s) => s.timeframe === TIMEFRAME);
      set({ symbols: available, alerts });
      const current = get().symbol;
      const next = available.some((s) => s.symbol === current) ? current : available[0]?.symbol;
      if (next) await get().select(next);
    } catch (err) {
      set({ error: message(err) });
    } finally {
      set({ loading: false });
    }
  },

  select: async (symbol) => {
    const changed = symbol !== get().symbol;
    set({ symbol, error: null, ...(changed ? { cone: null } : {}) });
    try {
      const q = `symbol=${encodeURIComponent(symbol)}&timeframe=${TIMEFRAME}`;
      const [candles, risk, results] = await Promise.all([
        call<Candle[]>(`/market/candles?${q}&limit=500`),
        call<RiskSummary>(`/risk/summary?${q}`),
        call<AiResult[]>(`/analysis/results?symbol=${encodeURIComponent(symbol)}&kind=volatility_cone&limit=1`),
      ]);
      // Une reponse arrivee apres un changement de symbole est ignoree.
      if (get().symbol !== symbol) return;
      set({ candles, risk, cone: results[0] ?? null });
    } catch (err) {
      set({ error: message(err) });
    }
  },

  runCone: async (horizonHours) => {
    const symbol = get().symbol;
    if (!symbol) return;
    set({ analysing: true, error: null });
    try {
      const cone = await call<AiResult>("/analysis/volatility", {
        symbol,
        timeframe: TIMEFRAME,
        horizon_hours: horizonHours,
        confidence: 0.8,
      });
      if (get().symbol === symbol) set({ cone });
    } catch (err) {
      set({ error: message(err) });
    } finally {
      set({ analysing: false });
    }
  },
}));
