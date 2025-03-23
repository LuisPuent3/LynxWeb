# Pruebas Automatizadas - Proyecto LYNX

Este directorio contiene pruebas automatizadas para el proyecto LYNX, que verifican diferentes aspectos de la aplicación según los casos de prueba especificados en el Plan de Pruebas.

## Casos de Prueba Implementados

1. **LYNX_003**: Prueba de Conexión API Frontend-Backend
   - Archivos: `ApiConnection.test.tsx`, `ApiConnectionIntegration.test.tsx`, `ApiConnectionSimple.test.ts`
   - Documentación: `LYNX_003_ApiConnection.md`, `LYNX_003_TestManualResults.md`
   - Script de automatización: `runLYNX003Tests.js`

2. **LYNX_010**: Prueba de Manejo de Errores API
   - Archivos: `ApiErrorHandling.test.ts`
   - Documentación: `LYNX_010_ApiErrorHandling.md`
   - Script de automatización: `runLYNX010Tests.mjs`

## Cómo Ejecutar las Pruebas

### Ejecución Manual

Para ejecutar las pruebas manualmente, utiliza los siguientes comandos:

```bash
# Ejecutar todas las pruebas
npm run test

# Ejecutar un archivo de prueba específico
npm run test -- ApiConnection.test.tsx

# Ejecutar pruebas en modo observador
npm run test:watch
```

### Documentación Automatizada

Para ejecutar las pruebas y actualizar automáticamente la documentación, utiliza los scripts proporcionados:

```bash
# Para el caso LYNX_003
node src/__tests__/runLYNX003Tests.js

# Para el caso LYNX_010
node src/__tests__/runLYNX010Tests.mjs
```

## Estructura de Archivos Recomendada

Para una mejor organización, se recomienda estructurar los tests de la siguiente manera:

```
src/
└── __tests__/
    ├── cases/                      # Carpeta principal de casos de prueba
    │   ├── LYNX_003/               # Un directorio por caso de prueba
    │   │   ├── ApiConnection.test.tsx
    │   │   ├── ApiConnectionIntegration.test.tsx
    │   │   ├── LYNX_003_ApiConnection.md
    │   │   └── runLYNX003Tests.js
    │   ├── LYNX_010/
    │   │   ├── ApiErrorHandling.test.ts
    │   │   ├── LYNX_010_ApiErrorHandling.md
    │   │   └── runLYNX010Tests.mjs
    │   └── ...
    ├── mocks/                      # Mocks compartidos entre pruebas
    │   ├── api-mocks.ts
    │   └── ...
    ├── utils/                      # Utilidades compartidas para pruebas
    │   ├── test-helpers.ts
    │   └── ...
    └── README.md                   # Este archivo
```

## Convenciones de Nombrado

- Prefija los archivos de prueba con el ID del caso de prueba (ej. `LYNX_010_`).
- Para pruebas unitarias, utiliza `*.test.ts`.
- Para pruebas que incluyen componentes React, utiliza `*.test.tsx`.
- Para documentación, utiliza `*_nombreDescriptivo.md`.

## Cómo Añadir Nuevos Casos de Prueba

1. Consulta el archivo `docs/CasosPruebas.txt` para seleccionar el caso a implementar.
2. Crea una carpeta para el caso de prueba dentro de `__tests__/cases/`.
3. Implementa los archivos de prueba según los requisitos del caso.
4. Crea un archivo de documentación para registrar los resultados.
5. Opcionalmente, crea un script de automatización para ejecutar las pruebas y actualizar la documentación.

## Categorías de Pruebas

Para proyectos más grandes, considera organizar las pruebas por categorías:

- **Unitarias**: Pruebas de funciones y componentes aislados.
- **Integración**: Pruebas de interacción entre componentes.
- **E2E**: Pruebas de flujos completos de usuario.
- **API**: Pruebas específicas de conexión con APIs.

## Prerrequisitos para las Pruebas

- Node.js y npm instalados
- Dependencias del proyecto instaladas (`npm install`)
- Entorno de desarrollo configurado
- Para pruebas de integración, el servidor backend debe estar en ejecución

## Buenas Prácticas

- Mantén las pruebas enfocadas en un solo comportamiento.
- Utiliza mocks para dependencias externas (como APIs).
- Actualiza la documentación después de cada ejecución de pruebas.
- Establece un umbral mínimo de cobertura de código (ej. 80%).
- Ejecuta las pruebas en el pipeline de CI/CD. 