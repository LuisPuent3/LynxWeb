/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    deps: {
      inline: ['react-router-dom']
    },
    css: true,
    environmentOptions: {
      jsdom: {
        url: 'http://localhost/'
      }
    }
  },
}); 