import { type FormEvent, useState } from "react";

import { ApiError } from "../api/client";
import { useAuth } from "../store/useAuth";

const field = {
  display: "block",
  width: "100%",
  minHeight: "var(--touch-target-min)",
  marginTop: "var(--space-1)",
  padding: "0 var(--space-3)",
  background: "var(--field-bg)",
  border: "1px solid var(--field-border)",
  borderRadius: "var(--radius-sm)",
  color: "var(--text-primary)",
  font: "inherit",
} as const;

export default function LoginForm() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await (mode === "login" ? login : register)(username, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur inattendue");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form
      onSubmit={submit}
      aria-label={mode === "login" ? "Connexion" : "Inscription"}
      style={{
        maxWidth: 360,
        margin: "var(--space-6) auto",
        padding: "var(--space-5)",
        background: "var(--surface-raised)",
        border: "1px solid var(--border-subtle)",
        borderRadius: "var(--radius-lg)",
      }}
    >
      <h1 style={{ marginTop: 0 }}>Sentinel</h1>
      <label style={{ display: "block", color: "var(--text-secondary)" }}>
        Nom d'utilisateur
        <input
          style={field}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          required
        />
      </label>
      <label style={{ display: "block", marginTop: "var(--space-3)", color: "var(--text-secondary)" }}>
        Mot de passe
        <input
          style={field}
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          minLength={mode === "register" ? 12 : undefined}
          required
        />
      </label>
      {error && (
        <p role="alert" style={{ color: "var(--field-invalid)" }}>
          {error}
        </p>
      )}
      <button
        type="submit"
        disabled={busy}
        style={{
          width: "100%",
          minHeight: "var(--touch-target-min)",
          marginTop: "var(--space-4)",
          background: "var(--accent)",
          color: "var(--accent-ink)",
          border: "none",
          borderRadius: "var(--radius-sm)",
          font: "inherit",
          fontWeight: 600,
          cursor: "pointer",
        }}
      >
        {mode === "login" ? "Se connecter" : "Creer le compte"}
      </button>
      <button
        type="button"
        onClick={() => {
          setMode(mode === "login" ? "register" : "login");
          setError(null);
        }}
        style={{
          width: "100%",
          minHeight: "var(--touch-target-min)",
          marginTop: "var(--space-2)",
          background: "transparent",
          color: "var(--text-secondary)",
          border: "none",
          font: "inherit",
          cursor: "pointer",
        }}
      >
        {mode === "login" ? "Pas de compte ? S'inscrire" : "Deja un compte ? Se connecter"}
      </button>
    </form>
  );
}
