import '@testing-library/jest-dom';
import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

// Configuración global para que las pruebas con React funcionen correctamente
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

// Configuración global para mocks
global.fetch = vi.fn();

// Para solucionar errores con localStorage en jsdom
if (!global.localStorage) {
  class LocalStorageMock {
    store: Record<string, string> = {};

    getItem(key: string) {
      return this.store[key] || null;
    }

    setItem(key: string, value: string) {
      this.store[key] = value;
    }

    removeItem(key: string) {
      delete this.store[key];
    }

    clear() {
      this.store = {};
    }
  }

  Object.defineProperty(global, 'localStorage', {
    value: new LocalStorageMock(),
    writable: true
  });
}

// Para solucionar errores con matchMedia en jsdom
if (!global.matchMedia) {
  global.matchMedia = () => ({
    matches: false,
    addListener: () => {},
    removeListener: () => {}
  } as MediaQueryList);
} 