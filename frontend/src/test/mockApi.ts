import { vi } from "vitest";

export type Route = (body: unknown) => { status: number; body: unknown };

// fetch factice : route par "METHODE /chemin" (sans la query string).
export function mockApi(routes: Record<string, Route>) {
  const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
    const path = new URL(url).pathname;
    const key = `${init?.method ?? "GET"} ${path}`;
    const route = routes[key];
    if (!route) return { ok: false, status: 404, json: async () => ({ error: { code: "not_found", message: key } }) };
    const { status, body } = route(init?.body ? JSON.parse(String(init.body)) : undefined);
    return { ok: status < 400, status, json: async () => body };
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}
