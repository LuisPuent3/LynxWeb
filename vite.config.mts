import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],  server: {
    proxy: {
      '/api': 'http://localhost:8004'  // API LCLN dinámico
    },
    port: 5174  // Puerto original del frontend
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})