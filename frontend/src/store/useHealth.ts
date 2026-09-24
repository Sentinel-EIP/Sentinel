import { create } from "zustand";

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

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
      const res = await fetch(`${API}/health/ready`);
      const body = await res.json();
      set({ status: body.status, checks: body.checks });
    } catch {
      // Pas de statut inconnu affiche comme une erreur : c'est un etat "perime".
      set({ status: "hors ligne", checks: null });
    }
  },
}));
