import '@testing-library/jest-dom';

// Configuración global para Testing Library
window.matchMedia = window.matchMedia || function() {
  return {
    matches: false,
    addListener: function() {},
    removeListener: function() {}
  };
};

// Polyfill para ResizeObserver que puede no estar disponible en JSDOM
if (!window.ResizeObserver) {
  window.ResizeObserver = class ResizeObserver {
    constructor(callback) {
      this.callback = callback;
    }
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

// Suprimir warnings específicos para pruebas
const originalConsoleError = console.error;
console.error = (...args) => {
  // Ignorar errores específicos que no afectan a las pruebas
  if (
    args[0]?.includes?.('Warning: ReactDOM.render is no longer supported') ||
    args[0]?.includes?.('Warning: useLayoutEffect does nothing on the server')
  ) {
    return;
  }
  originalConsoleError(...args);
}; 