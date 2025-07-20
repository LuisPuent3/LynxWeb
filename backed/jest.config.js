// jest.config.js en c:/xampp/htdocs/LynxWeb/backed/
export default {
  testEnvironment: 'node',
  // La ruta es relativa al directorio raíz del proyecto Jest (donde está jest.config.js)
  // o puedes usar <rootDir> que se refiere a la ubicación de este archivo de configuración.
  testMatch: ['<rootDir>/tests/**/*.test.js'],
  // Si tus archivos de backend (y sus tests) usan ES Modules (import/export)
  // y no estás usando Babel, podrías necesitar configurar transform para ES Modules
  // o asegurar que tu package.json en 'backed/' tenga "type": "module".
  // Por ahora, lo dejamos simple. Si hay errores de sintaxis de ES Modules,
  // esto necesitará ser ajustado.
  transform: {}, // Añadido para evitar problemas comunes con ES Modules si no hay otra transformación.
  // Silenciar advertencias de seguridad de JSDOM si no es necesario para pruebas de nodo
  // No es estrictamente necesario aquí ya que testEnvironment es 'node'.
  // setupFilesAfterEnv: ['./jest.setup.js'], // Si necesitas un archivo de setup para Jest
  // moduleNameMapper: { // Si necesitas mapear rutas
  //   '^@/(.*)$': '<rootDir>/src/$1',
  // },
  // collectCoverage: true, // Descomenta para habilitar la recolección de cobertura
  // coverageDirectory: "coverage", // Directorio para los reportes de cobertura
  // coverageProvider: "v8", // o "babel"
  // coverageReporters: ["json", "lcov", "text", "clover"],
  // collectCoverageFrom: [ // Patrones para incluir/excluir archivos de la cobertura
  //   "**/*.js",
  //   "!**/node_modules/**",
  //   "!**/vendor/**",
  //   "!**/tests/**",
  //   "!jest.config.js",
  // ],
};
