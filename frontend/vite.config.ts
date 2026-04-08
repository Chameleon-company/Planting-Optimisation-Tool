import * as path from "path";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "/",
  plugins: [react()],
  build: {
    outDir: "./build/dist",
  },
  test: {
    environment: "jsdom",
    globals: true,
    css: false,
    setupFiles: "./src/test/setupTests.ts",
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "@@": path.resolve(__dirname),
    },
  },
});
