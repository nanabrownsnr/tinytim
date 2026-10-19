import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  esbuild: { jsx: "automatic" },
  plugins: [viteSingleFile()],
  build: { outDir: "dist" },
});
