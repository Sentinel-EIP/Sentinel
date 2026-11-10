import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { useAuth } from "./store/useAuth";
import { useHealth } from "./store/useHealth";
import { mockApi, type Route } from "./test/mockApi";

const healthy: Route = () => ({ status: 200, body: { status: "ok", checks: { database: "ok", ml: "ok" } } });

describe("App", () => {
  // Les stores zustand sont des singletons de module : on repart d'un etat vierge.
  beforeEach(() => {
    useHealth.setState({ status: null, checks: null });
    useAuth.setState({ token: null, username: null });
    sessionStorage.clear();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("affiche le statut renvoye par /health/ready", async () => {
    mockApi({ "GET /health/ready": healthy });
    render(<App />);
    expect(await screen.findByText("ok")).toBeTruthy();
  });

  it("affiche hors ligne quand l'API est injoignable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    render(<App />);
    expect(await screen.findByText("hors ligne")).toBeTruthy();
  });

  it("connecte l'utilisateur puis le deconnecte", async () => {
    mockApi({
      "GET /health/ready": healthy,
      "POST /auth/login": () => ({ status: 200, body: { access_token: "jeton" } }),
    });
    render(<App />);
    fireEvent.change(screen.getByLabelText("Nom d'utilisateur"), { target: { value: "alice" } });
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "mot-de-passe-solide" } });
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }));
    expect(await screen.findByText("alice")).toBeTruthy();
    expect(JSON.parse(sessionStorage.getItem("sentinel.session")!).token).toBe("jeton");

    fireEvent.click(screen.getByRole("button", { name: "Deconnexion" }));
    expect(await screen.findByRole("button", { name: "Se connecter" })).toBeTruthy();
    expect(sessionStorage.getItem("sentinel.session")).toBeNull();
  });

  it("affiche l'erreur du backend sans la colorer en rouge", async () => {
    mockApi({
      "GET /health/ready": healthy,
      "POST /auth/login": () => ({ status: 401, body: { error: { code: "unauthorized", message: "Identifiants invalides" } } }),
    });
    render(<App />);
    fireEvent.change(screen.getByLabelText("Nom d'utilisateur"), { target: { value: "alice" } });
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "mauvais" } });
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }));
    const alert = await screen.findByRole("alert");
    expect(alert.textContent).toBe("Identifiants invalides");
    expect(alert.getAttribute("style")).toContain("--field-invalid");
  });

  it("inscrit puis connecte", async () => {
    const fetchMock = mockApi({
      "GET /health/ready": healthy,
      "POST /auth/register": () => ({ status: 201, body: { id: 1, username: "bob" } }),
      "POST /auth/login": () => ({ status: 200, body: { access_token: "jeton" } }),
    });
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Pas de compte ? S'inscrire" }));
    fireEvent.change(screen.getByLabelText("Nom d'utilisateur"), { target: { value: "bob" } });
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "mot-de-passe-solide" } });
    fireEvent.click(screen.getByRole("button", { name: "Creer le compte" }));
    expect(await screen.findByText("bob")).toBeTruthy();
    const calls = fetchMock.mock.calls.map(([url, init]) => `${init?.method ?? "GET"} ${new URL(url).pathname}`);
    expect(calls).toContain("POST /auth/register");
  });

  it("signale une API injoignable a la connexion", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    render(<App />);
    fireEvent.change(screen.getByLabelText("Nom d'utilisateur"), { target: { value: "alice" } });
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "x" } });
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }));
    expect((await screen.findByRole("alert")).textContent).toBe("API injoignable");
  });
});
