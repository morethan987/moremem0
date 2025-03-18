import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      buffer: 'buffer'
    },
  },
  server: {
    allowedHosts: ["moremem.xyz"],
  host: '0.0.0.0',
  proxy: {
    '/api': {
      target: '/',
      changeOrigin: false,
      rewrite: (path) => path,
      secure: true,
      ws: true
    }
  }
}
})
