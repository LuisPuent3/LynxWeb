import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import axios from "axios";
import api from "../../utils/api";

describe("LYNX_003: Prueba de Conexión API Frontend-Backend (Simple)", () => {
  it("Debe realizar una petición GET a /productos y recibir datos correctamente", async () => {
    try {
      const response = await api.get("/productos");
      expect(response.status).toBe(200);
      expect(Array.isArray(response.data)).toBe(true);
      console.log("Test de conexión exitoso");
    } catch (error) {
      console.error("Error en la prueba de conexión:", error);
      throw error;
    }
  });

  it("Debe manejar errores en la petición API correctamente", async () => {
    try {
      // Intentamos una ruta que no existe, lo que debería generar un error
      await expect(api.get("/ruta-invalida")).rejects.toThrow();
      console.log("Test de manejo de errores exitoso");
    } catch (error) {
      console.error("Error en la prueba de manejo de errores:", error);
      throw error;
    }
  });

  it("Debe procesar la respuesta de la API dentro del tiempo aceptable", async () => {
    const startTime = performance.now();
    try {
      await api.get("/productos");
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      console.log(`Tiempo de respuesta: ${responseTime.toFixed(2)}ms`);
      expect(responseTime).toBeLessThan(500); // Esperamos menos de 500ms
    } catch (error) {
      console.error("Error en la prueba de tiempo de respuesta:", error);
      throw error;
    }
  });

  it("Debe configurar correctamente los encabezados CORS", async () => {
    try {
      const response = await api.get("/productos");
      
      // Verificar que los encabezados CORS estén presentes
      const headers = response.headers;
      expect(headers["access-control-allow-origin"]).toBeDefined();
      console.log("Test de configuración CORS exitoso");
    } catch (error) {
      console.error("Error en la prueba de CORS:", error);
      throw error;
    }
  });
}); 