import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Config Vite afinada para Tauri: puerto fijo, sin limpiar pantalla
// (para no pisar los logs de cargo), y HMR estable.
export default defineConfig({
  plugins: [react()],
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    watch: {
      // El backend Rust lo vigila cargo, no Vite.
      ignored: ["**/src-tauri/**"],
    },
  },
});
