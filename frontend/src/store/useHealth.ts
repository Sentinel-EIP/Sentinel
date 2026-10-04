import { create } from "zustand";

import { API_URL } from "../api/client";

interface HealthState {
  status: string | null;
  checks: Record<string, string> | null;
  refresh: () => Promise<void>;
}

export const useHealth = create<HealthState>((set) => ({
  status: null,
  checks: null,
  refresh: async () => {
    try {
      // 503 quand une dependance manque : le corps porte quand meme le detail.
      const res = await fetch(`${API_URL}/health/ready`);
      const body = await res.json();
      set({ status: body.status, checks: body.checks });
    } catch {
      // Pas de statut inconnu affiche comme une erreur : c'est un etat "perime".
      set({ status: "hors ligne", checks: null });
    }
  },
}));
