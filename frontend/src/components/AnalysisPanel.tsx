import { useState } from "react";

import type { AiResult } from "../api/types";
import { formatDate, formatPercent, formatPrice } from "../format";

interface Props {
  cone: AiResult | null;
  busy: boolean;
  onRun: (horizonHours: number) => void;
}

// Toute sortie affichee porte son niveau de confiance, sa fiabilite mesuree et
// son explication (US3.4, CONTRIBUTING regles 1 et 5). Aucune direction.
export default function AnalysisPanel({ cone, busy, onRun }: Props) {
  const [horizon, setHorizon] = useState(4);
  return (
    <section className="panel" aria-label="Analyse">
      <h2 className="panel-title">Amplitude probable</h2>
      <div style={{ display: "flex", gap: "var(--space-2)" }}>
        <select
          className="control"
          aria-label="Horizon"
          value={horizon}
          onChange={(e) => setHorizon(Number(e.target.value))}
        >
          <option value={4}>4 h</option>
          <option value={24}>24 h</option>
          <option value={72}>72 h</option>
        </select>
        <button type="button" className="button-primary" disabled={busy} onClick={() => onRun(horizon)}>
          {busy ? "Calcul..." : "Calculer"}
        </button>
      </div>
      {cone && (
        <div style={{ marginTop: "var(--space-3)" }}>
          <div className="metric">
            Intervalle {cone.value.horizon_hours} h{" "}
            <strong>
              {formatPrice(cone.value.lower)} – {formatPrice(cone.value.upper)}
            </strong>
          </div>
          <div className="metric">
            Confiance <strong>{formatPercent(cone.confidence)}</strong>
          </div>
          <div className="metric">
            Fiabilite mesuree{" "}
            <strong>
              {cone.reliability === null
                ? "non mesurable"
                : `${formatPercent(cone.reliability)} sur ${cone.value.backtest_size} cas`}
            </strong>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>{cone.explanation}</p>
          <p style={{ margin: 0, color: "var(--text-tertiary)", fontSize: 12 }}>
            {cone.value.note} Modele {cone.model_version}, {formatDate(cone.created_at)}.
          </p>
        </div>
      )}
    </section>
  );
}
