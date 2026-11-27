import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { useHealth } from "./store/useHealth";

describe("App", () => {
  // Le store zustand est un singleton de module : on repart d'un etat vierge.
  beforeEach(() => useHealth.setState({ status: null, checks: null }));

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("affiche le statut renvoye par /health/ready", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        json: async () => ({ status: "ok", checks: { database: "ok", ml: "ok" } }),
      }),
    );
    render(<App />);
    expect(await screen.findByText("ok")).toBeTruthy();
  });

  it("affiche hors ligne quand l'API est injoignable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    render(<App />);
    expect(await screen.findByText("hors ligne")).toBeTruthy();
  });
});
