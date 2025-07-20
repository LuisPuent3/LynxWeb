/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.ts', // o js, si es un archivo js
    include: ['src/**/*.test.{ts,tsx,js,jsx}'], // Asegura que solo se incluyan tests del frontend
    // Opcional: excluir node_modules u otros directorios si es necesario
    // exclude: ['node_modules', 'dist', 'backed'],
  },
  resolve: {
    alias: {
      // Configura alias si los usas en tus importaciones, ej:
      // '@/': '/src/'
    },
  },
});