/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    watch: { usePolling: true },   // necessaire sous WSL/Docker
  },
  test: {
    environment: "jsdom",
    setupFiles: ["src/test/setup.ts"],
    coverage: {
      reporter: ["text", "lcov"],
      // Politique de tests : 60 % minimum sur le frontend. `lines: 60` au premier
      // niveau de coverage etait ignore par Vitest ; seul `thresholds` echoue.
      thresholds: { lines: 60, statements: 60, functions: 60, branches: 60 },
    },
  },
});
