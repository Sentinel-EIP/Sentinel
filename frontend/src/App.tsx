import { useEffect } from "react";

import { useHealth } from "./store/useHealth";

export default function App() {
  const { status, checks, refresh } = useHealth();

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 10_000);
    return () => clearInterval(id);
  }, [refresh]);

  return (
    <main style={{ padding: "var(--space-5)", fontFamily: "var(--font-ui)" }}>
      <h1 style={{ color: "var(--text-primary)" }}>Sentinel</h1>
      <p style={{ color: "var(--text-secondary)" }}>
        Squelette applicatif. Le dashboard suit le design system v1.2.
      </p>
      <section
        style={{
          marginTop: "var(--space-4)",
          padding: "var(--space-3)",
          background: "var(--surface-raised)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-md)",
        }}
      >
        <div style={{ color: "var(--text-tertiary)", fontSize: 11, letterSpacing: ".13em" }}>
          ETAT DE L'API
        </div>
        <div
          style={{
            fontFamily: "var(--font-numeric)",
            fontVariantNumeric: "tabular-nums",
            fontSize: 22,
            color: status === "ok" ? "var(--value-positive)" : "var(--state-stale)",
          }}
        >
          {status ?? "..."}
        </div>
        {checks && (
          <pre style={{ color: "var(--text-secondary)", fontSize: 11 }}>
            {JSON.stringify(checks, null, 2)}
          </pre>
        )}
      </section>
    </main>
  );
}
