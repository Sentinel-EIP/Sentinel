import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { AiResult, Alert, RiskSummary } from "../api/types";
import { useAuth } from "../store/useAuth";
import { useDashboard } from "../store/useDashboard";
import { mockApi, type Route } from "../test/mockApi";
import { chart } from "../test/setup";
import Dashboard from "./Dashboard";

const ok = (body: unknown): Route => () => ({ status: 200, body });

const symbols = [
  { symbol: "BTCEUR", timeframe: "1h", first: "2026-09-01T00:00:00Z", last: "2026-10-04T10:00:00Z", count: 800 },
  { symbol: "ETHEUR", timeframe: "1h", first: "2026-09-01T00:00:00Z", last: "2026-10-04T10:00:00Z", count: 800 },
  { symbol: "BTCEUR", timeframe: "1d", first: "2026-07-01T00:00:00Z", last: "2026-10-03T00:00:00Z", count: 90 },
];
const candles = [
  { ts: "2026-10-04T09:00:00Z", open: 1, high: 2, low: 0.5, close: 1.5, volume: 3 },
  { ts: "2026-10-04T10:00:00Z", open: 1.5, high: 2, low: 1, close: 1.8, volume: 2 },
];
const critical: Alert = {
  symbol: "BTCEUR",
  level: "critical",
  code: "drawdown",
  message: "Drawdown courant 25 % >= 20 %",
  value: 0.25,
  threshold: 0.2,
};
const stale: Alert = { ...critical, symbol: "ETHEUR", level: "stale", code: "data_stale", message: "Donnees perimees" };
const risk = (symbol: string): RiskSummary => ({
  symbol,
  timeframe: "1h",
  as_of: "2026-10-04T10:00:00Z",
  last_price: 75000,
  volatility: 0.45,
  max_drawdown: 0.3,
  current_drawdown: 0.25,
  sample_size: 720,
  alerts: symbol === "BTCEUR" ? [critical] : [],
});
const cone: AiResult = {
  id: 1,
  kind: "volatility_cone",
  symbol: "BTCEUR",
  model_version: "realized-vol-v1",
  confidence: 0.8,
  reliability: 0.79,
  explanation: "Volatilite realisee sur 499 rendements.",
  value: { reference_price: 75000, lower: 74000, upper: 76000, horizon_hours: 4, backtest_size: 465, note: "Amplitude probable. Aucune direction implicite." },
  created_at: "2026-10-04T10:05:00Z",
};

function routes(overrides: Record<string, Route> = {}): Record<string, Route> {
  return {
    "GET /market/symbols": ok(symbols),
    "GET /alerts": ok([critical, stale]),
    "GET /market/candles": ok(candles),
    "GET /risk/summary": () => ({ status: 200, body: risk(useDashboard.getState().symbol ?? "") }),
    "GET /analysis/results": ok([]),
    "POST /analysis/volatility": ok(cone),
    ...overrides,
  };
}

describe("Dashboard", () => {
  beforeEach(() => {
    useAuth.setState({ token: "jeton", username: "alice" });
    useDashboard.setState({ symbols: [], symbol: null, candles: [], risk: null, alerts: [], cone: null, error: null });
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("affiche graphique, risque et alertes du premier symbole", async () => {
    const fetchMock = mockApi(routes());
    render(<Dashboard />);
    expect(await screen.findByText("Risque — BTCEUR")).toBeTruthy();
    await waitFor(() => expect(chart.series.setData).toHaveBeenLastCalledWith(expect.arrayContaining([expect.objectContaining({ close: 1.8 })])));

    // Seul le rouge du drawdown, seuil critique depasse.
    expect(screen.getByText("25 %").getAttribute("style")).toContain("--risk-critical");
    expect(screen.getByText("45 %").getAttribute("style")).toContain("--text-primary");
    expect(screen.getByText("Critique")).toBeTruthy();
    expect(screen.getByText("Perime")).toBeTruthy();

    // Seuls les symboles 1h sont proposes ; le jeton accompagne chaque appel.
    expect(screen.getAllByRole("option").map((o) => o.textContent)).toEqual(["BTCEUR", "ETHEUR"].concat(["4 h", "24 h", "72 h"]));
    const init = fetchMock.mock.calls.find(([url]) => String(url).includes("/market/candles"))?.[1];
    expect((init?.headers as Record<string, string>).Authorization).toBe("Bearer jeton");
  });

  it("change de symbole", async () => {
    mockApi(routes());
    render(<Dashboard />);
    await screen.findByText("Risque — BTCEUR");
    fireEvent.change(screen.getByLabelText("Symbole"), { target: { value: "ETHEUR" } });
    expect(await screen.findByText("Risque — ETHEUR")).toBeTruthy();
  });

  it("calcule le cone et l'affiche avec confiance, fiabilite et explication", async () => {
    mockApi(routes());
    render(<Dashboard />);
    await screen.findByText("Risque — BTCEUR");
    fireEvent.change(screen.getByLabelText("Horizon"), { target: { value: "24" } });
    fireEvent.click(screen.getByRole("button", { name: "Calculer" }));
    expect(await screen.findByText("79 % sur 465 cas")).toBeTruthy();
    expect(screen.getByText("80 %")).toBeTruthy();
    expect(screen.getByText(cone.explanation)).toBeTruthy();
    expect(screen.getByText(/Aucune direction implicite/)).toBeTruthy();
    expect(chart.series.createPriceLine).toHaveBeenCalledTimes(2);
  });

  it("affiche l'erreur d'analyse (historique insuffisant)", async () => {
    mockApi(
      routes({
        "POST /analysis/volatility": () => ({
          status: 409,
          body: { error: { code: "conflict", message: "Historique insuffisant : 10 bougies, 31 minimum" } },
        }),
      }),
    );
    render(<Dashboard />);
    await screen.findByText("Risque — BTCEUR");
    fireEvent.click(screen.getByRole("button", { name: "Calculer" }));
    expect((await screen.findByRole("alert")).textContent).toContain("Historique insuffisant");
  });

  it("indique l'absence de donnees", async () => {
    mockApi(routes({ "GET /market/symbols": ok([]), "GET /alerts": ok([]) }));
    render(<Dashboard />);
    expect(await screen.findByText(/Aucune donnee de marche/)).toBeTruthy();
  });

  it("deconnecte quand le jeton a expire", async () => {
    mockApi(
      routes({
        "GET /market/symbols": () => ({ status: 401, body: { error: { code: "unauthorized", message: "Authentification requise" } } }),
      }),
    );
    render(<Dashboard />);
    await waitFor(() => expect(useAuth.getState().token).toBeNull());
  });

  it("garde le dernier cone calcule pour le symbole", async () => {
    mockApi(routes({ "GET /analysis/results": ok([cone]) }));
    render(<Dashboard />);
    expect(await screen.findByText("79 % sur 465 cas")).toBeTruthy();
  });
});
