import type { Alert, AlertLevel } from "../api/types";

const STYLE: Record<AlertLevel, { color: string; background: string; label: string }> = {
  critical: { color: "var(--risk-critical)", background: "var(--risk-critical-soft)", label: "Critique" },
  warning: { color: "var(--warning)", background: "var(--warning-soft)", label: "Attention" },
  stale: { color: "var(--state-stale)", background: "var(--state-stale-soft)", label: "Perime" },
};

export default function AlertsPanel({ alerts }: { alerts: Alert[] }) {
  return (
    <section className="panel" aria-label="Alertes">
      <h2 className="panel-title">Alertes</h2>
      {alerts.length === 0 ? (
        <p style={{ margin: 0, color: "var(--text-secondary)" }}>Aucune alerte en cours.</p>
      ) : (
        <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
          {alerts.map((a) => (
            <li
              key={`${a.symbol}-${a.code}`}
              style={{
                padding: "var(--space-2) var(--space-3)",
                marginTop: "var(--space-2)",
                borderRadius: "var(--radius-sm)",
                background: STYLE[a.level].background,
                borderLeft: `3px solid ${STYLE[a.level].color}`,
              }}
            >
              <span style={{ color: STYLE[a.level].color, fontWeight: 600 }}>{STYLE[a.level].label}</span>{" "}
              <span style={{ color: "var(--text-primary)" }}>{a.symbol}</span>
              <div style={{ color: "var(--text-secondary)", fontSize: 13 }}>{a.message}</div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
