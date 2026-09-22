import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const apiOrigin = process.env.VITE_API_ORIGIN ?? "http://127.0.0.1:8060";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts"
  },
  server: {
    host: "0.0.0.0",
    port: 3066,
    strictPort: true,
    proxy: {
      "/api": apiOrigin,
      "/health": apiOrigin
    }
  },
  preview: {
    host: "0.0.0.0",
    port: 3066,
    strictPort: true
  }
});
