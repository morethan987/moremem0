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
    allowedHosts: ["frp-put.com"],
  host: '0.0.0.0',
  proxy: {
    '/api': {
      target: 'http://localhost:80',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ""),
      secure: false
    }
  }
}
})
