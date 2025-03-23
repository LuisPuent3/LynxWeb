# Caso de Prueba LYNX_003: Prueba de Conexión API Frontend-Backend

## Información General

| Campo | Valor |
|-------|-------|
| Test Case ID | LYNX_003 |
| Test Case Description | Verificar la correcta conexión entre frontend y backend |
| Created By | Luis Ángel Puente Quevedo |
| Reviewed By | Oscar Pérez Luna |
| Version | 1.0 |
| QA Tester's Log | Versión inicial |
| Tester's Name | Luis Ángel Puente Quevedo |
| Date Tested | Pendiente |
| Test Case Status | No ejecutado |

## Prerrequisitos

- Entorno de desarrollo configurado
- Servidor backend en ejecución (`http://localhost:5000`)
- Aplicación frontend en ejecución (`npm run dev`)
- API configurada en ambos extremos

## Datos de Prueba

- **Ruta API**: /api/productos
- **Método**: GET

## Escenario de Prueba

Verificar que la aplicación frontend puede comunicarse correctamente con el backend

## Pasos de Prueba

| Paso # | Detalles del Paso | Resultados Esperados | Resultados Actuales | Estado |
|--------|-------------------|----------------------|---------------------|--------|
| 1 | Abrir las herramientas de desarrollo del navegador (pestaña Network) | Herramientas de desarrollo muestran panel de red | | |
| 2 | Navegar a la página de productos | La interfaz intenta cargar la lista de productos | | |
| 3 | Observar las llamadas de red | Se realiza petición GET a /api/productos sin errores CORS | | |
| 4 | Verificar respuesta del servidor | Código de estado 200 y datos en formato JSON | | |
| 5 | Verificar renderizado | Datos recibidos se muestran correctamente en la interfaz | | |

## Pruebas Automatizadas Implementadas

### 1. Prueba Unitaria con Mocks

**Archivo:** `ApiConnection.test.tsx`

Esta prueba utiliza mocks para simular la comunicación API y verificar:
- La correcta llamada al endpoint /productos
- El manejo adecuado de la respuesta
- La visualización de datos en la interfaz
- El manejo de errores cuando el servidor falla

**Código de Prueba Clave:**
```typescript
it('Debe realizar una petición GET a /api/productos y procesar la respuesta correctamente', async () => {
  // Preparar datos mock
  const mockProductos = [
    { id_producto: 1, nombre: 'Producto 1', precio: 100, descripcion: 'Descripción 1', categoria: 'Categoría 1', imagen: 'imagen1.jpg', cantidad: 1 },
    { id_producto: 2, nombre: 'Producto 2', precio: 200, descripcion: 'Descripción 2', categoria: 'Categoría 2', imagen: 'imagen2.jpg', cantidad: 1 }
  ];

  // Configurar el mock para devolver datos
  mockAxiosGet.mockResolvedValueOnce({ data: mockProductos });

  // Renderizar el componente
  render(
    <BrowserRouter>
      <ProductList addToCart={() => {}} searchTerm="" />
    </BrowserRouter>
  );

  // Verificar que la llamada a la API se realizó correctamente
  await waitFor(() => {
    expect(mockAxiosGet).toHaveBeenCalledWith('/productos');
  });

  // Verificar que los productos se muestran en la interfaz
  await waitFor(() => {
    expect(screen.getByText('Producto 1')).toBeInTheDocument();
    expect(screen.getByText('Producto 2')).toBeInTheDocument();
  });
});
```

### 2. Prueba de Integración Real

**Archivo:** `ApiConnectionIntegration.test.tsx`

Esta prueba realiza solicitudes reales a la API y verifica:
- Que el servidor responde con código 200
- Que la respuesta contiene datos en el formato correcto
- Que los encabezados CORS estén correctamente configurados

**Código de Prueba Clave:**
```typescript
it('Debe realizar una petición GET a /api/productos y recibir código 200', async () => {
  try {
    // Hacer una solicitud real a la API
    const response: AxiosResponse = await api.get('/productos');
    
    // Verificar código de estado
    expect(response.status).toBe(200);
    
    // Verificar que la respuesta es un array
    expect(Array.isArray(response.data)).toBe(true);
    
    // Opcional: Verificar la estructura de los datos
    if (response.data.length > 0) {
      const primerProducto = response.data[0];
      expect(primerProducto).toHaveProperty('id_producto');
      expect(primerProducto).toHaveProperty('nombre');
      expect(primerProducto).toHaveProperty('precio');
    }
  } catch (error) {
    // Manejo de errores...
    throw error; // Re-lanzar para que la prueba falle
  }
});
```

## Instrucciones para Ejecutar las Pruebas

### Ejecución de Pruebas Unitarias

```bash
# Ejecutar todas las pruebas
npm run test

# Ejecutar específicamente la prueba de conexión API
npm run test -- ApiConnection.test.tsx
```

### Ejecución de Pruebas de Integración

Requisito: El servidor backend debe estar en ejecución en http://localhost:5000

```bash
# Ejecutar pruebas de integración
npm run test -- ApiConnectionIntegration.test.tsx
```

## Evidencias a Recolectar

1. **Capturas de pantalla:**
   - Herramientas de desarrollo mostrando la petición a /api/productos
   - Respuesta JSON recibida del servidor
   - Renderizado de productos en la interfaz

2. **Logs:**
   - Logs del servidor mostrando la petición recibida
   - Logs de pruebas automatizadas (output de Jest/Vitest)

3. **Análisis CORS (si aplica):**
   - Capturas de encabezados de la petición y respuesta
   - Documentación de errores CORS si se presentan

## Notas Adicionales

- Este caso de prueba es esencial para verificar la funcionalidad base del sistema antes de continuar con pruebas más complejas
- Se recomienda ejecutar esta prueba después de cualquier cambio en la configuración de red o API
- Si se detectan problemas de CORS, verificar la configuración del servidor en `backed/src/app.js` o archivo equivalente

## Historial de Cambios

| Fecha | Versión | Autor | Cambios Realizados |
|-------|---------|-------|-------------------|
| 23/03/2025 | 1.0 | Luis Ángel Puente Quevedo | Versión inicial del caso de prueba |
| | | | |