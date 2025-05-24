import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:5000',
      '/uploads': 'http://localhost:5000'
    },
    open: true
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  base: '/',
  build: {
    rollupOptions: {
      onwarn(warning, warn) {
        // Ignorar warnings de TypeScript durante el build
        if (warning.code === 'TYPESCRIPT_ERROR') return;
        warn(warning);
      }
    }
  }
})