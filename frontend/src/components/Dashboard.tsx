import "../styles/dashboard.css";

import { useEffect } from "react";

import { useDashboard } from "../store/useDashboard";
import AlertsPanel from "./AlertsPanel";
import AnalysisPanel from "./AnalysisPanel";
import CandleChart from "./CandleChart";
import RiskPanel from "./RiskPanel";

const REFRESH_MS = 60_000; // bougies 1h collectees tous les quarts d'heure

export default function Dashboard() {
  const { symbols, symbol, candles, risk, alerts, cone, loading, analysing, error, load, select, runCone } =
    useDashboard();

  useEffect(() => {
    load();
    const id = setInterval(load, REFRESH_MS);
    return () => clearInterval(id);
  }, [load]);

  if (!loading && symbols.length === 0 && !error) {
    return (
      <p style={{ color: "var(--text-secondary)" }}>
        Aucune donnee de marche pour l'instant : la collecte tourne tous les quarts d'heure.
      </p>
    );
  }

  return (
    <>
      <div style={{ display: "flex", gap: "var(--space-3)", alignItems: "center", marginBottom: "var(--space-4)" }}>
        <select
          className="control"
          aria-label="Symbole"
          value={symbol ?? ""}
          onChange={(e) => select(e.target.value)}
        >
          {symbols.map((s) => (
            <option key={s.symbol} value={s.symbol}>
              {s.symbol}
            </option>
          ))}
        </select>
        {error && (
          <span role="alert" style={{ color: "var(--warning)" }}>
            {error}
          </span>
        )}
      </div>
      <div className="dashboard-grid">
        <section className="panel" aria-label="Graphique">
          <CandleChart candles={candles} cone={cone} />
        </section>
        <div>
          <RiskPanel risk={risk} />
          <AlertsPanel alerts={alerts} />
          <AnalysisPanel cone={cone} busy={analysing} onRun={runCone} />
        </div>
      </div>
    </>
  );
}
