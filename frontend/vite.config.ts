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
    coverage: { reporter: ["text", "lcov"], lines: 60 },
  },
});
