# LYNX_010: Prueba de Manejo de Errores API

## Descripción

Este documento registra los resultados de las pruebas automatizadas para el caso de prueba LYNX_010, que verifica el manejo de errores en la API del sistema LYNX.

## Detalles del Caso de Prueba

| Test Case ID | LYNX_010 |
|--------------|----------|
| Test Case Description | Verificar el manejo de errores en la API |
| Created By | Luis Ángel Puente Quevedo |
| Reviewed By | Oscar Pérez Luna |
| Version | 1.0 |
| QA Tester's Log | Versión inicial |
| Tester's Name | Luis Ángel Puente Quevedo |
| Date Tested | 22/03/2025 |
| Test Case Status | Exitoso |

## Prerrequisitos

1. Entorno de desarrollo configurado
2. Servidor backend en ejecución
3. Framework de pruebas Vitest configurado

## Datos de Prueba

1. Ruta API inexistente = /api/rutainexistente
2. Producto inexistente = ID 9999
3. Token inválido = "Bearer invalidtoken12345"
4. Datos POST inválidos (falta el campo nombre)
5. Token con permisos insuficientes

## Escenario de Prueba

Verificar que la API maneja correctamente los errores y devuelve respuestas apropiadas con los códigos HTTP correctos y mensajes de error claros.

## Pasos y Resultados

| Paso # | Detalles del Paso | Resultados Esperados | Resultados Actuales | Estado |
|--------|-------------------|----------------------|---------------------|--------|
| 1 | Enviar petición para probar ruta inexistente | Código 404 con mensaje de error claro | Código 404 con mensaje "Ruta no encontrada" | Pasado |
| 2 | Enviar petición para probar producto inexistente | Código 404 con mensaje de error claro | Código 404 con mensaje "Producto no encontrado" | Pasado |
| 3 | Enviar petición para probar autenticación requerida | Código 401 con mensaje de error claro | Código 401 con mensaje "Se requiere autenticación" | Pasado |
| 4 | Enviar petición para probar token inválido | Código 401 con mensaje de error claro | Código 401 con mensaje "Token inválido" | Pasado |
| 5 | Enviar petición para probar datos inválidos en POST | Código 400 con mensaje de error claro | Código 400 con mensaje "Datos inválidos" | Pasado |
| 6 | Enviar petición para probar permisos insuficientes | Código 403 con mensaje de error claro | Código 403 con mensaje "Acceso denegado" | Pasado |

## Resultados de Pruebas Automatizadas

```
PS C:\xampp\htdocs\LynxWeb\cliente> npm run test -- ApiErrorHandling.test.ts

> lynxwebpage@0.0.0 test
> vitest run ApiErrorHandling.test.ts


 RUN  v3.0.9 C:/xampp/htdocs/LynxWeb


 ❯ cliente/src/__tests__/ApiErrorHandling.test.ts [queued]
stdout | cliente/src/__tests__/ApiErrorHandling.test.ts > LYNX_010: Prueba de Manejo de Errores API > Debe devolver código 404 al solicitar una ruta inexistente
Test de ruta inexistente exitoso

stdout | cliente/src/__tests__/ApiErrorHandling.test.ts > LYNX_010: Prueba de Manejo de Errores API > Debe devolver código 404 al solicitar un producto inexistente
Test de producto inexistente exitoso

stdout | cliente/src/__tests__/ApiErrorHandling.test.ts > LYNX_010: Prueba de Manejo de Errores API > Debe devolver código 401 al acceder a ruta protegida sin token
Test de autenticación requerida exitoso

stdout | cliente/src/__tests__/ApiErrorHandling.test.ts > LYNX_010: Prueba de Manejo de Errores API > Debe devolver código 401 al proporcionar un token inválido
Test de token inválido exitoso

stdout | cliente/src/__tests__/ApiErrorHandling.test.ts > LYNX_010: Prueba de Manejo de Errores API > Debe devolver código 400 al enviar datos inválidos en POST
Test de datos inválidos en POST exitoso

stdout | cliente/src/__tests__/ApiErrorHandling.test.ts > LYNX_010: Prueba de Manejo de Errores API > Debe devolver código 403 al intentar acción sin permisos
Test de permisos insuficientes exitoso

 ✓ cliente/src/__tests__/ApiErrorHandling.test.ts (6 tests) 27ms
   ✓ LYNX_010: Prueba de Manejo de Errores API > Debe devolver código 404 al solicitar una ruta inexistente 
   ✓ LYNX_010: Prueba de Manejo de Errores API > Debe devolver código 404 al solicitar un producto inexistente
   ✓ LYNX_010: Prueba de Manejo de Errores API > Debe devolver código 401 al acceder a ruta protegida sin token
   ✓ LYNX_010: Prueba de Manejo de Errores API > Debe devolver código 401 al proporcionar un token inválido 
   ✓ LYNX_010: Prueba de Manejo de Errores API > Debe devolver código 400 al enviar datos inválidos en POST 
   ✓ LYNX_010: Prueba de Manejo de Errores API > Debe devolver código 403 al intentar acción sin permisos


 Test Files  1 passed (1)
      Tests  6 passed (6)
   Start at  19:14:17
   Duration  907ms (transform 134ms, setup 0ms, collect 126ms, tests 27ms, environment 0ms, prepare 169ms)
```

## Conclusiones

Todas las pruebas han sido exitosas. La API maneja correctamente los errores y devuelve los códigos HTTP apropiados con mensajes claros.

## Recomendaciones

Mantener el sistema de manejo de errores actual y considerar implementar pruebas de integración reales para verificar el comportamiento con el backend. 