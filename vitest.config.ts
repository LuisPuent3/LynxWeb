import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    // setupFiles: ['./cliente/src/__tests__/setup.ts']
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './cliente/src'),
      '@utils': resolve(__dirname, './cliente/src/utils'),
      '@components': resolve(__dirname, './cliente/src/components'),
      '@tests': resolve(__dirname, './cliente/src/__tests__')
    }
  }
}); 