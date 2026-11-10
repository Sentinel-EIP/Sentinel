import { useEffect } from "react";

import { useHealth } from "../store/useHealth";

// Etat de l'API (base et ML). Interroge toutes les 10 s.
export default function HealthBadge() {
  const { status, checks, refresh } = useHealth();

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 10_000);
    return () => clearInterval(id);
  }, [refresh]);

  const color =
    status === "ok"
      ? "var(--value-positive)"
      : status === "hors ligne"
        ? "var(--state-offline)"
        : "var(--state-stale)";
  const detail = checks ? Object.entries(checks).map(([k, v]) => `${k} : ${v}`).join(", ") : "";

  return (
    <span title={detail} style={{ display: "inline-flex", gap: "var(--space-2)", alignItems: "center" }}>
      <span style={{ color: "var(--text-tertiary)", fontSize: 11, letterSpacing: ".13em" }}>API</span>
      <span style={{ fontFamily: "var(--font-numeric)", color }}>{status ?? "..."}</span>
    </span>
  );
}
