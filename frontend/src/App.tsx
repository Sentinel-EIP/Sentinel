import HealthBadge from "./components/HealthBadge";
import LoginForm from "./components/LoginForm";
import { useAuth } from "./store/useAuth";

export default function App() {
  const { token, username, logout } = useAuth();

  return (
    <div style={{ minHeight: "100vh", fontFamily: "var(--font-ui)" }}>
      <header
        style={{
          display: "flex",
          alignItems: "center",
          gap: "var(--space-4)",
          padding: "var(--space-3) var(--space-5)",
          borderBottom: "1px solid var(--border-subtle)",
          background: "var(--surface-raised)",
        }}
      >
        <strong style={{ letterSpacing: ".04em" }}>Sentinel</strong>
        <span style={{ flex: 1 }} />
        <HealthBadge />
        {token && (
          <>
            <span style={{ color: "var(--text-secondary)" }}>{username}</span>
            <button
              type="button"
              onClick={logout}
              style={{
                minHeight: "var(--touch-target-min)",
                background: "transparent",
                color: "var(--text-secondary)",
                border: "1px solid var(--border-strong)",
                borderRadius: "var(--radius-sm)",
                padding: "0 var(--space-3)",
                font: "inherit",
                cursor: "pointer",
              }}
            >
              Deconnexion
            </button>
          </>
        )}
      </header>
      <main style={{ padding: "var(--space-5)" }}>
        {token ? (
          <p style={{ color: "var(--text-secondary)" }}>Connecte en tant que {username}.</p>
        ) : (
          <LoginForm />
        )}
      </main>
    </div>
  );
}
