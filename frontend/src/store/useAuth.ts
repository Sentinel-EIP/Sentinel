import { create } from "zustand";

import { apiFetch } from "../api/client";

// Jeton en sessionStorage : survit a un rechargement, pas a la fermeture de
// l'onglet. Stockage indisponible (navigation privee...) : session en memoire.
const KEY = "sentinel.session";

interface Session {
  token: string;
  username: string;
}

function load(): Session | null {
  try {
    const raw = sessionStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as Session) : null;
  } catch {
    return null;
  }
}

function save(session: Session | null): void {
  try {
    if (session) sessionStorage.setItem(KEY, JSON.stringify(session));
    else sessionStorage.removeItem(KEY);
  } catch {
    // stockage indisponible : la session reste en memoire
  }
}

interface AuthState {
  token: string | null;
  username: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const initial = load();

export const useAuth = create<AuthState>((set, get) => ({
  token: initial?.token ?? null,
  username: initial?.username ?? null,
  login: async (username, password) => {
    const { access_token } = await apiFetch<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: { username, password },
    });
    save({ token: access_token, username });
    set({ token: access_token, username });
  },
  register: async (username, password) => {
    await apiFetch("/auth/register", { method: "POST", body: { username, password } });
    await get().login(username, password);
  },
  logout: () => {
    save(null);
    set({ token: null, username: null });
  },
}));
