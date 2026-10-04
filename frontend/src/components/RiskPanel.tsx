import type { RiskSummary } from "../api/types";
import { formatDate, formatPercent, formatPrice } from "../format";

// Couleur reservee : --risk-critical seulement si un seuil critique est depasse
// (design system v1.2, CONTRIBUTING regle 3).
function levelColor(risk: RiskSummary, code: string): string {
  const alert = risk.alerts.find((a) => a.code === code);
  if (alert?.level === "critical") return "var(--risk-critical)";
  if (alert?.level === "warning") return "var(--warning)";
  return "var(--text-primary)";
}

export default function RiskPanel({ risk }: { risk: RiskSummary | null }) {
  if (!risk) return null;
  return (
    <section className="panel" aria-label="Risque">
      <h2 className="panel-title">Risque — {risk.symbol}</h2>
      <div className="metric">
        Dernier prix <strong>{formatPrice(risk.last_price)}</strong>
      </div>
      <div className="metric">
        Volatilite annualisee{" "}
        <strong style={{ color: levelColor(risk, "volatility") }}>{formatPercent(risk.volatility)}</strong>
      </div>
      <div className="metric">
        Drawdown courant{" "}
        <strong style={{ color: levelColor(risk, "drawdown") }}>{formatPercent(risk.current_drawdown)}</strong>
      </div>
      <div className="metric">
        Drawdown maximal <strong>{formatPercent(risk.max_drawdown)}</strong>
      </div>
      <p style={{ margin: "var(--space-2) 0 0", color: "var(--text-tertiary)", fontSize: 12 }}>
        {risk.sample_size} bougies {risk.timeframe}, derniere : {formatDate(risk.as_of)}
      </p>
    </section>
  );
}
